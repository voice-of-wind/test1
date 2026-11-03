# lab04 · 合并与冲突（核心实验）

**目标**：造出一次真实的 **4 个文件**冲突，把它解决干净，并且让测试重新变绿。

**对应阅读**：`docs/04-合并与冲突.md`（**先读，再动手**）
**预计**：60–90 分钟

**这个 lab 你会经历：**

1. 两条分支各自加一个新功能（真代码，不是玩具）
2. 第一次合并：顺利，产生一个合并提交
3. 第二次合并：**4 个文件冲突**
4. 演练 `git merge --abort`（学会安全退出）
5. 逐个解决冲突，跑测试验收

---

## 0. 准备

```powershell
cd D:\AI\deepseekHarness\DS_project\gitlearn\project
git status
```

必须是干净的。然后：

```powershell
python -m unittest discover -s tests -q
```

```text
Ran 12 tests in 0.0xxs

OK
```

**记住 12。** 加完两个功能后应该变成 **14**，这是你的验收标准。

```powershell
git lg
```

记下现在 `main` 的位置。

---

## 1. 分支 A：搜索功能

```powershell
git switch -c feature/search
```

要改 4 个文件。**一行一行敲，不要复制整段**——手打能让你注意到每一处插入的位置。

### 1.1 `todo/store.py`：在文件**最末尾**追加一个方法

`store.py` 现在以 `completed()` 结尾：

```python
    def completed(self) -> list[Task]:
        """已完成的任务。"""
        return [task for task in self._tasks if task.done]
```

在它**后面**追加（注意缩进是 4 个空格，和上面的方法对齐，前面空一行）：

```python

    def search(self, keyword: str) -> list[Task]:
        """标题或标签里包含关键词的任务（忽略大小写）。"""
        key = keyword.lower()
        return [
            task
            for task in self._tasks
            if key in task.title.lower() or any(key in tag.lower() for tag in task.tags)
        ]
```

### 1.2 `todo/cli.py`：三处插入

**第一处**：找到这一行（在 `build_parser` 里）：

```python
    p_done = sub.add_parser("done", help="把任务标记为完成")
```

在它**上面**插入两行：

```python
    p_search = sub.add_parser("search", help="按关键词搜索任务")
    p_search.add_argument("keyword", help="要搜的词")

```

**第二处**：找到 `def cmd_done(`，在它**上面**插入整个函数：

```python
def cmd_search(store: TaskStore, args: argparse.Namespace) -> int:
    tasks = store.search(args.keyword)
    if not tasks:
        print(f"（没有匹配「{args.keyword}」的任务）")
        return 0
    for task in tasks:
        print(task.format())
    print(f"\n共 {len(tasks)} 条")
    return 0


```

**第三处**：找到 `COMMANDS` 字典：

```python
COMMANDS = {
    "add": cmd_add,
    "list": cmd_list,
    "done": cmd_done,
    "rm": cmd_rm,
}
```

在 `"rm": cmd_rm,` **后面**加一行：

```python
    "search": cmd_search,
```

### 1.3 `README.md`：命令表加一行

找到：

```markdown
| `rm` | 删除任务 |
```

在它**下面**加一行：

```markdown
| `search` | 按关键词搜索 |
```

### 1.4 `tests/test_store.py`：加一个测试

找到文件末尾：

```python
if __name__ == "__main__":
    unittest.main()
```

在它**上面**（也就是类里面，缩进 4 空格）插入：

```python
    def test_search_finds_title_and_tags(self) -> None:
        self.store.add("写周报", tags=["work"])
        self.store.add("买牛奶", tags=["life"])
        self.assertEqual([t.title for t in self.store.search("周报")], ["写周报"])
        self.assertEqual([t.title for t in self.store.search("LIFE")], ["买牛奶"])
        self.assertEqual(self.store.search("没有的东西"), [])
```

### 1.5 验证 + 提交

```powershell
python -m unittest discover -s tests -q
```

**13 个测试全过**（12 + 1 个新的）。

```powershell
python -m todo.cli search 周报
```

```text
[ ] #1 (high) 写周报  @work

共 1 条
```

```powershell
git status --short
git add -A
git commit -m "feat(store): 支持按关键词搜索任务"
```

```text
[feature/search 042f020] feat(store): 支持按关键词搜索任务
 4 files changed, 29 insertions(+)
```

**改 4 个文件、29 行。记住这个数字，等下对比。**

---

## 2. 分支 B：统计功能

```powershell
git switch main
```

> **关键动作**：切回 main 再开新分支。如果从 `feature/search` 上开，B 就包含了 A 的改动，那就不叫"并行开发"了。

```powershell
git switch -c feature/stats
```

### 2.1 `todo/store.py`：先改 import

顶部的这一行：

```python
from .models import Task, now_text
```

改成：

```python
from .models import PRIORITIES, Task, now_text
```

> 注意：`PRIORITIES` 本来只被 `cli.py` 用，现在 store 也要用了。

### 2.2 `todo/store.py`：在最末尾追加方法

```python

    def stats(self) -> dict:
        """简单统计：总数、完成数、完成率、各优先级数量。"""
        total = len(self._tasks)
        done = len(self.completed())
        by_priority = {name: 0 for name in PRIORITIES}
        for task in self._tasks:
            by_priority[task.priority] = by_priority.get(task.priority, 0) + 1
        return {
            "total": total,
            "done": done,
            "pending": total - done,
            "done_rate": (done / total) if total else 0.0,
            "by_priority": by_priority,
        }
```

### 2.3 `todo/cli.py`：四件事

**① 加 `import json`**（`cmd_stats` 要用）。找到：

```python
import argparse
import sys
```

改成：

```python
import argparse
import json
import sys
```

**② 加子命令**，位置和 A 一样——在 `p_done = sub.add_parser(...)` **上面**：

```python
    p_stats = sub.add_parser("stats", help="看统计")
    p_stats.add_argument("--json", action="store_true", help="用 JSON 输出")

```

**③ 加处理函数**，位置也在 `def cmd_done(` **上面**：

```python
def cmd_stats(store: TaskStore, args: argparse.Namespace) -> int:
    data = store.stats()
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    print(f"总数 {data['total']}  已完成 {data['done']}  未完成 {data['pending']}")
    print(f"完成率 {data['done_rate']:.0%}")
    for name, count in data["by_priority"].items():
        print(f"  {name:<7}{count}")
    return 0


```

**④ `COMMANDS` 字典**，在 `"rm": cmd_rm,` 后面加：

```python
    "stats": cmd_stats,
```

### 2.4 `README.md`：命令表加一行

在 `| \`rm\` | 删除任务 |` 下面加：

```markdown
| `stats` | 看统计 |
```

### 2.5 `tests/test_store.py`：加测试

同样插在 `if __name__ == "__main__":` **上面**：

```python
    def test_stats_counts_and_rate(self) -> None:
        first = self.store.add("写周报", priority="high")
        self.store.add("买牛奶")
        self.store.done(first.id)
        data = self.store.stats()
        self.assertEqual((data["total"], data["done"], data["pending"]), (2, 1, 1))
        self.assertAlmostEqual(data["done_rate"], 0.5)
        self.assertEqual(data["by_priority"]["high"], 1)
        self.assertEqual(data["by_priority"]["normal"], 1)
```

### 2.6 验证 + 提交

```powershell
python -m unittest discover -s tests -q
```

**13 个测试全过**（这条分支上是 12 + 它自己的 1 个）。

```powershell
python -m todo.cli stats
```

```text
总数 2  已完成 0  未完成 2
完成率 0%
  low    0
  normal 1
  high   1
```

```powershell
git add -A
git commit -m "feat(store): 增加任务统计"
```

### 2.7 现在历史长什么样

```powershell
git lg
```

```text
* a6b6625 (HEAD -> feature/stats) feat(store): 增加任务统计
| * 042f020 (feature/search) feat(store): 支持按关键词搜索任务
|/
* 8b2f0d1 (main) docs: 补充贡献说明
* ...
```

**两条分支从 `main` 分叉，各自往前一格。** 这就是典型的并行开发。

---

## 3. 第一次合并：搜索功能

```powershell
git switch main
git merge --no-ff feature/search -m "merge: 合并搜索功能"
```

```text
Merge made by the 'ort' strategy.
 README.md           |  1 +
 tests/test_store.py |  6 ++++++
 todo/cli.py         | 13 +++++++++++++
 todo/store.py       |  9 +++++++++
 4 files changed, 29 insertions(+)
```

`--no-ff` 强制产生一个合并提交（即使能快进）。看：

```powershell
git lg
```

```text
*   2b27f7b (HEAD -> main) merge: 合并搜索功能
|\
| * 042f020 (feature/search) feat(store): 支持按关键词搜索任务
|/
* 8b2f0d1 (main) docs: 补充贡献说明
```

那个 `|\` 和 `|/` 就是合并的形状。`main` 现在包含了搜索功能。

```powershell
python -m unittest discover -s tests -q       # 13 个
python -m todo.cli search 周报                  # 能用
```

---

## 4. 第二次合并：冲突来了

```powershell
git merge feature/stats
```

```text
Auto-merging README.md
CONFLICT (content): Merge conflict in README.md
Auto-merging tests/test_store.py
CONFLICT (content): Merge conflict in tests/test_store.py
Auto-merging todo/cli.py
CONFLICT (content): Merge conflict in todo/cli.py
Auto-merging todo/store.py
CONFLICT (content): Merge conflict in todo/store.py
Automatic merge failed; fix conflicts and then commit the result.
```

**四个文件全冲突。** 别慌，原因很简单：两条分支都在**同一个位置**加了东西——文件末尾、同一行后面、同一个函数前面。

```powershell
git status
```

```text
On branch main
You have unmerged paths.
  (fix conflicts and run "git commit")
  (use "git merge --abort" to abort the merge)

Unmerged paths:
  (use "git add <file>..." to mark resolution)
        both modified:   README.md
        both modified:   tests/test_store.py
        both modified:   todo/cli.py
        both modified:   todo/store.py

no changes added to commit (use "git add" and/or "git commit -a")
```

`You have unmerged paths` + `both modified` = **合并没有完成**，现在处于"合并中"状态。

先看一处冲突长什么样：

```powershell
Select-String -Path todo\store.py -Pattern '<<<<<<<' -Context 0,12
```

你会看到：

```python
<<<<<<< HEAD
    def search(self, keyword: str) -> list[Task]:
        """标题或标签里包含关键词的任务（忽略大小写）。"""
        key = keyword.lower()
        return [
            task
            for task in self._tasks
            if key in task.title.lower() or any(key in tag.lower() for tag in task.tags)
        ]
=======
    def stats(self) -> dict:
        """简单统计：总数、完成数、完成率、各优先级数量。"""
        ...
>>>>>>> feature/stats
```

**解读：**

- `<<<<<<< HEAD` 到 `=======` 之间 = **你现在所在的分支**（main，已经有 search 了）
- `=======` 到 `>>>>>>> feature/stats` = **被合进来的分支**（stats）
- 两边都在这一个位置加了方法，Git 不知道你要哪个，也不知道要不要都留

---

## 5. 先演练一次"逃跑"

在真正解决之前，先试试后悔药——这是最该养成的肌肉记忆。

```powershell
git merge --abort
```

```powershell
git status
```

```text
On branch main
nothing to commit, working tree clean
```

**回到了合并前，一个冲突标记都没有了，代码完好。**

```powershell
python -m unittest discover -s tests -q      # 还是 13 个，全过
```

现在重新来：

```powershell
git merge feature/stats
```

（会再冲突一次，这是正常的，冲突是确定性的。）

> **记住这个动作**：解到一半发现搞错了、或者想换个思路，`git merge --abort` 永远能回到干净的起点。比硬着头皮解完强。

---

## 6. 解决冲突

规则只有一条：**处理 `<<<<<<<` 到 `>>>>>>>` 之间的部分，然后把三行标记删掉。标记之外的代码一个字都别动。**

这次的原则很明确：**两边的功能都要，都保留。**

### 6.1 `todo/store.py`

打开文件，滚到末尾。把整段冲突（从 `<<<<<<<` 到 `>>>>>>>`）替换成：

```python
    def search(self, keyword: str) -> list[Task]:
        """标题或标签里包含关键词的任务（忽略大小写）。"""
        key = keyword.lower()
        return [
            task
            for task in self._tasks
            if key in task.title.lower() or any(key in tag.lower() for tag in task.tags)
        ]

    def stats(self) -> dict:
        """简单统计：总数、完成数、完成率、各优先级数量。"""
        total = len(self._tasks)
        done = len(self.completed())
        by_priority = {name: 0 for name in PRIORITIES}
        for task in self._tasks:
            by_priority[task.priority] = by_priority.get(task.priority, 0) + 1
        return {
            "total": total,
            "done": done,
            "pending": total - done,
            "done_rate": (done / total) if total else 0.0,
            "by_priority": by_priority,
        }
```

也就是：**两个方法都要，`search` 在前，`stats` 在后，中间空一行。**

> 顺带检查文件顶部：`from .models import PRIORITIES, Task, now_text` 应该已经在（stats 分支改的 import 不在冲突区域，Git 自动合好了）。这正是"有的改动会自动合，有的不会"。

### 6.2 `todo/cli.py`（三处）

**冲突 1 —— 子命令注册**，替换成：

```python
    p_search = sub.add_parser("search", help="按关键词搜索任务")
    p_search.add_argument("keyword", help="要搜的词")

    p_stats = sub.add_parser("stats", help="看统计")
    p_stats.add_argument("--json", action="store_true", help="用 JSON 输出")

    p_done = sub.add_parser("done", help="把任务标记为完成")
```

（两个都要，`p_done` 这行是标记之外的内容，别动它。）

**冲突 2 —— 处理函数**，替换成：

```python
def cmd_search(store: TaskStore, args: argparse.Namespace) -> int:
    tasks = store.search(args.keyword)
    if not tasks:
        print(f"（没有匹配「{args.keyword}」的任务）")
        return 0
    for task in tasks:
        print(task.format())
    print(f"\n共 {len(tasks)} 条")
    return 0


def cmd_stats(store: TaskStore, args: argparse.Namespace) -> int:
    data = store.stats()
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    print(f"总数 {data['total']}  已完成 {data['done']}  未完成 {data['pending']}")
    print(f"完成率 {data['done_rate']:.0%}")
    for name, count in data["by_priority"].items():
        print(f"  {name:<7}{count}")
    return 0


```

**冲突 3 —— COMMANDS 字典**，替换成：

```python
COMMANDS = {
    "add": cmd_add,
    "list": cmd_list,
    "done": cmd_done,
    "rm": cmd_rm,
    "search": cmd_search,
    "stats": cmd_stats,
}
```

（如果字典里的冲突只是两行 `"search": ...` / `"stats": ...`，那就在保留 `"rm": cmd_rm,` 的前提下把两行都留下。）

> 别忘了顶部的 `import json` —— 它是 stats 分支加的，不在冲突区，应该已经自动合好了。**解决完打开文件扫一眼确认。**

### 6.3 `README.md`

命令表里两个行都要，顺序无所谓：

```markdown
| `rm` | 删除任务 |
| `stats` | 看统计 |
| `search` | 按关键词搜索 |
```

### 6.4 `tests/test_store.py`

两个测试方法都要，放在类里面（`if __name__ == "__main__":` 之前）：

```python
    def test_search_finds_title_and_tags(self) -> None:
        self.store.add("写周报", tags=["work"])
        self.store.add("买牛奶", tags=["life"])
        self.assertEqual([t.title for t in self.store.search("周报")], ["写周报"])
        self.assertEqual([t.title for t in self.store.search("LIFE")], ["买牛奶"])
        self.assertEqual(self.store.search("没有的东西"), [])

    def test_stats_counts_and_rate(self) -> None:
        first = self.store.add("写周报", priority="high")
        self.store.add("买牛奶")
        self.store.done(first.id)
        data = self.store.stats()
        self.assertEqual((data["total"], data["done"], data["pending"]), (2, 1, 1))
        self.assertAlmostEqual(data["done_rate"], 0.5)
        self.assertEqual(data["by_priority"]["high"], 1)
        self.assertEqual(data["by_priority"]["normal"], 1)
```

### 6.5 检查有没有漏掉的标记

```powershell
git diff --check
```

没有输出 = 没有残留的空白错误。再保险一点：

```powershell
Select-String -Path todo\*.py, tests\*.py, README.md -Pattern '^(<<<<<<<|=======|>>>>>>>)'
```

**必须什么都没搜到。** 有输出就是还有没处理完的冲突。

---

## 7. 标记为已解决

```powershell
git add -A
git status
```

```text
On branch main
All conflicts fixed but you are still merging.
  (use "git commit" to conclude merge)

Changes to be committed:
        modified:   README.md
        modified:   tests/test_store.py
        modified:   todo/cli.py
        modified:   todo/store.py
```

`All conflicts fixed but you are still merging` —— 冲突解完了，但**合并还没提交**。`git add` 就是"我解决好了"的信号。

---

## 8. 验收：测试必须全绿

**这一步是本节的重点。** 冲突标记删干净、代码能跑，**不代表合并正确**。

```powershell
python -m unittest discover -s tests -q
```

**必须看到 14 个测试全过：**

```text
Ran 14 tests in 0.0xxs

OK
```

为什么是 14：原来的 12 个 + search 的 1 个 + stats 的 1 个。

如果这里是 12 或 13，说明你**丢掉了一个测试方法**（很可能是解冲突时只留了一边）。回去 6.4 检查。

如果有 `IndentationError`，说明方法插到 `if __name__ == "__main__":` 里面了（缩进不对）。

再手动跑一遍两个新命令：

```powershell
python -m todo.cli search 牛奶
python -m todo.cli stats
```

```text
[ ] #2 (normal) 买牛奶  @life

共 1 条
总数 2  已完成 0  未完成 2
完成率 0%
  low    0
  normal 1
  high   1
```

**两个功能都活着。**

---

## 9. 提交合并

```powershell
git commit -m "merge: 合并统计功能"
```

```powershell
git lg
```

```text
*   da3a0c0 (HEAD -> main) merge: 合并统计功能
|\
| * a6b6625 (feature/stats) feat(store): 增加任务统计
* |   2b27f7b merge: 合并搜索功能
|\ \
| |/
| | * 042f020 (feature/search) feat(store): 支持按关键词搜索任务
| |/
|/|
* 8b2f0d1 docs: 补充贡献说明
```

这个图形现在能看懂了：两条分支，各自从 `8b2f0d1` 分出来，各自汇回 main。

---

## 10. 清理

```powershell
git branch -d feature/search feature/stats
```

```text
Deleted branch feature/search (was 042f020).
Deleted branch feature/stats (was a6b6625).
```

```powershell
git branch          # 只剩 main
git status          # 干净
```

---

## 检查点

- [ ] `git lg` 里有**两个**合并提交，图形呈闭环
- [ ] `python -m unittest discover -s tests -q` → **14 tests OK**
- [ ] `python -m todo.cli search 牛奶` 和 `stats` 都能用
- [ ] `git branch` 只剩 `main`
- [ ] `git diff --check` 无输出，没有任何残留的冲突标记

## 思考题

1. 为什么第一次合并用 `--no-ff`，第二次没用也能产生合并提交？
2. `<<<<<<< HEAD` 里的 HEAD，指的是哪条分支？
3. 如果解冲突时把 `search` 方法删了、但把 `cli.py` 里的 `search` 子命令留下了，会发生什么？测试能发现吗？
4. `git add` 之后，Git 有没有检查你解得对不对？
5. 什么情况下 `git merge` 不会冲突，即使两边都改了代码？

<details>
<summary>答案</summary>

1. 第一次 main 没分叉（feature/search 是从 main 直接长出去的），默认会快进、不留痕迹，所以用 `--no-ff` 强制造合并提交。第二次 main 已经往前走了（有了合并提交），必然分叉，所以必然产生三方合并。
2. 你执行 `merge` 时所在的分支，也就是 `main`（"我这边的"）。
3. 不会报错，但运行 `python -m todo.cli search xx` 会 `AttributeError: 'TaskStore' object has no attribute 'search'`。**测试能发现**——因为 `test_search_finds_title_and_tags` 会调用 `store.search()`。这就是"解完必须跑测试"的意义：**语法正确，语义错误**。
4. 没有。`git add` 只是声明"我处理好了"，Git 完全信任你。它不检查标记有没有删干净，也不检查逻辑对不对。
5. 两边改的是**不同文件**，或者同一个文件里**距离足够远**的区域（Git 按 hunk 合并，默认上下文不重叠就能自动合）。lab04 里 `import json` 那处就是自动合好的。

</details>

---

**下一步**：`labs/lab05-远程与团队协作.md`
