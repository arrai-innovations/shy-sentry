# Copyright (C) 2020 Arrai Innovations Inc. - All Rights Reserved
import os
import subprocess
from time import sleep
from unittest import TestCase

import psutil
from pretenders.client.http import HTTPMock


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
        sleep(1)
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

    def do_test(self, script, expect_traceback=False, expect_request=True):
        ran = self.run_script(script, check=not expect_traceback)
        self.assertEqual(ran.stdout, "expected output\n")
        if expect_traceback:
            stderr = ran.stderr.strip("\n").split("\n")
            self.assertEqual(stderr[-1] if stderr else None, "ZeroDivisionError: division by zero")
        if expect_request:
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
        self.do_test("./tests/test_scripts/noguard.py", expect_traceback=True)

    def test_guard_decorator_no_error(self):
        self.do_test("./tests/test_scripts/guard_decorator_no_error.py", expect_request=False)

    def test_guard_context_manager_no_error(self):
        self.do_test("./tests/test_scripts/guard_context_manager_no_error.py", expect_request=False)

    def test_guard_decorator_no_init(self):
        self.do_test(
            "./tests/test_scripts/guard_decorator_no_init.py", expect_traceback=True, expect_request=False,
        )

    def test_guard_context_manager_no_init(self):
        self.do_test(
            "./tests/test_scripts/guard_context_manager_no_init.py", expect_traceback=True, expect_request=False,
        )

    def test_cwd_config(self):
        with open("./tests/test_scripts/sentry_config.json", "r") as src:
            with open("./sentry_config.json", "w") as dest:
                dest.write(src.read())
        try:
            self.do_test("./tests/test_scripts/cwd_config.py")
        finally:
            os.unlink("./sentry_config.json")
