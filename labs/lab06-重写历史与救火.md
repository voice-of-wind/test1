# lab06 · 重写历史与救火

**目标**：在一个可以随便弄坏的沙盒仓库里，练会 `bisect` / `rebase -i` / `cherry-pick` / `stash` / `reset` / `reflog`。

**对应阅读**：`docs/06-重写历史与救火.md`
**预计**：90 分钟

> ⚠️ 这个 lab **不要**在 `project/` 里做。用 `sandbox/broken-history`，弄坏了就重跑脚本。

---

## 0. 生成沙盒

```powershell
cd D:\AI\deepseekHarness\DS_project\gitlearn
powershell -ExecutionPolicy Bypass -File tools\new-sandbox.ps1 -Force
```

```text
沙盒仓库已生成：D:\AI\deepseekHarness\DS_project\gitlearn\sandbox\broken-history

* 4b06b0f (exp/formatting) 加数字格式化 fmt()
* 2f50b61 (HEAD -> main) 加类型注解
* f69d78e update
* 7fece51 加除法
* 0d4bbe5 fix
* 5256f6f 加乘法
* 26cec45 111
* 1d519a1 update
* aca97e0 init: 加法和减法
```

（哈希可能和这里略有不同，以你自己看到的为准；**提交信息的顺序是一样的**。）

进去看看：

```powershell
cd sandbox\broken-history
```

```powershell
git lg
git status
python -m unittest -q
```

```text
F
======================================================================
FAIL: test_div (test_calc.CalcTest.test_div)
----------------------------------------------------------------------
AssertionError: 2 != 2.5

Ran 4 tests
FAILED (failures=1)
```

**测试是红的，这是故意的。** 有人在历史某处把 `div` 写成了整除 `//`。现在我们要找出是哪次提交干的。

> **随时可以重来**：`cd ..\..;  powershell -File tools\new-sandbox.ps1 -Force`

---

## 1. `git bisect`：从 9 个提交里定位 bug

### 1.1 手工模式（先理解原理）

```powershell
git bisect start
git bisect bad                    # 当前 HEAD 是坏的
git bisect good HEAD~7            # 第一个提交是好的
```

```text
Bisecting: 3 revisions left to test after this (roughly 2 steps)
[5256f6f...] 加乘法
```

Git 自动切到了中间那个提交（"加乘法"）。现在你测一下：

```powershell
python -m unittest -q
```

```text
Ran 3 tests
OK
```

这个提交是好的：

```powershell
git bisect good
```

```text
Bisecting: 1 revision left to test after this (roughly 1 steps)
[0d4bbe5...] fix
```

再测：

```powershell
python -m unittest -q
```

还是 OK。

```powershell
git bisect good
```

```text
Bisecting: 0 revisions left to test after this (roughly 0 steps)
[7fece51...] 加除法
```

```powershell
python -m unittest -q
```

```text
FAILED (failures=1)
```

坏了！

```powershell
git bisect bad
```

```text
7fece511d490dbd74f01423bef53072c94c402dd is the first bad commit
commit 7fece511d490dbd74f01423bef53072c94c402dd
    加除法

 calc.py      | 6 +++++-
 test_calc.py | 5 ++++-
```

**找到了：`加除法` 那次提交。** 9 个提交，只用了 3 次判断。

```powershell
git bisect reset
```

回到原来的位置。

### 1.2 全自动模式（真实项目里更常用）

```powershell
git bisect start
git bisect bad
git bisect good HEAD~7
git bisect run python -m unittest -q
```

```text
running 'python' '-m' 'unittest' '-q'
...
7fece511d490dbd74f01423bef53072c94c402dd is the first bad commit
    加除法
bisect found first bad commit
```

**你什么都没干，Git 自己跑完了。** 前提是"好坏"能用退出码判断（0=good，非 0=bad）——这也是为什么项目的测试要能一键跑、并且有明确退出码。

```powershell
git bisect reset
```

> 记下这个哈希 `7fece51`，等下会看到它被 rebase 改写。

---

## 2. `git rebase -i`：把 3 条垃圾提交压成 1 条

现在看历史，最近三条是：

```text
2f50b61 加类型注解      ← 只是加了类型注解
f69d78e update          ← 信息等于没说
7fece51 加除法          ← 主体
```

这三条其实是"一件事"（加除法），被拆成了三次。压成一条。

```powershell
git rebase -i HEAD~3
```

记事本会打开，内容是（**从上到下 = 从旧到新**）：

```text
pick 7fece51 加除法
pick f69d78e update
pick 2f50b61 加类型注解

# Rebase 0d4bbe5..2f50b61 onto 0d4bbe5 (3 commands)
#
# Commands:
# p, pick <commit> = use commit
# r, reword <commit> = use commit, but edit the commit message
# e, edit <commit> = use commit, but stop for amending
# s, squash <commit> = use commit, but meld into previous commit
# f, fixup <commit> = like "squash", but discard this commit's log message
# d, drop <commit> = remove commit
...
```

把后两行的 `pick` 改成 `squash`：

```text
pick 7fece51 加除法
squash f69d78e update
squash 2f50b61 加类型注解
```

**保存并关闭记事本**（Ctrl+S，然后关窗口）。

Git 会再弹一次记事本，让你编辑合并后的提交信息：

```text
# This is a combination of 3 commits.
# This is the 1st commit message:

加除法

# This is the commit message #2:

update

# This is the commit message #3:

加类型注解
```

改成一条像样的：

```text
feat(calc): 加除法（含类型注解与文档更新）
```

保存关闭。

```text
Successfully rebased and updated refs/heads/main.
```

```powershell
git lg
```

```text
* 8f3c2d1 (HEAD -> main) feat(calc): 加除法（含类型注解与文档更新）
* 0d4bbe5 fix
* 5256f6f 加乘法
* 26cec45 111
* 1d519a1 update
* aca97e0 init: 加法和减法
```

**三条变一条，而且提交信息能看了。**

> 三条提交的哈希全变了（`7fece51` → `8f3c2d1`）。这就是"改写历史"——`bisect` 找到的那个哈希现在已经不存在了，但**内容**还在（被合并进新提交）。

### 如果卡在 vim 里

看到满屏 `~`，底部没提示，说明进了 vim：

1. 按 `i`（进入编辑模式，左下角出现 `-- INSERT --`）
2. 改内容
3. 按 `Esc`
4. 输入 `:wq` 回车（保存退出）；不想保存用 `:q!`

想彻底避开：`git config --global core.editor notepad`（README 里配过）。

### 弄砸了怎么办

```powershell
git rebase --abort
```

回到 rebase 之前。**任何时候都可以。**

---

## 3. `git cherry-pick`：只搬一个提交

`exp/formatting` 分支上有一个提交（加 `fmt()` 函数），主线现在也需要：

```powershell
git log --oneline exp/formatting -3
```

```text
4b06b0f 加数字格式化 fmt()
2f50b61 加类型注解          ← 这条已经被 squash 掉了，但分支还指着它
...
```

```powershell
git switch main
git cherry-pick exp/formatting
```

```text
[main 5d4bea2] 加数字格式化 fmt()
 Date: Sat Oct 24 14:10:00 2026 +0800
 2 files changed, 10 insertions(+), 2 deletions(-)
```

```powershell
git lg -3
```

```text
* 5d4bea2 (HEAD -> main) 加数字格式化 fmt()
* 8f3c2d1 feat(calc): 加除法（含类型注解与文档更新）
```

**注意：hash 变了**（`4b06b0f` → `5d4bea2`）。cherry-pick 是"复制改动、重新提交"，不是"把提交搬过去"。

```powershell
python -m unittest -q
```

```text
FAILED (failures=1)     ← 还是那个 div 的 bug，5 个测试了
```

---

## 4. 修掉那个 bug

```powershell
Select-String -Path calc.py -Pattern "a // b"
```

```text
def div(a: float, b: float) -> float:
    return a // b
```

改成真除法：

```python
def div(a: float, b: float) -> float:
    if b == 0:
        raise ZeroDivisionError("除数不能为 0")
    return a / b
```

```powershell
python -m unittest -q
```

```text
Ran 5 tests
OK
```

```powershell
git add -A
git commit -m "fix(calc): 除法改成真除法，并处理除零"
```

**历史现在是干净的：能看懂的提交信息 + 全绿的测试。**

---

## 5. `git stash`：临时收起来

场景：改到一半，要去 `exp/formatting` 上看点东西。

```powershell
Add-Content -Path calc.py -Value "`n# 我正在写的新功能，先不提交" -Encoding UTF8
git status --short
```

```text
 M calc.py
```

```powershell
git stash push -m "半成品：新功能"
```

```text
Saved working directory and index state On main: 半成品：新功能
```

```powershell
git status --short
```

**干净了。** 改动去哪了？

```powershell
git stash list
```

```text
stash@{0}: On main: 半成品：新功能
```

```powershell
git stash show -p 'stash@{0}'
```

> **PowerShell 注意**：`stash@{0}` 里的 `@{}` 必须加引号，否则 PowerShell 会当成哈希表。

现在可以自由切分支了，看完回来：

```powershell
git stash pop
```

```text
On branch main
Changes not staged for commit:
        modified:   calc.py

Dropped refs/stash@{0} (...)
```

改动回来了，stash 条目也删了（`pop` = apply + drop）。

```powershell
git restore calc.py
```

---

## 6. `git reset` 三种模式

先造三个提交，用来当靶子：

```powershell
Add-Content -Path notes.txt -Value "- 三个测试提交 1" -Encoding UTF8
git commit -qam "test: 提交 1"
Add-Content -Path notes.txt -Value "- 三个测试提交 2" -Encoding UTF8
git commit -qam "test: 提交 2"
Add-Content -Path notes.txt -Value "- 三个测试提交 3" -Encoding UTF8
git commit -qam "test: 提交 3"
git lg -4
```

### `--soft`：撤销提交，改动全留在暂存区

```powershell
git reset --soft HEAD~1
git status --short
```

```text
M  notes.txt        ← 左边 M：改动在暂存区
```

```text
git lg -3
```

提交 3 没了，但它的改动还在暂存区，随时可以重新提交。**适合"提交早了/想重写提交信息"。**

```powershell
git commit -q -m "test: 提交 3（重写）"
```

### `--mixed`（默认）：撤销提交 + 取消暂存

```powershell
git reset HEAD~1
git status --short
```

```text
 M notes.txt        ← 右边 M：改动在工作区，不在暂存区
```

改动还在文件里，只是需要重新 `add`。

```powershell
git add -A
git commit -q -m "test: 提交 3（再来一次）"
```

### `--hard`：连工作区一起回到那个提交

```powershell
Add-Content -Path notes.txt -Value "- 这行会消失" -Encoding UTF8
git status --short
git reset --hard HEAD
git status --short
```

```text
（干净）
Select-String -Path notes.txt -Pattern "会消失"     ← 什么都没有，改动真的没了
```

**`--hard` 不可撤销**——除非……

---

## 7. `git reflog`：把 `--hard` 干掉的东西捞回来

### 7.1 制造事故

```powershell
git lg -4        # 记下现在有几个提交
git reset --hard HEAD~2
git lg -3
```

**两个提交消失了。** 手抖了吧。

### 7.2 看 reflog

```powershell
git reflog -8
```

```text
8b2f0d1 HEAD@{0}: reset: moving to HEAD~2
1a2b3c4 HEAD@{1}: commit: test: 提交 3（再来一次）
5d6e7f8 HEAD@{2}: commit: ...
...
```

`HEAD@{0}` 是你现在（被 reset 到的位置），`HEAD@{1}` 是**丢之前**的位置。

### 7.3 救回来

```powershell
git reset --hard 'HEAD@{1}'
```

> **PowerShell 必须加引号！** 不加会报 `unknown switch 'e'`——因为 PowerShell 把 `@{...}` 当成哈希表语法解析了。这是 Windows 上最高频的 Git 报错之一。

```powershell
git lg -3
```

**回来了。**

### 7.4 更安全的救法：开个新分支

```powershell
git switch -c rescue/lost 'HEAD@{2}'
```

从历史某个点开新分支，比直接 reset 更安全（原来的分支没动，可以对比）。

---

## 8. 收尾

```powershell
git status
git lg --all
python -m unittest -q
```

**你应该得到**：

- 一条整理过的主线历史（垃圾提交信息没了）
- 一个 `fix(calc)` 提交，测试全绿
- 一个从 reflog 救回来的世界

### 随时重来

```powershell
cd D:\AI\deepseekHarness\DS_project\gitlearn
powershell -ExecutionPolicy Bypass -File tools\new-sandbox.ps1 -Force
```

---

## 检查点

- [ ] 用 `bisect`（手工 + 自动各一次）找到了 `加除法`
- [ ] 用 `rebase -i` 把 3 条提交压成 1 条，并改写了提交信息
- [ ] 用 `cherry-pick` 把 `fmt()` 搬到了 main，并知道哈希为什么会变
- [ ] 用 `stash` 暂存并取回，知道 `stash@{0}` 要加引号
- [ ] 能说出 `reset --soft / --mixed / --hard` 各自动了哪几个区域
- [ ] 用 `reflog` 把 `reset --hard` 丢掉的提交捞了回来
- [ ] 知道 `git rebase --abort` 能救回 rebase 到一半的状态

## 思考题

1. `rebase -i` 的列表顺序，和 `git log` 的显示顺序为什么是反的？
2. `squash` 和 `fixup` 的区别？
3. `reset --hard` 之后，被丢的提交真的从磁盘上消失了吗？
4. `cherry-pick` 之后，两条分支上的同一个改动，将来合并会怎样？
5. 为什么 `reflog` 在别人的电脑上救不了你的场？

<details>
<summary>答案</summary>

1. `rebase -i` 的列表是"**将要被重放执行的顺序**"，从旧到新；`git log` 是"**从新到旧**"。一个是剧本，一个是历史记录。
2. `squash` 会保留被压缩提交的信息（在编辑器里合并成一段），`fixup` 直接丢弃，只留代码改动。整理垃圾提交时用 `fixup` 更省事。
3. 没有立刻消失。它们变成"不可达对象"，还在 `.git/objects` 里，`git reflog` 能找回。默认 30 天后 `git gc` 才真正清理。
4. 可能冲突。因为同一个改动在两条分支上各是一份"独立提交"，Git 合并时会看到两边都改了同一处。**所以能用 merge/rebase 就别用 cherry-pick。**
5. `reflog` 是**本地私有**的记录，不会 push，也不在远程仓库里。它只记录"这台机器上 HEAD 怎么动过"。

</details>

---

**下一步**：`labs/lab07-综合演练.md`
