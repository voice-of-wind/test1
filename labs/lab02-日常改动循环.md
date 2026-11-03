# lab02 · 日常改动循环

**目标**：把"改代码 → 看 diff → 挑着提交 → 写信息"这套动作练成肌肉记忆，并处理好不该进仓库的文件。

**对应阅读**：`docs/02-提交与历史.md`
**预计**：40 分钟

---

## 准备

```powershell
cd D:\AI\deepseekHarness\DS_project\gitlearn\project
git status
```

应该是 `nothing to commit, working tree clean`。如果 lab01 还没做完，先回去做。

---

## A. 最小的改动循环

### 1. 改一行代码

打开 `todo/cli.py`，找到 `cmd_add`：

```python
def cmd_add(store: TaskStore, args: argparse.Namespace) -> int:
    task = store.add(args.title, priority=args.priority, tags=args.tag)
    print(f"已添加 #{task.id}：{task.title}")
    return 0
```

把最后那句 print 改成：

```python
    print(f"已添加 #{task.id}：{task.title}（{task.priority}）")
```

### 2. 先看状态

```powershell
git status --short
```

```text
 M todo/cli.py
```

左边空、右边 M = 工作区改了，**还没进暂存区**。

### 3. 看 diff

```powershell
git diff
```

```diff
diff --git a/todo/cli.py b/todo/cli.py
index 3f8a1c2..b7d4e51 100644
--- a/todo/cli.py
+++ b/todo/cli.py
@@ -44,7 +44,7 @@ def cmd_add(store: TaskStore, args: argparse.Namespace) -> int:
     task = store.add(args.title, priority=args.priority, tags=args.tag)
-    print(f"已添加 #{task.id}：{task.title}")
+    print(f"已添加 #{task.id}：{task.title}（{task.priority}）")
     return 0
```

`-` 是旧的，`+` 是新的。**这就是你将要提交的全部内容**——确认是你要的。

### 4. 确认功能没坏

```powershell
python -m unittest discover -s tests -q
```

```text
Ran 12 tests in 0.0xxs

OK
```

> 养成"提交前跑测试"的习惯。CI 会兜底，但等 CI 反馈太慢。

### 5. 暂存 + 再看

```powershell
git add todo/cli.py
git diff --staged
```

内容跟刚才一样，但这个命令看的是**暂存区 vs 最新提交**——也就是"我现在 commit 会提交什么"。

此刻 `git diff` 应该变成空的（工作区和暂存区一致了）。

### 6. 提交

```powershell
git commit -m "feat(cli): 添加任务时回显优先级"
```

```text
[main 4f2c8a1] feat(cli): 添加任务时回显优先级
 1 file changed, 1 insertion(+), 1 deletion(-)
```

---

## B. 不该进仓库的文件

### 1. 跑一下程序

```powershell
python -m todo.cli add "写周报" -p high -t work
python -m todo.cli add "买牛奶" -t life
python -m todo.cli list
```

```text
[ ] #1 (high) 写周报  @work
[ ] #2 (normal) 买牛奶  @life

共 2 条
```

### 2. 看 Git 怎么说

```powershell
git status --short
```

```text
?? data/
```

`??` = 未跟踪。`data/tasks.json` 是你的**本地数据**，每台机器不一样，不该进仓库。

### 3. 用 `.gitignore` 让它消失

打开 `.gitignore`，在末尾加上：

```gitignore

# 本地数据，每台机器不一样，不该进仓库
data/
```

```powershell
git status --short
```

```text
 M .gitignore        ← 只有 .gitignore 自己变了，data/ 不见了
```

**注意：`.gitignore` 文件本身要提交**，否则别人拿到的仓库没有这条规则。

```powershell
git add .gitignore
git commit -m "chore: 忽略本地数据目录"
```

### 4. 验证一下

```powershell
python -m todo.cli add "第三件事"
git status --short
Get-ChildItem data
```

`data/tasks.json` 确实在磁盘上，但 `git status` 里没有它了。**这就是 `.gitignore` 的作用：让 Git 假装看不见它。**

---

## C. 把一次改动拆成两次提交（`add -p`）

场景：你同时改了两件不相干的事，但不想塞进同一个提交。

### 1. 改两处

`todo/cli.py` 第 22 行左右：

```python
VERSION = "0.1.0"
```
改成：
```python
VERSION = "0.2.0"
```

`todo/cli.py` 的 `cmd_list` 里：

```python
    if not tasks:
        print("（这里还没有任务）")
        return 0
```
改成：
```python
    if not tasks:
        print("（这里还没有任务，用 add 加一条吧）")
        return 0
```

```powershell
git status --short
git diff --stat
```

```text
 M todo/cli.py
 todo/cli.py | 4 ++--
 1 file changed, 2 insertions(+), 2 deletions(-)
```

4 行改动，但它们是**两件事**。

### 2. 一段一段挑

```powershell
git add -p todo/cli.py
```

Git 会一段一段问你：

```text
@@ -19,7 +19,7 @@ from .store import DEFAULT_PATH, TaskStore

-VERSION = "0.1.0"
+VERSION = "0.2.0"
Stage this hunk [y,n,q,a,d,s,e,?]?
```

输入 `y`（这段要），回车。

```text
@@ -68,7 +68,7 @@ def cmd_list(store: TaskStore, args: argparse.Namespace) -> int:
     tasks = store.all() if args.all else store.pending()
     if not tasks:
-        print("（这里还没有任务）")
+        print("（这里还没有任务，用 add 加一条吧）")
Stage this hunk [y,n,q,a,d,s,e,?]?
```

输入 `n`（这段先不要），回车。

### 3. 检查

```powershell
git diff --staged          # 只有版本号
git diff                   # 只有提示文案
```

```powershell
git commit -m "chore(release): 版本号升到 0.2.0"
```

```powershell
git add todo/cli.py
git commit -m "feat(cli): 空列表提示更友好"
```

一条改动，两条干净的提交。`git log --oneline` 应该变成 5 条。

> 交互按键速记：`y` 要、`n` 不要、`s` 再拆细、`q` 退出、`?` 帮助。

---

## D. 提交信息写错了，改掉

假装手滑：

```powershell
git commit --allow-empty -m "docs: 补充贡献说名"
```

（`--allow-empty` 造一个空提交，专门用来练手。）

```powershell
git lg
```

```text
* 7a1e9c4 (HEAD -> main) docs: 补充贡献说名     ← 错别字「名」
* ...
```

改掉：

```powershell
git commit --amend -m "docs: 补充贡献说明"
```

```text
[main 8b2f0d1] docs: 补充贡献说明
 Date: Fri Oct 30 10:40:46 2026 +0800
```

再看：

```powershell
git lg
```

```text
* 8b2f0d1 (HEAD -> main) docs: 补充贡献说明     ← 哈希变了！
```

**哈希变了**，因为这是一个全新的提交（内容一样，但提交信息变了 → 哈希变）。旧的 `7a1e9c4` 还在 reflog 里。

> 所以：**已经 push 的提交不要 amend**，否则你本地和远程的历史就对不上了。

---

## E. 撤销一个还没提交的改动

```powershell
git status --short            # 干净
```

现在故意改坏一个文件——把 `todo/models.py` 的 `format` 方法里删掉几行（随便删，反正要撤销）：

```powershell
Add-Content -Path todo\models.py -Value "`n# 这是我随手加的一行，等下要撤销" -Encoding UTF8
git status --short
git diff
```

确认改坏了，现在撤销：

```powershell
git restore todo/models.py
git status --short
```

```text
（什么都没有）
```

`git restore <file>` = **把工作区这个文件恢复到最新提交的样子**。你刚加的改动没了。

⚠️ 这个操作**不可撤销**（没提交过的东西没有历史）。所以 `restore` 之前，`git diff` 一定要看过。

---

## F. 进阶实验：已经跟踪的文件，加进 .gitignore 也没用

> 这个坑几乎每个人都会踩一次，提前踩。

### 1. 强行把数据文件提交进去

```powershell
git add -f data/tasks.json
git commit -m "chore: 误提交数据文件（马上撤销）"
git status --short
```

### 2. 现在再改 .gitignore，看有没有用

`.gitignore` 里已经有 `data/` 了，但：

```powershell
python -m todo.cli add "又加了一条"
git status --short
```

```text
 M data/tasks.json      ← 还是被跟踪着！
```

**`.gitignore` 只对"未跟踪"的文件生效。** 已经进了版本控制的文件，Git 会继续跟踪它的每一次变化。

### 3. 正确做法

```powershell
git rm --cached data/tasks.json      # 从版本控制移除，但保留本地文件
```

```text
rm 'data/tasks.json'
```

```powershell
git status --short
```

```text
D  data/tasks.json        ← 这个"删除"会被提交
```

```powershell
git commit -m "chore: 不再跟踪本地数据文件"
git status --short
```

干净了。而且 `data/tasks.json` 还在磁盘上（`--cached` 只动版本控制，不动文件）。

> 不加 `--cached` 的 `git rm` 会把本地文件也删掉。**这两个一定要分清。**

---

## 检查点

- [ ] `git status` 干净
- [ ] `git lg` 有 6 条左右提交，信息都是 `type: 说明` 格式
- [ ] `data/` 不在版本控制里，但磁盘上还有 `data/tasks.json`
- [ ] `python -m unittest discover -s tests -q` 还是 12 个测试全过
- [ ] 能解释 `git diff` 和 `git diff --staged` 的区别

## 思考题

1. `git add` 之后又改了文件，再 `commit`，提交进去的是哪个版本？
2. `git commit --amend` 之后，原来那条提交去哪了？
3. 为什么 `--cached` 这个参数很重要？
4. 提交前你想确认"这次到底提交了什么"，该用哪个命令？

<details>
<summary>答案</summary>

1. **暂存区里的那个版本**（`add` 时的那一刻）。之后再改的内容不会被提交，`git status` 会显示 `MM`（暂存了一份，工作区又改了）。
2. 还在。它变成了"不可达对象"，`git reflog` 能看到，默认 30 天后被 `git gc` 回收。
3. `git rm` 默认会**同时删除工作区文件**。对"我只是不想跟踪它，但文件我还要用"（数据、配置、日志）的场景，必须加 `--cached`。
4. `git diff --staged`（或 `git status`）。

</details>

---

**下一步**：`labs/lab03-分支.md`
