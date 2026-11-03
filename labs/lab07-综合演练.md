# lab07 · 综合演练：走完一个完整迭代

**目标**：把前面学的所有东西串起来——需求 → 分支 → 开发 → 推送 → review → 合并 → 发布 → 清理。全程不需要别人配合，你自己扮演开发 + 同事。

**前置**：lab01–lab06 都做完了（`project/` 里有 `main`、`origin`、tag `v0.2.0`）。
**预计**：60 分钟

---

## 0. 场景

> 产品说：任务多起来以后，`list` 看不出轻重缓急，希望**按优先级从高到低**排。

这就是你的 "issue"。接下来是标准流程。

---

## 1. 确认起点

```powershell
cd D:\AI\deepseekHarness\DS_project\gitlearn\project
git switch main
git pull
git status
git lg -3
python -m unittest discover -s tests -q
```

应该是：干净、和远程一致、**14 个测试全过**。

```powershell
git tag
```

应该有 `v0.2.0`。

---

## 2. 开分支

```powershell
git switch -c feature/sort-by-priority
```

命名说明：`feature/` 前缀 + 连字符 + 说清做什么。**不要**叫 `sort`、`dev`、`我的分支`。

---

## 3. 第一个提交：数据层

### 3.1 `todo/store.py` 末尾追加

```python

    def sorted_by_priority(self) -> list[Task]:
        """按优先级从高到低排序；同优先级保持原有顺序。"""
        order = {name: index for index, name in enumerate(PRIORITIES)}
        return sorted(self._tasks, key=lambda task: -order.get(task.priority, 0))
```

（`PRIORITIES` 在 lab04 时已经 import 进来了，这里直接用。）

> 为什么用 `-order[...]`：`sorted` 是升序，而我们要 high 在前，所以把权重取负。

### 3.2 `tests/test_store.py` 加测试

插在 `if __name__ == "__main__":` 上面的类里：

```python
    def test_sorted_by_priority(self) -> None:
        self.store.add("低优先级", priority="low")
        self.store.add("高优先级", priority="high")
        self.store.add("普通任务")
        titles = [t.title for t in self.store.sorted_by_priority()]
        self.assertEqual(titles, ["高优先级", "普通任务", "低优先级"])
```

### 3.3 验证 + 提交

```powershell
python -m unittest discover -s tests -q
```

**15 个测试全过。**

```powershell
git add -A
git commit -m "feat(store): 支持按优先级排序"
```

---

## 4. 第二个提交：接到命令行上

### 4.1 `todo/cli.py`：给 `list` 加参数

找到：

```python
    p_list = sub.add_parser("list", help="列出未完成任务")
    p_list.add_argument("-a", "--all", action="store_true", help="连已完成的一起列")
```

在下面加一行：

```python
    p_list.add_argument("--sort", choices=["priority"], help="按优先级排序（高 → 低）")
```

### 4.2 `todo/cli.py`：改 `cmd_list`

原来的：

```python
def cmd_list(store: TaskStore, args: argparse.Namespace) -> int:
    tasks = store.all() if args.all else store.pending()
    if not tasks:
        print("（这里还没有任务，用 add 加一条吧）")
        return 0
    for task in tasks:
        print(task.format())
    print(f"\n共 {len(tasks)} 条")
    return 0
```

改成：

```python
def cmd_list(store: TaskStore, args: argparse.Namespace) -> int:
    if args.sort == "priority":
        tasks = store.sorted_by_priority()
    else:
        tasks = store.all() if args.all else store.pending()
    if not args.all:
        tasks = [task for task in tasks if not task.done]
    if not tasks:
        print("（这里还没有任务，用 add 加一条吧）")
        return 0
    for task in tasks:
        print(task.format())
    print(f"\n共 {len(tasks)} 条")
    return 0
```

> 注意：空列表那句话一个字都别改。`test_cli.py` 里有断言依赖它（`assertIn("还没有任务", out)`）。这是个很好的例子——**改代码前先看看有没有测试盯着它**。

### 4.3 `README.md` 命令表加一行

```markdown
| `list --sort priority` | 按优先级列出 |
```

### 4.4 验证 + 提交

```powershell
python -m unittest discover -s tests -q      # 15 个
```

手动试一下（没有任务数据的话先加几条）：

```powershell
python -m todo.cli add "低优先级的事" -p low
python -m todo.cli add "紧急的事" -p high
python -m todo.cli add "普通的事"
python -m todo.cli list --sort priority
```

```text
[ ] #4 (high) 紧急的事
[ ] #5 (normal) 普通的事
[ ] #3 (low) 低优先级的事

共 3 条
```

```powershell
git add -A
git commit -m "feat(cli): list 支持 --sort priority"
```

```powershell
git lg -3
```

---

## 5. 推送，开 PR

```powershell
git push -u origin feature/sort-by-priority
```

```text
To D:/AI/deepseekHarness/DS_project/gitlearn/remotes/todo.git
 * [new branch]      feature/sort-by-priority -> feature/sort-by-priority
branch 'feature/sort-by-priority' set up to track 'origin/feature/sort-by-priority'.
```

**如果有真 GitHub**，这时候网页上会出现 "Compare & pull request" 按钮，点开填标题和说明即可。本地裸仓库没有网页，我们就用命令行模拟。

---

## 6. 模拟 review：同事提了意见

（现在换顶帽子，你是 Bob。）

先"以同事的身份"把分支拉下来看看：

```powershell
cd ..\project-bob
git fetch
git diff main...origin/feature/sort-by-priority
```

> 三个点 `...` = "从分叉点开始比，只看这条分支带来的改动"。review 时用三个点，两个点会把主干上别人的改动也算进来。

Bob 的意见（真实 review 里经常是这样：先质疑，最后决定不改）：

> `sorted_by_priority` 里 `order.get(task.priority, 0)` 的默认值有点可疑——
> 万一有人传了个非法优先级，它会被当成 low 悄悄排到最后，而不是报错。
> 不过现在 `priority` 只能从 `choices` 里来，暂时进不来非法值，**先不拦**。
> 另外 `-order[...]` 这个取负的写法，建议补一句注释，不然下一个人要愣一下。

结论：**采纳"补注释"，不改接口。**

### 6.1 按意见改代码

在 `sorted_by_priority` 里加一行注释：

```python
    def sorted_by_priority(self) -> list[Task]:
        """按优先级从高到低排序；同优先级保持原有顺序。"""
        # sorted 是升序，取负号让 high(-2) 排在 low(0) 前面
        order = {name: index for index, name in enumerate(PRIORITIES)}
        return sorted(self._tasks, key=lambda task: -order.get(task.priority, 0))
```

### 6.2 追加提交（不是 amend！）

```powershell
cd ..\project
git add -A
git commit -m "docs(store): 说明优先级排序取负号的原因"
git push
```

> **为什么是追加提交而不是 `git commit --amend`？** 因为 `feature/sort-by-priority` 已经 push 了。amend 会让本地和远程的历史分叉，review 页面上的评论也会错位。**已推送的提交，用追加提交来表达"我改好了"。**

---

## 7. 合并（模拟点 "Merge pull request"）

（换回你的身份，也就是"有权限合并的人"。）

```powershell
git switch main
git pull
git merge --no-ff feature/sort-by-priority -m "merge: 合并按优先级排序功能"
```

```text
Merge made by the 'ort' strategy.
 README.md           | 1 +
 todo/cli.py         | 8 ++++++--
 todo/store.py       | 6 ++++++
 tests/test_store.py | 7 +++++++
 4 files changed, 22 insertions(+), 2 deletions(-)
```

```powershell
python -m unittest discover -s tests -q
```

**15 个全过。** 合并后一定要跑（这是 lab04 学到的）。

```powershell
git push
```

```powershell
git lg -4
```

```text
*   9a8b7c6 (HEAD -> main, origin/main) merge: 合并按优先级排序功能
|\
| * 3f2e1d0 (feature/sort-by-priority) docs(store): 说明优先级排序取负号的原因
| * 2c1b0a9 feat(cli): list 支持 --sort priority
| * 1a0f9e8 feat(store): 支持按优先级排序
|/
* 7e3f2a1 feat(models): 给 Task 加上 __repr__
```

---

## 8. 发布：打 tag

```powershell
git tag -a v0.3.0 -m "v0.3.0：支持按优先级排序"
git push origin v0.3.0
```

```powershell
git tag
```

```text
v0.2.0
v0.3.0
```

让 Bob 也同步到：

```powershell
cd ..\project-bob
git pull
git fetch --tags
git tag
```

---

## 9. 清理

```powershell
cd ..\project
git branch -d feature/sort-by-priority
git push origin --delete feature/sort-by-priority
```

```text
Deleted branch feature/sort-by-priority (was 3f2e1d0).
To D:/.../todo.git
 - [deleted]         feature/sort-by-priority
```

```powershell
git branch -a
git status
git lg -5
```

**本地和远程都只剩下 `main`。** 一次干净的迭代结束。

---

## 10. 复盘：这 9 步对应哪些命令

| 阶段 | 你敲的 | 背后的概念 |
| --- | --- | --- |
| 同步 | `git pull` | fetch + merge |
| 开分支 | `git switch -c` | 分支是指针 |
| 开发 | `git add` / `git commit` | 暂存区 → 本地仓库 |
| 推送 | `git push -u` | 建立上游跟踪 |
| review | `git diff main...分支` | 三点 diff |
| 改意见 | `git commit` + `git push` | 追加而不是改写 |
| 合并 | `git merge --no-ff` | 三方合并 + 保留分支痕迹 |
| 发布 | `git tag -a` + `git push origin <tag>` | tag 不随 push 走 |
| 清理 | `git branch -d` + `push --delete` | 删指针，提交仍在 |

---

## 检查点

- [ ] `python -m unittest discover -s tests -q` → **15 tests OK**
- [ ] `git lg` 里有一次 `--no-ff` 的合并提交
- [ ] `git tag` 有 `v0.2.0` 和 `v0.3.0`
- [ ] `git branch -a` 只剩 `main`
- [ ] `python -m todo.cli list --sort priority` 能按 high → normal → low 输出
- [ ] 能不看笔记，把"开分支 → 开发 → 推送 → 合并 → 打 tag → 清理"走一遍

## 思考题

1. 为什么 review 之后要"追加提交"而不是 `amend`？
2. `git diff main...feature/x` 和 `git diff main..feature/x` 有什么区别？
3. 如果 Bob 在你合并前也推了一个提交到 main，你的 `git push` 会怎样？
4. 合并之后，`feature/sort-by-priority` 这条分支的提交还在吗？
5. 如果这个功能上线后发现严重 bug，要回滚，怎么做最稳？

<details>
<summary>答案</summary>

1. 分支已经 push，`amend` 会改写已推送的历史，导致本地和远程分叉、review 评论错位。追加提交是"在历史上往后加"，谁都对得上。
2. 两个点：`main` 和 `feature/x` 直接比较（包含 main 上别人后来的改动）。三个点：从**共同祖先**开始比，只看 `feature/x` 自己带来的改动。review 用三个点。
3. 被拒（`! [rejected]` non-fast-forward）。需要先 `git pull --rebase`（或 `merge`）再推。
4. 还在。删分支只是删指针，提交已经被合并进 main 了（merge commit 有两个父，其中一个就是它）。
5. `git revert <合并提交的哈希> -m 1`（`-m 1` 指定保留哪个父提交）。**不要**用 `reset --hard` 然后强推——那会把别人的历史也抹掉。

</details>

---

## 全部做完了

回头看 `学习清单.md`，应该全部勾上了。

接下来建议：

1. 用**你自己的真实项目**，按 lab07 的流程走一遍
2. 把 `docs/08-速查与故障.md` 存成书签
3. 想再深入：`git worktree`、`git rerere`、`git filter-repo`、Git LFS、CI 里的 `git diff` 用法
