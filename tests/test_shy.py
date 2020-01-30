# Copyright (C) 2020 Arrai Innovations Inc. - All Rights Reserved
import os
import subprocess
from time import sleep
from unittest import TestCase

import psutil
from pretenders.client.http import HTTPMock

NOGUARD_EXPECTED_TRACEBACK = """Traceback (most recent call last):
  File "./tests/test_scripts/noguard.py", line 17, in <module>
    main()
  File "./tests/test_scripts/noguard.py", line 12, in main
    print(1 / 0)
ZeroDivisionError: division by zero
"""

GUARD_DECORATOR_NO_INIT_EXPECTED_TRACEBACK = """Traceback (most recent call last):
  File "./tests/test_scripts/guard_decorator_no_init.py", line 17, in <module>
    main()
  File "/home/joel/PycharmProjects/shy-sentry/shy_sentry/shy_sentry.py", line 69, in guarding
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
            ["python", "-m", "pretenders.server.server", "--host", "localhost", "--port", "8888"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        sleep(0.5)
        cls.mock_sentry = HTTPMock("localhost", 8888, name="mock_sentry")

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
    def subcmd_with_coverage(cls, cmd, check=True):
        kwargs = {
            "shell": True,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "check": False,
            "encoding": "utf8",
            "timeout": 15,
        }
        cmd = "coverage run -p " + cmd
        ran = subprocess.run(cmd, **kwargs)
        if check:
            ran.check_returncode()
        return ran

    def test_guard_decorator(self):
        ran = self.subcmd_with_coverage("./tests/test_scripts/guard_decorator.py")
        self.assertEqual(ran.stdout, "expected output\n")
        request = self.mock_sentry.get_request(0)
        self.assertEqual(request.method, "POST")
        self.assertEqual(request.url, f"/api/{self.project_id}/store/")
        request = self.mock_sentry.get_request(1)
        self.assertIsNone(request)

    def test_guard_context_manager(self):
        ran = self.subcmd_with_coverage("./tests/test_scripts/guard_context_manager.py")
        self.assertEqual(ran.stdout, "expected output\n")
        request = self.mock_sentry.get_request(0)
        self.assertEqual(request.method, "POST")
        self.assertEqual(request.url, f"/api/{self.project_id}/store/")
        request = self.mock_sentry.get_request(1)
        self.assertIsNone(request)

    def test_no_guard(self):
        ran = self.subcmd_with_coverage("./tests/test_scripts/noguard.py", check=False)
        self.assertEqual(ran.stdout, "expected output\n")
        self.assertEqual(ran.stderr, NOGUARD_EXPECTED_TRACEBACK)
        request = self.mock_sentry.get_request(0)
        self.assertEqual(request.method, "POST")
        self.assertEqual(request.url, f"/api/{self.project_id}/store/")
        request = self.mock_sentry.get_request(1)
        self.assertIsNone(request)

    def test_guard_decorator_no_error(self):
        ran = self.subcmd_with_coverage("./tests/test_scripts/guard_decorator_no_error.py")
        self.assertEqual(ran.stdout, "expected output\n")
        request = self.mock_sentry.get_request(0)
        self.assertIsNone(request)

    def test_guard_context_manager_no_error(self):
        ran = self.subcmd_with_coverage("./tests/test_scripts/guard_context_manager_no_error.py")
        self.assertEqual(ran.stdout, "expected output\n")
        request = self.mock_sentry.get_request(0)
        self.assertIsNone(request)

    def test_guard_decorator_no_init(self):
        ran = self.subcmd_with_coverage("./tests/test_scripts/guard_decorator_no_init.py", check=False)
        self.assertEqual(ran.stdout, "expected output\n")
        self.assertEqual(ran.stderr, GUARD_DECORATOR_NO_INIT_EXPECTED_TRACEBACK)
        request = self.mock_sentry.get_request(0)
        self.assertIsNone(request)

    def test_guard_context_manager_no_init(self):
        ran = self.subcmd_with_coverage("./tests/test_scripts/guard_context_manager_no_init.py", check=False)
        self.assertEqual(ran.stdout, "expected output\n")
        self.assertEqual(ran.stderr, GUARD_CONTEXT_MANAGER_NO_INIT_EXPECTED_TRACEBACK)
        request = self.mock_sentry.get_request(0)
        self.assertIsNone(request)

    def test_cwd_config(self):
        with open("./tests/test_scripts/sentry_config.json", "r") as src:
            with open("./sentry_config.json", "w") as dest:
                dest.write(src.read())
        try:
            ran = self.subcmd_with_coverage("./tests/test_scripts/cwd_config.py")
            self.assertEqual(ran.stdout, "expected output\n")
            request = self.mock_sentry.get_request(0)
            self.assertEqual(request.method, "POST")
            self.assertEqual(request.url, f"/api/{self.project_id}/store/")
            request = self.mock_sentry.get_request(1)
            self.assertIsNone(request)
        finally:
            os.unlink("./sentry_config.json")
