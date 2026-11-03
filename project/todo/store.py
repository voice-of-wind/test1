"""任务的读写：全部任务存在一个 JSON 文件里。

文件格式：

    {
      "next_id": 3,
      "tasks": [ { ... }, { ... } ]
    }

每次改动立刻落盘，所以「跑一条命令 → 看一眼 git status」就能看到变化，
这是练习 git diff / git status 的好素材。
"""

from __future__ import annotations

import json
from pathlib import Path

from .models import Task, now_text

#: 默认数据文件：项目根目录下的 data/tasks.json
DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "tasks.json"


class TaskStore:
    """一个 JSON 文件 = 一个任务库。"""

    def __init__(self, path: str | Path = DEFAULT_PATH) -> None:
        self.path = Path(path)
        self._tasks: list[Task] = []
        self._next_id = 1
        self.load()

    # ---------------- 读写 ----------------
    def load(self) -> None:
        """从磁盘读；文件不存在就从空库开始（第一次运行就是这种情况）。"""
        if not self.path.exists():
            self._tasks, self._next_id = [], 1
            return
        raw_text = self.path.read_text(encoding="utf-8").strip()
        raw = json.loads(raw_text) if raw_text else {}
        self._tasks = [Task.from_dict(item) for item in raw.get("tasks", [])]
        self._next_id = raw.get("next_id") or self._guess_next_id()

    def save(self) -> None:
        """写回磁盘，顺手建好父目录。"""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "next_id": self._next_id,
            "tasks": [task.to_dict() for task in self._tasks],
        }
        self.path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def _guess_next_id(self) -> int:
        return max((task.id for task in self._tasks), default=0) + 1

    # ---------------- 增删改查 ----------------
    def add(self, title: str, priority: str = "normal", tags: list[str] | None = None) -> Task:
        """新增一条任务，返回它（带上了分配好的 id）。"""
        task = Task(
            id=self._next_id,
            title=title,
            priority=priority,
            tags=list(tags or []),
        )
        self._next_id += 1
        self._tasks.append(task)
        self.save()
        return task

    def get(self, task_id: int) -> Task:
        """按 id 取任务；取不到抛 KeyError（CLI 会接住并打印错误）。"""
        for task in self._tasks:
            if task.id == task_id:
                return task
        raise KeyError(f"没有编号为 {task_id} 的任务")

    def done(self, task_id: int) -> Task:
        """标记完成，并记下完成时间。"""
        task = self.get(task_id)
        task.done = True
        task.done_at = now_text()
        self.save()
        return task

    def remove(self, task_id: int) -> Task:
        """删除任务（真删，不是标记）。"""
        task = self.get(task_id)
        self._tasks.remove(task)
        self.save()
        return task

    def all(self) -> list[Task]:
        return list(self._tasks)

    def pending(self) -> list[Task]:
        """未完成的任务。"""
        return [task for task in self._tasks if not task.done]

    def completed(self) -> list[Task]:
        """已完成的任务。"""
        return [task for task in self._tasks if task.done]
