"""命令行入口。

用法：

    python -m todo.cli add "写周报" -p high -t work
    python -m todo.cli list
    python -m todo.cli list --all
    python -m todo.cli done 1
    python -m todo.cli rm 1

（在 Windows PowerShell 里，如果标题里带空格记得加引号。）
"""

from __future__ import annotations

import argparse
import sys

from .models import PRIORITIES
from .store import DEFAULT_PATH, TaskStore

VERSION = "0.1.0"


def build_parser() -> argparse.ArgumentParser:
    """搭出整套子命令。想加新命令，基本就在这里加一段。"""
    parser = argparse.ArgumentParser(
        prog="todo",
        description="练习 Git 用的小型任务清单",
    )
    parser.add_argument("--version", action="version", version=f"todo {VERSION}")
    parser.add_argument("--file", help="指定数据文件（默认 data/tasks.json）")

    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="新增任务")
    p_add.add_argument("title", help="任务标题")
    p_add.add_argument("-p", "--priority", choices=PRIORITIES, default="normal", help="优先级")
    p_add.add_argument("-t", "--tag", action="append", default=[], help="标签，可重复写")

    p_list = sub.add_parser("list", help="列出未完成任务")
    p_list.add_argument("-a", "--all", action="store_true", help="连已完成的一起列")

    p_done = sub.add_parser("done", help="把任务标记为完成")
    p_done.add_argument("id", type=int, help="任务编号")

    p_rm = sub.add_parser("rm", help="删除任务")
    p_rm.add_argument("id", type=int, help="任务编号")

    return parser


# ---------------------------------------------------------------- 各命令实现
def cmd_add(store: TaskStore, args: argparse.Namespace) -> int:
    task = store.add(args.title, priority=args.priority, tags=args.tag)
    print(f"已添加 #{task.id}：{task.title}")
    return 0


def cmd_list(store: TaskStore, args: argparse.Namespace) -> int:
    tasks = store.all() if args.all else store.pending()
    if not tasks:
        print("（这里还没有任务）")
        return 0
    for task in tasks:
        print(task.format())
    print(f"\n共 {len(tasks)} 条")
    return 0


def cmd_done(store: TaskStore, args: argparse.Namespace) -> int:
    task = store.done(args.id)
    print(f"已完成 #{task.id}：{task.title}")
    return 0


def cmd_rm(store: TaskStore, args: argparse.Namespace) -> int:
    task = store.remove(args.id)
    print(f"已删除 #{task.id}：{task.title}")
    return 0


#: 命令名 → 处理函数。加新命令时这里也要加一行。
COMMANDS = {
    "add": cmd_add,
    "list": cmd_list,
    "done": cmd_done,
    "rm": cmd_rm,
}


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    store = TaskStore(args.file or DEFAULT_PATH)
    try:
        return COMMANDS[args.command](store, args)
    except KeyError as exc:
        print(f"错误：{exc.args[0]}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
