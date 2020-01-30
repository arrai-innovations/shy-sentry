# Copyright (C) 2020 Arrai Innovations Inc. - All Rights Reserved
import os
import subprocess
from time import sleep
from unittest import TestCase
from shy_sentry import shy_sentry

import psutil
from pretenders.client.http import HTTPMock

NOGUARD_EXPECTED_TRACEBACK = """Traceback (most recent call last):
  File "./tests/test_scripts/noguard.py", line 17, in <module>
    main()
  File "./tests/test_scripts/noguard.py", line 12, in main
    print(1 / 0)
ZeroDivisionError: division by zero
"""

GUARD_DECORATOR_NO_INIT_EXPECTED_TRACEBACK = f"""Traceback (most recent call last):
  File "./tests/test_scripts/guard_decorator_no_init.py", line 17, in <module>
    main()
  File "{shy_sentry.__file__}", line 69, in guarding
    return guarded(*args, **kwargs)
  File "./tests/test_scripts/guard_decorator_no_init.py", line 13, in main
    print(1 / 0)
ZeroDivisionError: division by zero
"""

GUARD_CONTEXT_MANAGER_NO_INIT_EXPECTED_TRACEBACK = """Traceback (most recent call last):
  File "./tests/test_scripts/guard_context_manager_no_init.py", line 17, in <module>
    main()
  File "./tests/test_scripts/guard_context_manager_no_init.py", line 12, in main
    print(1 / 0)
ZeroDivisionError: division by zero
"""


class MockSentryTestCase(TestCase):
    maxDiff = None

    project_id = "123456"
    pretender_boss = None

    @classmethod
    def setUpClass(cls: TestCase) -> None:
        super().setUpClass()
        cls.pretender_boss = subprocess.Popen(
            ["python", "-m", "pretenders.server.server", "--host", "127.0.0.1", "--port", "8888"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        sleep(0.5)
        cls.mock_sentry = HTTPMock("127.0.0.1", 8888, name="mock_sentry")

    def setUp(self) -> None:
        super().setUp()
        self.mock_sentry.reset()
        self.mock_sentry.when(f"POST /api/{self.project_id}/store/").reply(
            '{"id": "fc6d8c0c43fc4630ad850ee518f1b9d0"}',
            headers={"Content-Type": "application/json"},
            status=200,
            after=2.5,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        me = psutil.Process(os.getpid())
        for child in me.children(recursive=True):
            child.kill()
        cls.pretender_boss.wait()
        super().tearDownClass()

    @classmethod
    def run_script(cls, cmd, check=True):
        kwargs = {
            "shell": True,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "check": False,
            "encoding": "utf8",
            "timeout": 15,
        }
        cmd = "python " + cmd
        ran = subprocess.run(cmd, **kwargs)
        if check:
            ran.check_returncode()
        return ran

    def do_test(self, script, expected_traceback=None, expect_sentry_request=True):
        ran = self.run_script(script, check=not expected_traceback)
        self.assertEqual(ran.stdout, "expected output\n")
        if expected_traceback:
            self.assertEqual(ran.stderr, expected_traceback)
        if expect_sentry_request:
            request = self.mock_sentry.get_request(0)
            self.assertEqual(request.method, "POST")
            self.assertEqual(request.url, f"/api/{self.project_id}/store/")
            request = self.mock_sentry.get_request(1)
            self.assertIsNone(request)
        else:
            request = self.mock_sentry.get_request(0)
            self.assertIsNone(request)

    def test_guard_decorator(self):
        self.do_test("./tests/test_scripts/guard_decorator.py")

    def test_guard_context_manager(self):
        self.do_test("./tests/test_scripts/guard_context_manager.py")

    def test_no_guard(self):
        self.do_test("./tests/test_scripts/noguard.py", NOGUARD_EXPECTED_TRACEBACK)

    def test_guard_decorator_no_error(self):
        self.do_test("./tests/test_scripts/guard_decorator_no_error.py", expect_sentry_request=False)

    def test_guard_context_manager_no_error(self):
        self.do_test("./tests/test_scripts/guard_context_manager_no_error.py", expect_sentry_request=False)

    def test_guard_decorator_no_init(self):
        self.do_test(
            "./tests/test_scripts/guard_decorator_no_init.py",
            expected_traceback=GUARD_DECORATOR_NO_INIT_EXPECTED_TRACEBACK,
            expect_sentry_request=False,
        )

    def test_guard_context_manager_no_init(self):
        self.do_test(
            "./tests/test_scripts/guard_context_manager_no_init.py",
            expected_traceback=GUARD_CONTEXT_MANAGER_NO_INIT_EXPECTED_TRACEBACK,
            expect_sentry_request=False,
        )

    def test_cwd_config(self):
        with open("./tests/test_scripts/sentry_config.json", "r") as src:
            with open("./sentry_config.json", "w") as dest:
                dest.write(src.read())
        try:
            self.do_test("./tests/test_scripts/cwd_config.py")
        finally:
            os.unlink("./sentry_config.json")
