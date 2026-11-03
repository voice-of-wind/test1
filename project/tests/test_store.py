"""TaskStore 的单元测试：只碰数据层，不碰命令行。"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from todo.store import TaskStore


class TaskStoreTest(unittest.TestCase):
    def setUp(self) -> None:
        # 每个测试用一个临时目录，绝不污染项目里的 data/
        self._tmp = TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.path = Path(self._tmp.name) / "tasks.json"
        self.store = TaskStore(self.path)

    def test_new_store_is_empty(self) -> None:
        self.assertEqual(self.store.all(), [])
        self.assertFalse(self.path.exists(), "只是读，不应该创建文件")

    def test_add_assigns_incrementing_ids(self) -> None:
        first = self.store.add("写周报")
        second = self.store.add("修 bug")
        self.assertEqual((first.id, second.id), (1, 2))

    def test_add_keeps_priority_and_tags(self) -> None:
        task = self.store.add("写周报", priority="high", tags=["work", "weekly"])
        self.assertEqual(task.priority, "high")
        self.assertEqual(task.tags, ["work", "weekly"])

    def test_save_then_reload_roundtrip(self) -> None:
        self.store.add("写周报", priority="high", tags=["work"])
        reloaded = TaskStore(self.path)
        self.assertEqual([t.title for t in reloaded.all()], ["写周报"])
        self.assertEqual(reloaded.all()[0].tags, ["work"])
        # id 计数器也要活着，否则重开一次就会撞号
        self.assertEqual(reloaded.add("新任务").id, 2)

    def test_done_marks_and_stamps_time(self) -> None:
        task = self.store.add("写周报")
        self.assertFalse(task.done)
        self.store.done(task.id)
        again = TaskStore(self.path).get(task.id)
        self.assertTrue(again.done)
        self.assertIsNotNone(again.done_at)

    def test_remove(self) -> None:
        task = self.store.add("临时任务")
        self.store.remove(task.id)
        self.assertEqual(self.store.all(), [])
        with self.assertRaises(KeyError):
            self.store.get(task.id)

    def test_pending_and_completed_split(self) -> None:
        done_task = self.store.add("已完成的事")
        self.store.add("还没做的事")
        self.store.done(done_task.id)
        self.assertEqual([t.title for t in self.store.pending()], ["还没做的事"])
        self.assertEqual([t.title for t in self.store.completed()], ["已完成的事"])

    def test_get_missing_raises_keyerror(self) -> None:
        with self.assertRaises(KeyError):
            self.store.get(999)


if __name__ == "__main__":
    unittest.main()
