# lab03 · 分支

**目标**：亲手体验"分支只是一个指针"，学会创建、切换、查看、删除。

**对应阅读**：`docs/03-分支.md`
**预计**：30 分钟

---

## 准备

```powershell
cd D:\AI\deepseekHarness\DS_project\gitlearn\project
git status          # 必须干净
git lg              # 记住现在有几条提交
```

---

## A. 建一条分支，在上面改东西

```powershell
git switch -c experiment/hello
```

```text
Switched to a new branch 'experiment/hello'
```

`-c` = create。这一条命令做了两件事：建分支 + 切过去。

```powershell
git branch
```

```text
* experiment/hello
  main
```

`*` 表示当前分支。

现在改 `README.md`，在末尾加一行：

```powershell
Add-Content -Path README.md -Value "`n这一行是在 experiment/hello 分支上加的。`n" -Encoding UTF8
```

```powershell
git add README.md
git commit -m "docs(readme): 试一下分支上的改动"
git lg
```

```text
* 3c9d8e2 (HEAD -> experiment/hello) docs(readme): 试一下分支上的改动
* 8b2f0d1 (main) docs: 补充贡献说明
* ...
```

**看这一行：`HEAD -> experiment/hello`。** `main` 还停在 `8b2f0d1`，没动。

> 这就是"分支是指针"的实物证据：你提交时，只有当前分支那个指针往前挪了。

---

## B. 切回 main，看文件变化

```powershell
git switch main
```

```text
Switched to branch 'main'
```

**现在打开 `README.md` 看最后一行——那句话没了。**

```powershell
Get-Content README.md | Select-Object -Last 3
```

切分支时，Git 把工作区的文件换成了 `main` 那次提交的样子。你刚才的改动没有丢，它在 `experiment/hello` 的提交里。

再切回去：

```powershell
git switch experiment/hello
Get-Content README.md | Select-Object -Last 3
```

那句话又回来了。

```powershell
git switch -          # 回到上一个分支，不用记名字
```

---

## C. 两条分支并行：互不干扰

现在做真事：一条分支改文档，一条分支改代码，看它们互不影响。

### 1. 文档分支

```powershell
git switch -c docs/quickstart
```

在 `README.md` 的"## 跑起来"这一节后面加一段（随便写两句）：

```markdown
> 小提示：命令里的引号在 PowerShell 里是必须的。
```

```powershell
git add README.md
git commit -m "docs(readme): 补充 PowerShell 引号提示"
```

### 2. 代码分支（从 main 拉，不是从 docs 拉）

```powershell
git switch main
git switch -c feat/friendly-desc
```

改 `todo/cli.py` 里 `build_parser()` 的说明文字：

```python
    parser = argparse.ArgumentParser(
        prog="todo",
        description="练习 Git 用的小型任务清单",
    )
```

改成：

```python
    parser = argparse.ArgumentParser(
        prog="todo",
        description="一个小型任务清单（Git 练习用）",
    )
```

```powershell
git add todo/cli.py
git commit -m "feat(cli): 调整命令行说明文字"
```

### 3. 看全貌

```powershell
git lg
```

```text
* 1a2b3c4 (HEAD -> feat/friendly-desc) feat(cli): 调整命令行说明文字
| * 5d6e7f8 (docs/quickstart) docs(readme): 补充 PowerShell 引号提示
|/
* 8b2f0d1 (main) docs: 补充贡献说明
* ...
```

两条分叉从同一个点长出来，各自往前一格。**这就是"并行开发"。**

```powershell
git log --oneline --graph --all --decorate
```

（和 `git lg` 一样，只是没有别名时用这个。）

### 4. 回到 main，两条分支的改动都不在

```powershell
git switch main
git status                    # 干净
Get-Content README.md | Select-Object -Last 3    # 没有引号提示
Select-String -Path todo\cli.py -Pattern "版本参数"  # 什么都没有
```

**分支上的工作，不会自动跑到 main 上。** 要合，得 `merge`（下一节 lab04）。

---

## D. 删除分支

### 已合并的，直接删

```powershell
git switch main
git merge experiment/hello        # 先合进来（这条分支只有文档改动，会快进）
git branch -d experiment/hello
```

```text
Updating 8b2f0d1..3c9d8e2
Fast-forward
 README.md | 1 +
 1 file changed, 1 insertion(+)

Deleted branch experiment/hello (was 3c9d8e2).
```

`Fast-forward` = 快进合并：main 只是往前挪了一格，没有产生新提交。因为 main 没有分叉，直接"追上去"就行。

### 没合并的，Git 不让你删

```powershell
git branch -d docs/quickstart
```

```text
error: the branch 'docs/quickstart' is not fully merged
hint: If you are sure you want to delete it, run 'git branch -D docs/quickstart'
```

**Git 在保护你**：这条分支上有提交，还没合到任何地方，删了你可能就找不到了。

两个选择：

```powershell
git merge docs/quickstart          # 选项一：合进来（正确做法）
git branch -d docs/quickstart
```

```powershell
git branch -D docs/quickstart      # 选项二：确定不要了，强删
```

> 强删之后提交还在，reflog 里能找到（lab06 会练）。

现在把 `feat/friendly-desc` 也处理掉——先合进来，再删：

```powershell
git merge feat/friendly-desc
git branch -d feat/friendly-desc
```

（这次会提示 `Merge made by the 'ort' strategy` 或者 `Fast-forward`，取决于 main 有没有往前走。都正常。）

---

## E. 看看跟踪关系

```powershell
git branch -vv
```

```text
* main  e5f6a7b [origin/main: ahead 3] merge: ...
```

现在还没有远程，所以方括号里什么都没有。lab05 配好远程后再回来看，会显示 `[origin/main: ahead 3]` 这种信息。

---

## F. 分离头指针（看一眼就好）

```powershell
git switch --detach HEAD~2
```

```text
Note: switching to 'HEAD~2'.

You are in 'detached HEAD' state. ...
HEAD is now at 4f2c8a1 feat(cli): 添加任务时回显优先级
```

```powershell
git lg
```

```text
* ... (HEAD) ...        ← HEAD 直接指着提交，不在任何分支上
```

**这时候提交，提交不属于任何分支**。切走就可能"看不见"了（还在 reflog 里）。

```powershell
git switch main
```

回到正常状态。

> 什么时候会进 detached HEAD：看某个历史版本、看 tag、`git bisect` / `git rebase` 过程中。看到 `detached` 别慌，也别在上面直接写代码——先 `git switch -c <新分支名>`。

---

## 检查点

- [ ] `git branch` 只剩 `main`（其它都删了）
- [ ] `git lg` 是一条直线（所有分支都合进来了）
- [ ] 能说出"切分支时文件为什么会变"
- [ ] `git branch -d` 和 `-D` 的区别能讲清楚

## 思考题

1. 建一条分支，磁盘上会多出什么？大概多大？
2. 在 `experiment/hello` 上提交时，`main` 的指针动了吗？
3. `git branch -d` 报"not fully merged"，是出错了还是保护？
4. detached HEAD 状态下提交，提交会丢吗？

<details>
<summary>答案</summary>

1. 多一个文件：`.git/refs/heads/<分支名>`，内容是 40 个字符的哈希。几字节。**不复制任何代码。**
2. 没动。只有当前分支（HEAD 指向的那个）会前进。
3. 是保护。它在提醒你"这些提交还没合到别处，删了就难找了"。确认不要才用 `-D`。
4. 不会立刻丢，但没有分支指向它，`git log` 看不见。`git reflog` 能找到，30 天内可救。

</details>

---

**下一步**：`labs/lab04-合并与冲突.md`（本节最核心）
