"""命令行的端到端测试：直接调 main()，比较打印出来的文本。"""

import contextlib
import io
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from todo.cli import main


class CliTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.file = str(Path(self._tmp.name) / "tasks.json")

    def run_cli(self, *argv: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(["--file", self.file, *argv])
        return code, out.getvalue(), err.getvalue()

    def test_add_then_list(self) -> None:
        code, out, _ = self.run_cli("add", "写周报", "-p", "high", "-t", "work")
        self.assertEqual(code, 0)
        self.assertIn("已添加 #1", out)

        code, out, _ = self.run_cli("list")
        self.assertEqual(code, 0)
        self.assertIn("[ ] #1 (high) 写周报  @work", out)

    def test_list_empty_hint(self) -> None:
        _, out, _ = self.run_cli("list")
        self.assertIn("还没有任务", out)

    def test_done_then_list_all(self) -> None:
        self.run_cli("add", "写周报")
        code, out, _ = self.run_cli("done", "1")
        self.assertEqual(code, 0)

        # 默认 list 只列未完成
        _, out, _ = self.run_cli("list")
        self.assertIn("还没有任务", out)

        # --all 才能看到它，而且是打勾的
        _, out, _ = self.run_cli("list", "--all")
        self.assertIn("[x] #1", out)

    def test_rm_missing_id_reports_error(self) -> None:
        code, _, err = self.run_cli("rm", "42")
        self.assertEqual(code, 1)
        self.assertIn("没有编号为 42 的任务", err)


if __name__ == "__main__":
    unittest.main()
