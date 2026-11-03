# lab05 · 远程与团队协作

**目标**：用**本地裸仓库**完整模拟团队协作——推、拉、push 被拒、tag。全程不需要网络和 GitHub 账号。

**对应阅读**：`docs/05-远程与协作.md`
**预计**：60 分钟

---

## 0. 先理解"远程"是什么

"远程仓库"技术上就是**另一个 Git 仓库**。只是它通常：

- 没有工作区（叫**裸仓库**，bare repo），只存历史和对象
- 放在一台大家都能访问的机器上
- 用 URL 访问（https / ssh / 本地路径）

所以本地建一个裸仓库，就能 100% 模拟 GitHub。**命令完全一样**，学会了换成 https 地址就行。

这个 lab 要用到三个目录：

```text
gitlearn\
├── remotes\todo.git      ← 扮演 GitHub（裸仓库，没有工作区）
├── project\              ← 你（已经有 main 和两次合并）
└── project-bob\          ← 扮演同事 Bob（等下 clone 出来）
```

---

## 1. 建"远程服务器"

```powershell
cd D:\AI\deepseekHarness\DS_project\gitlearn
New-Item -ItemType Directory -Force -Path remotes | Out-Null
git init --bare remotes\todo.git
git -C remotes\todo.git symbolic-ref HEAD refs/heads/main
```

第一条建裸仓库，第二条**把它的默认分支显式设成 `main`**（这行很关键，下面解释）。

```text
Initialized empty Git repository in D:/AI/deepseekHarness/DS_project/gitlearn/remotes/todo.git/
```

看看里面有什么：

```powershell
Get-ChildItem remotes\todo.git
```

```text
HEAD  config  description  hooks  info  objects  refs
```

**没有 `todo/`、`tests/` 这些文件**——裸仓库只存历史，不存工作区。这就是"服务器"的样子。

> `--bare` 的作用：不建工作区。它专门用来当中央仓库。

### 为什么要有 `symbolic-ref` 那一条

裸仓库也有一个 `HEAD` 文件，它决定"别人 clone 下来默认检出哪条分支"。`git init` 会按 `init.defaultBranch` 来设——你的系统配置里可能是 `master`，而我们要用的是 `main`。

不设的话，Bob 一 clone 就会看到：

```text
warning: remote HEAD refers to nonexistent ref, unable to checkout
```

然后得到一个空目录 + 一条空的 `master` 分支。**这是本地裸仓库最容易踩的坑。**

`symbolic-ref HEAD refs/heads/main` 就是"把这个服务器的默认分支设成 main"，等价于 GitHub 仓库设置里的 "Default branch"。

---

## 2. 把本地仓库连上去

```powershell
cd project
git remote add origin ..\remotes\todo.git
git remote -v
```

```text
origin  D:/AI/deepseekHarness/DS_project/gitlearn/remotes/todo.git (fetch)
origin  D:/AI/deepseekHarness/DS_project/gitlearn/remotes/todo.git (push)
```

`origin` 只是**名字**，随便起。`..\remotes\todo.git` 是**地址**，可以换成 `https://github.com/you/todo.git`。

> 用相对路径 `..\remotes\todo.git` 时，Git 会存成绝对路径，所以之后从任何目录操作都有效。

---

## 3. 推上去

```powershell
git push -u origin main
```

```text
Enumerating objects: 31, done.
Counting objects: 100% (31/31), done.
...
To D:/AI/deepseekHarness/DS_project/gitlearn/remotes/todo.git
 * [new branch]      main -> main
branch 'main' set up to track 'origin/main'.
```

`-u`（= `--set-upstream`）建立**跟踪关系**：以后 `git push` / `git pull` 不用再写 `origin main`。

```powershell
git branch -vv
```

```text
* main da3a0c0 [origin/main] merge: 合并统计功能
```

`[origin/main]` 出现了，而且没有 `ahead` / `behind`——说明本地和远程一致。

```powershell
git lg
```

```text
* da3a0c0 (HEAD -> main, origin/main) merge: 合并统计功能
```

**注意括号里多了 `origin/main`**：这个"远程跟踪分支"指向同一个提交。

---

## 4. 同事 Bob 克隆一份

```powershell
cd ..
git clone remotes\todo.git project-bob
```

```text
Cloning into 'project-bob'...
done.
```

> 如果看到 `warning: remote HEAD refers to nonexistent ref`，说明第 1 步的 `symbolic-ref` 漏了。补上：
>
> ```powershell
> git -C remotes\todo.git symbolic-ref HEAD refs/heads/main
> Remove-Item -Recurse -Force project-bob
> git clone remotes\todo.git project-bob
> ```

```powershell
cd project-bob
git lg
```

```text
* da3a0c0 (HEAD -> main, origin/main) merge: 合并统计功能
```

Bob 现在有了完整历史，而且 `origin` 已经自动配好（指向 `remotes\todo.git`）。

给他配个身份，让提交记录看得出是谁：

```powershell
git config user.name "Bob"
git config user.email "bob@example.com"
```

---

## 5. Bob 改点东西，推上去

```powershell
Add-Content -Path README.md -Value "`n## 常见问题`n`n**Q: 数据存哪里？**  `data/tasks.json`，已经在 .gitignore 里。`n" -Encoding UTF8
git add -A
git commit -m "docs: 补充常见问题"
git push
```

```text
To D:/AI/deepseekHarness/DS_project/gitlearn/remotes/todo.git
   da3a0c0..b91e2f4  main -> main
```

**远程的 main 往前走了。** 但你的 `project/` 还停在 `da3a0c0`——**push 不会自动同步到别人那里**。

---

## 6. 你这边：先 fetch，看清楚再合

```powershell
cd ..\project
git fetch
```

```text
remote: Enumerating objects: 5, done.
...
From D:/AI/deepseekHarness/DS_project/gitlearn/remotes/todo.git
   da3a0c0..b91e2f4  main       -> origin/main
```

注意：**只更新了 `origin/main`，你的 `main` 和工作区一点没变。**

```powershell
git status
```

```text
On branch main
Your branch is behind 'origin/main' by 1 commit, and can be fast-forwarded.
```

```powershell
git log --oneline HEAD..origin/main
```

```text
b91e2f4 docs: 补充常见问题
```

`HEAD..origin/main` 读作"远程有、我没有的提交"。

```powershell
git diff HEAD origin/main
```

看到 Bob 具体改了什么。**这才是安全的协作方式：fetch → 看 → 再合。**

```powershell
git merge origin/main
```

```text
Updating da3a0c0..b91e2f4
Fast-forward
 README.md | 3 +++
 1 file changed, 3 insertions(+)
```

或者一步到位（你已经确认过内容了）：

```powershell
git pull
```

> `git pull` = `git fetch` + `git merge`。省事，但你失去了中间"看一眼"的机会。**重要分支上建议手动两步。**

现在两边一致了：

```powershell
git status
git lg -3
```

---

## 7. 制造一次 push 被拒

这是协作里最高频的场景，必须亲手撞一次。

### 7.1 你本地提交一个改动（还没推）

改 `todo/models.py`，给 `Task` 加个 `__repr__`（随便一处小改动）：

```powershell
Add-Content -Path todo\models.py -Value "`n    def __repr__(self) -> str:`n        return f\"<Task #{self.id} {self.title!r}>\"`n" -Encoding UTF8
```

> 注意：这段必须缩进 4 空格（在类里）。如果你加错了位置导致语法错误，`python -c "import todo.models"` 会报错，先修好。

```powershell
python -m unittest discover -s tests -q      # 15 tests? 不，还是 14，只是加了个方法
git add -A
git commit -m "feat(models): 给 Task 加上 __repr__"
```

### 7.2 同时 Bob 也提交并推送了

```powershell
cd ..\project-bob
git pull                                       # 先拉你刚才的（其实没新的）
Add-Content -Path README.md -Value "`n**Q: 支持排序吗？**  v0.3 会加上。`n" -Encoding UTF8
git add -A
git commit -m "docs: FAQ 补充排序问题"
git push
cd ..\project
```

### 7.3 现在你推

```powershell
git push
```

```text
To D:/AI/deepseekHarness/DS_project/gitlearn/remotes/todo.git
 ! [rejected]        main -> main (fetch first)
error: failed to push some refs to '...'
hint: Updates were rejected because the remote contains work that you do not
hint: have locally. ...
```

**被拒了。** 这不是错误，是 Git 在阻止你覆盖 Bob 的提交。

原因：你的 `main` 和 `origin/main` 已经分叉（各自多了一个提交），直接 push 会让远程历史"回退"。

### 7.4 正确解法：pull --rebase

```powershell
git pull --rebase
```

```text
From D:/AI/deepseekHarness/DS_project/gitlearn/remotes/todo.git
   b91e2f4..c8d9e01  main       -> origin/main
Successfully rebased and updated refs/heads/main.
```

发生了什么：Git 先把你的 `main` 退回到分叉点，把远程的新提交拉下来，然后**把你的提交"重放"到最新位置**。

```powershell
git lg
```

```text
* 7e3f2a1 (HEAD -> main) feat(models): 给 Task 加上 __repr__
* c8d9e01 (origin/main) docs: FAQ 补充排序问题
* b91e2f4 docs: 补充常见问题
* da3a0c0 merge: 合并统计功能
```

**一条直线，没有 merge commit。** 这就是 `--rebase` 的意义。

```powershell
python -m unittest discover -s tests -q      # 确保 rebase 没弄坏东西
git push
```

```text
To D:/AI/deepseekHarness/DS_project/gitlearn/remotes/todo.git
   c8d9e01..7e3f2a1  main -> main
```

成功。

> **另一种解法**：`git pull`（默认 merge），会产生一个 merge commit。两种都对，团队选一种统一即可。个人分支建议 rebase，公共分支建议 merge。

---

## 8. Tag：给版本打标记

现在 `main` 是一个可以发布的版本：

```powershell
git tag -a v0.2.0 -m "v0.2.0：支持搜索与统计"
```

```text
（没有输出，成功的命令通常不说话）
```

```powershell
git tag
```

```text
v0.2.0
```

```powershell
git show v0.2.0 --stat
```

看到 tag 信息 + 它指向的提交。

**关键：`git push` 不会推 tag。** 先验证这一点：

```powershell
git push
```

（提示 `Everything up-to-date`——但你刚打的 tag 根本没上去。）

```powershell
cd ..\project-bob
git fetch
git tag
```

**Bob 那边是空的。** 确认了 tag 不会自动同步。

推上去：

```powershell
cd ..\project
git push origin v0.2.0
```

```text
To D:/AI/deepseekHarness/DS_project/gitlearn/remotes/todo.git
 * [new tag]         v0.2.0 -> v0.2.0
```

```powershell
cd ..\project-bob
git fetch --tags
git tag
```

```text
v0.2.0
```

Bob 也能看到了。

> 一次推所有 tag：`git push --tags`。但日常建议**显式推单个**，避免把临时 tag 也推上去。

---

## 9. 在真 GitHub / Gitee 上，这些操作长什么样

本地练完，换成真实平台的步骤：

### 9.1 建远程仓库

- GitHub：右上角 `+` → New repository → 名字 → **不要**勾 "Add a README"（否则远程会有一个初始提交，你 push 会被拒）→ Create
- Gitee：类似

### 9.2 连上去

```powershell
git remote add origin https://github.com/你的用户名/todo.git
git push -u origin main
```

第一次会要求认证：

- **HTTPS**：用户名 + **Personal Access Token**（GitHub 2021 年后不接受账号密码）
  - GitHub → Settings → Developer settings → Personal access tokens → 勾 `repo` 权限
- **SSH**：`git@github.com:你的用户名/todo.git`，需要先把公钥传到 GitHub

### 9.3 PR（Pull Request）流程

网页上点按钮，背后对应这些命令：

```text
① 你 push 了 feature/xxx 分支
② 网页上 "Compare & pull request" → 选 base=main, compare=feature/xxx
   → 这等价于 git diff main...feature/xxx
③ 同事 review，提意见
④ 你改代码 → git commit → git push（PR 自动更新）
⑤ 点 "Merge pull request"
   → 等价于 git merge --no-ff feature/xxx
⑥ 点 "Delete branch"
   → 等价于 git push origin --delete feature/xxx
```

然后本地：

```powershell
git switch main
git pull
git branch -d feature/xxx
```

### 9.4 一个完整的团队循环（抄下来）

```powershell
git switch main
git pull
git switch -c feature/xxx
# ...写代码...
git add -A && git commit -m "feat: ..."
git push -u origin feature/xxx
# → 网页开 PR，等 review，改完再 push
# → 合并后：
git switch main
git pull
git branch -d feature/xxx
```

---

## 10. 清理现场（可选）

练习完可以把"公司服务器"删掉：

```powershell
cd D:\AI\deepseekHarness\DS_project\gitlearn
Remove-Item -Recurse -Force remotes
```

`project` 里的 `origin` 就失效了（`git remote -v` 还会显示，但用不了）。想重新连，重新 `git remote add`。

> **建议留着**：lab07 还要用它。

---

## 检查点

- [ ] `git remote -v` 能看到 `origin`
- [ ] `git branch -vv` 显示 `[origin/main]` 且没有 ahead/behind
- [ ] `git lg` 里有一条 `origin/main` 引用
- [ ] 亲手撞到过一次 `! [rejected]`，并且用 `pull --rebase` 解决了
- [ ] `git tag` 里有 `v0.2.0`，且 Bob 那边也能看到
- [ ] 能说出 `origin/main` 和 `main` 的区别

## 思考题

1. `git fetch` 之后，工作区文件变了吗？
2. `git pull --rebase` 和 `git pull` 的区别是什么？
3. 为什么 `git push` 之后 `origin/main` 会跟着动？
4. 如果 Bob 在你 rebase 之前就基于你那两个旧提交开了分支，会发生什么？
5. `git push --force` 在这个场景里会造成什么后果？

<details>
<summary>答案</summary>

1. 没变。`fetch` 只更新 `origin/main` 这个指针和对应的对象，工作区和 `main` 都不动。
2. `pull` = fetch + merge（可能产生 merge commit，历史有分叉）；`pull --rebase` = fetch + rebase（把你的提交重放到远程最新之后，历史是直线，但你的提交哈希会变）。
3. `push` 成功后，Git 同时更新本地的 `origin/main`，让它指向刚推上去的提交。所以它始终代表"上次同步时远程的样子"。
4. 他基于的旧提交被你 rebase 掉了（哈希变了），两边历史分叉。他一 push 就可能覆盖你，或者合并出一堆重复提交。**这就是"不要在公共分支上 rebase"的原因。**
5. 会直接把 Bob 的提交从远程抹掉。Bob 本地虽然还有，但他下次 push 又会把它们带回来，历史来回横跳，所有人都得重新对账。团队里这属于事故。

</details>

---

**下一步**：`labs/lab06-重写历史与救火.md`
