"""数据模型：一条任务长什么样。

故意写得朴素——它的作用是当你的 Git 练习对象，不是健壮的生产代码。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

#: 允许的优先级，从低到高
PRIORITIES = ("low", "normal", "high")


def now_text() -> str:
    """当前时间的固定格式文本，方便排序，也方便 diff。"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class Task:
    """一条任务。字段就是 tasks.json 里存的东西。"""

    id: int
    title: str
    done: bool = False
    priority: str = "normal"
    tags: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=now_text)
    done_at: str | None = None

    def to_dict(self) -> dict:
        """转成可以 json.dumps 的普通字典。"""
        return {
            "id": self.id,
            "title": self.title,
            "done": self.done,
            "priority": self.priority,
            "tags": list(self.tags),
            "created_at": self.created_at,
            "done_at": self.done_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """从字典还原。

        老版本的数据可能没有 priority / tags，用 get 兜住，
        这样「旧文件 + 新代码」不会直接崩——升级数据格式时这一点很重要。
        """
        return cls(
            id=data["id"],
            title=data["title"],
            done=data.get("done", False),
            priority=data.get("priority", "normal"),
            tags=list(data.get("tags", [])),
            created_at=data.get("created_at") or now_text(),
            done_at=data.get("done_at"),
        )

    def format(self) -> str:
        """终端里的一行展示。"""
        box = "x" if self.done else " "
        line = f"[{box}] #{self.id} ({self.priority}) {self.title}"
        if self.tags:
            line += "  " + " ".join(f"@{tag}" for tag in self.tags)
        if self.done_at:
            line += f"  (完成于 {self.done_at})"
        return line
