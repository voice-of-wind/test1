# lab01 · 初始化与首次提交

**目标**：把一个普通目录变成 Git 仓库，完成第一次提交，并学会读 `status` / `log` / `show`。

**对应阅读**：`docs/01-概念模型.md`、`docs/02-提交与历史.md` 第 1–3 节
**预计**：30 分钟

---

## 0. 确认起点

```powershell
cd D:\AI\deepseekHarness\DS_project\gitlearn\project
```

先确认程序本身是好的（这一步很重要：出问题时才能确定是 Git 的问题还是代码的问题）：

```powershell
python -m unittest discover -s tests -v
```

应该看到：

```text
...
----------------------------------------------------------------------
Ran 12 tests in 0.0xx s

OK
```

> **记住 12 这个数字。** 后面每次合并完，你都要回来跑这条命令。

现在看看目录里有什么：

```powershell
Get-ChildItem -Force
```

应该有 `todo/`、`tests/`、`docs/`、`README.md`、`.gitignore`、`.gitattributes`。
**没有 `.git`** —— 这是故意的，你要自己建。

---

## 1. 在 Git 眼里，它还不是一个仓库

```powershell
git status
```

```text
fatal: not a git repository (or any of the parent directories): .git
```

这句话的意思是：Git 从当前目录开始往上找 `.git` 目录，一直找到磁盘根目录都没找到。

**对比记忆**：Git 靠 `.git` 目录识别仓库。有它才是仓库，没有就是普通文件夹。删掉 `.git` = 删掉所有历史（但工作区文件还在）。

---

## 2. 建仓库

```powershell
git init -b main
```

```text
Initialized empty Git repository in D:/AI/deepseekHarness/DS_project/gitlearn/project/.git/
```

`-b main` 指定初始分支叫 `main`（老版本 Git 默认叫 `master`）。

看看它建了什么：

```powershell
Get-ChildItem -Force .git
```

```text
Mode   Name
----   ----
d----  hooks
d----  info
d----  objects      ← 所有提交内容都存这里
d----  refs         ← 分支指针（一个分支一个文件）
-a---  HEAD         ← 我在哪条分支
-a---  config       ← 这个仓库的配置
-a---  description
```

再看状态：

```powershell
git status
```

```text
On branch main

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        .gitattributes
        .gitignore
        README.md
        docs/
        tests/
        todo/

nothing added to commit but untracked files present (use "git add" to track)
```

逐句翻译：

| 输出 | 意思 |
| --- | --- |
| `On branch main` | 你在 main 分支上 |
| `No commits yet` | 还没有任何提交（所以分支指针指向"空") |
| `Untracked files:` | 这些文件 Git 见过但没纳入管理 |
| 最后一行 | 现在提交不了，得先 `add` |

> 如果中文文件名显示成 `"docs/\345\274\200..."` 这种八进制，说明没配 `core.quotepath false`。回 README 环境准备第 3 步。
> **内容没有坏**，只是显示问题。

---

## 3. 放进暂存区

```powershell
git add .
```

`. ` 表示"当前目录下所有改动"（含新增文件）。

```powershell
git status
```

```text
On branch main

No commits yet

Changes to be committed:
  (use "git rm --cached <file>..." to unstage)
        new file:   .gitattributes
        new file:   .gitignore
        new file:   README.md
        new file:   docs/开发约定.md
        new file:   tests/test_cli.py
        tests/test_store.py
        todo/__init__.py
        todo/cli.py
        todo/models.py
        todo/store.py
```

区域从 "Untracked files" 变成了 "**Changes to be committed**"（将要提交的改动）。

**注意这里发生了什么**：文件内容一个字都没变，变的是 Git 对它们的记录状态——它们从"未跟踪"进了"暂存区"。

> 此刻 `git diff` 是**空的**（工作区和暂存区一样），`git diff --staged` 才有内容。试试看，体会一下两者的区别。

---

## 4. 第一次提交

```powershell
git commit -m "chore: 初始化 todo 项目（模型、存储、命令行、测试）"
```

```text
[main (root-commit) 6ea5f4c] chore: 初始化 todo 项目（模型、存储、命令行、测试）
 10 files changed, 595 insertions(+)
 create mode 100644 .gitattributes
 create mode 100644 .gitignore
 ...
```

逐段读：

- `[main ...]` 提交到了 main 分支
- `(root-commit)` 这是第一个提交（没有父提交，所以叫 root）
- `6ea5f4c` 新提交的短哈希（**你的肯定不一样**，因为时间不同）
- `10 files changed, 595 insertions(+)` 改了 10 个文件，新增 595 行

提交信息用了约定式格式（`chore: ...`），见 `project/docs/开发约定.md`。

> **关于 `-m`**：如果信息里要换行，用多个 `-m`：`git commit -m "标题" -m "正文"`。

---

## 5. 看历史

```powershell
git log
```

```text
commit 6ea5f4c39d26842dc9461395b2efcaa7c6cfe188 (HEAD -> main)
Author: mshx <2571120318@qq.com>
Date:   Fri Oct 30 10:40:45 2026 +0800

    chore: 初始化 todo 项目（模型、存储、命令行、测试）
```

- `(HEAD -> main)` 告诉你：HEAD 指向 main，main 指向这个提交。**这就是"分支是指针"的实物证据。**
- `Author` 是 README 里配的 `user.name` / `user.email`

日常用这个更清爽：

```powershell
git lg
```

```text
* 6ea5f4c (HEAD -> main) chore: 初始化 todo 项目（模型、存储、命令行、测试）
```

（`git lg` 是 README 里配的别名，等于 `git log --oneline --graph --all --decorate`。）

---

## 6. 看某次提交改了什么

```powershell
git show HEAD
```

```text
commit 6ea5f4c39d26842dc9461395b2efcaa7c6cfe188 (HEAD -> main)
Author: mshx <2571120318@qq.com>
Date:   Fri Oct 30 10:40:45 2026 +0800

    chore: 初始化 todo 项目（模型、存储、命令行、测试）

diff --git a/.gitattributes b/.gitattributes
new file mode 100644
index 0000000..4a1b2c3
--- /dev/null
+++ b/.gitattributes
@@ -0,0 +1,13 @@
+# 让 git 自己判断哪些是文本文件...
...
```

只想看改了哪些文件：

```powershell
git show --stat HEAD
```

```text
 .gitattributes                                     |  13 +++
 .gitignore                                         |  16 ++++
 README.md                                          |  99 +++++++++++++++++++
 docs/开发约定.md                                     |  58 ++++++++++++
 tests/test_cli.py                                  |  57 +++++++++++
 tests/test_store.py                                |  68 +++++++++++++
 todo/__init__.py                                   |   7 ++
 todo/cli.py                                        | 103 ++++++++++++++++++++
 todo/models.py                                     |  69 ++++++++++++++
 todo/store.py                                      | 105 +++++++++++++++++++++
 10 files changed, 595 insertions(+)
```

---

## 7. 再提交一次，让历史有两条

改一下 README，随便加一行（比如在末尾加 `## 许可` 一节）：

```powershell
Add-Content -Path README.md -Value "`n## 许可`n`n练习用，随意。" -Encoding UTF8
```

```powershell
git status --short
```

```text
 M README.md
```

右边 `M` = 工作区改了，还没 add。

```powershell
git diff
```

看到 `-` / `+` 那几行，确认改的是你想改的。

```powershell
git add README.md
git commit -m "docs(readme): 补充许可说明"
```

```powershell
git lg
```

```text
* 9b3f1d2 (HEAD -> main) docs(readme): 补充许可说明
* 6ea5f4c chore: 初始化 todo 项目（模型、存储、命令行、测试）
```

**两条提交，一条历史线，HEAD 在最上面。** 这就是最小可用的 Git 仓库。

---

## 检查点

做完这些才算过：

- [ ] `git status` 显示 `nothing to commit, working tree clean`
- [ ] `git lg` 有 2 条提交，提交信息不是 `update` / `fix` 这种
- [ ] `git show HEAD --stat` 能看到这次只改了 README
- [ ] 能回答下面的问题

## 思考题

1. `git add .` 之后，文件内容变了吗？
2. `git status` 里的 `(root-commit)` 是什么意思？
3. `HEAD -> main` 这个箭头，指向的是"分支"还是"提交"？
4. 如果现在删掉 `.git` 目录，`README.md` 会消失吗？

<details>
<summary>答案</summary>

1. 没变。`add` 只是把当前内容记进暂存区（`.git/index`），工作区文件原封不动。
2. 这是仓库的第一个提交，没有父提交。
3. `HEAD` 指向分支 `main`，`main` 指向提交。所以括号里是 `HEAD -> main`，两者一起标注在提交旁边。
4. 不会。工作区文件是普通文件，`.git` 只存历史。删掉 `.git` 等于放弃所有版本记录，代码还在，但变成"没有历史的普通目录"。

</details>

---

**下一步**：`labs/lab02-日常改动循环.md`
