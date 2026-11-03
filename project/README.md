# todo —— 练习 Git 用的小任务清单

一个只有几百行 Python 的小项目：JSON 存任务、argparse 做命令行、unittest 写测试。
它存在的唯一目的是给你当**操作对象**：分支、合并、冲突、远程、回滚，全在它身上练。

## 环境

只需要 Python 3.10+（因为用了 `str | None` 这种类型写法）。没有第三方依赖，不用 `pip install`。

```powershell
python --version          # 应该是 3.10 或更高
```

## 跑起来

在 `project/` 目录下：

```powershell
python -m todo.cli add "写周报" -p high -t work
python -m todo.cli add "买牛奶" -t life
python -m todo.cli list
```

输出大致是：

```text
[ ] #1 (high) 写周报  @work
[ ] #2 (normal) 买牛奶  @life

共 2 条
```

`list` 默认只显示未完成的，加 `--all` 连已完成的也看：

```powershell
python -m todo.cli list --all
```

标记完成、删除：

```powershell
python -m todo.cli done 1
python -m todo.cli rm 2
```

数据存在 `data/tasks.json`（相对项目根目录，不是相对当前目录）。
想换文件可以用 `--file`：

```powershell
python -m todo.cli --file D:\tmp\demo.json list
```

## 命令一览

| 命令 | 作用 |
| --- | --- |
| `add` | 新增任务 |
| `list` | 列出任务 |
| `done` | 标记完成 |
| `rm` | 删除任务 |

## 跑测试

```powershell
python -m unittest discover -s tests -v
```

应该看到 12 个测试全过。**这条命令是你练习合并时的裁判**：

> 冲突解完 → 测试必须还全绿。测试红了，说明「冲突解决得语法正确、语义错误」。

## 目录结构

```text
project/
├── todo/
│   ├── __init__.py
│   ├── models.py      # Task 数据模型
│   ├── store.py       # JSON 读写 + 增删改查
│   └── cli.py         # 命令行入口
├── tests/
│   ├── test_store.py  # 数据层测试
│   └── test_cli.py    # 命令行测试
├── docs/
│   └── 开发约定.md     # 提交信息规范、分支命名（练 amend 用）
├── .gitignore
├── .gitattributes
└── README.md
```

## 已知的"以后可以加"

这些是故意留白的功能，正好用来当分支任务：

- 按关键词搜索任务
- 统计（总数 / 各优先级数量 / 完成率）
- 任务排序（按优先级）
- 数据导出成 Markdown

> 注意：这个仓库**一开始没有 `.git`**。第一步是 `git init` —— 见 `labs/lab01-初始化与首次提交.md`。
