# Git 系统学习包

一套"边读边敲"的 Git 教程 + 一个真的能跑的小项目。

**设计原则：** 每一节都配一个可执行的实验（lab），实验对象是 `project/` 里那个几百行的 Python 任务清单程序。你不需要背命令，只需要按顺序把 7 个实验敲一遍，敲完就覆盖了日常开发 90% 的 Git 操作。

---

## 目录里有什么

```
gitlearn/
├── README.md              ← 你在这里：环境准备 + 学习路线
├── 学习清单.md             ← 7 个实验的完成标准，做完打勾
├── docs/                  ← 概念讲解（先读，再动手）
│   ├── 01-概念模型.md         四个区域、提交的本质、HEAD
│   ├── 02-提交与历史.md       status/add/commit/diff/log/blame
│   ├── 03-分支.md             分支就是指针
│   ├── 04-合并与冲突.md       ff / merge commit / 冲突解决
│   ├── 05-远程与协作.md       remote/fetch/pull/push/PR/tag
│   ├── 06-重写历史与救火.md   rebase/reset/revert/reflog/cherry-pick/stash/bisect
│   ├── 07-团队日常.md         工作流、规范、gitignore/gitattributes/hooks
│   └── 08-速查与故障.md       一页命令表 + 20 个"我该怎么办"
├── labs/                  ← 动手实验（照着敲）
│   ├── lab01-初始化与首次提交.md
│   ├── lab02-日常改动循环.md
│   ├── lab03-分支.md
│   ├── lab04-合并与冲突.md      ← 最核心的一节
│   ├── lab05-远程与团队协作.md
│   ├── lab06-重写历史与救火.md
│   └── lab07-综合演练.md        ← 模拟一个完整的迭代
├── project/               ← 练习对象（一开始故意没有 .git）
└── tools/
    ├── new-sandbox.ps1        生成"脏历史"沙盒仓库（lab06 用）
    ├── reset-practice.ps1     把练习环境恢复到起点（重来用）
    └── pristine-project.zip   project/ 的原始快照（重置时用）
```

---

## 一、环境准备（10 分钟，只做一次）

打开 **PowerShell**，在 `gitlearn` 目录下依次执行。

### 1. 确认工具在

```powershell
git --version
python --version
```

需要 Git 2.23 以上（要新的 `git switch` / `git restore` 命令），Python 3.10 以上。

### 2. 告诉 Git 你是谁

提交记录里会永久带着这两个信息：

```powershell
git config --global user.name "你的名字"
git config --global user.email "你的邮箱@example.com"
```

> 用公司仓库时，邮箱最好和 Git 平台账号一致，否则提交在网页上认不出是你。

### 3. 一次性配好这 8 项

```powershell
git config --global init.defaultBranch main      # 新仓库默认分支叫 main，不叫 master
git config --global core.quotepath false         # 中文文件名正常显示，不显示 \346\226\207
git config --global core.autocrlf false          # 换行符交给 .gitattributes 管（见 docs/07）
git config --global pull.rebase false            # git pull 默认用 merge，不猜
git config --global push.default simple          # git push 只推当前分支
git config --global fetch.prune true             # 远程删掉的分支，本地跟着清
git config --global core.editor notepad          # 需要写多行提交信息时用记事本
git config --global alias.lg "log --oneline --graph --all --decorate"
```

最后一条是别名：以后敲 `git lg` 就等于敲那一长串，看历史非常方便。再顺手加两个：

```powershell
git config --global alias.st "status -sb"
git config --global alias.last "log -1 HEAD --stat"
```

检查一下都生效了：

```powershell
git config --global --list
```

> 如果你习惯 VS Code，把 `notepad` 换成 `"code --wait"`（注意引号）。

### 4. 让终端正确显示中文（Windows 必做）

PowerShell 默认用 GBK，`git log` 里的中文会变乱码。在**每个新开的窗口**里执行：

```powershell
chcp 65001 > $null
$env:PYTHONUTF8 = "1"
```

嫌麻烦就写进 PowerShell 配置文件，以后自动生效：

```powershell
if (-not (Test-Path $PROFILE)) { New-Item -Path $PROFILE -Force | Out-Null }
Add-Content -Path $PROFILE -Value "chcp 65001 > `$null"
Add-Content -Path $PROFILE -Value "`$env:PYTHONUTF8 = '1'"
```

---

## 二、学习路线

按顺序做，不要跳。每个 lab 先读对应的 `docs/` 章节（15 分钟），再照着 `labs/` 敲（30–60 分钟）。

| 阶段 | 内容 | 对应文件 | 预计 |
| --- | --- | --- | --- |
| ① 打地基 | 四个区域、提交、看历史 | docs/01、02 → lab01、lab02 | 1.5 h |
| ② 分支与合并 | 分支的本质、冲突怎么解 | docs/03、04 → lab03、lab04 | 2 h |
| ③ 团队协作 | 远程、push/pull、PR、tag | docs/05 → lab05 | 1.5 h |
| ④ 进阶与救火 | rebase、reset、reflog、bisect | docs/06 → lab06 | 2 h |
| ⑤ 综合 | 完整走一个迭代 | lab07 | 1 h |

**别一次做完。** 一个阶段做完，隔一天再做下一个——Git 的肌肉记忆靠重复，不靠一口气读完。

### 每一节怎么用

1. **读 `docs/`**：只求看懂"为什么"，看不懂的细节先跳过。
2. **敲 `labs/`**：一条一条敲，**不要复制粘贴整段**。手打能逼你看清每个参数。
3. **对输出**：lab 里给了预期输出。对不上就先别往下走，那通常是环境问题（见 docs/08）。
4. **打勾**：`学习清单.md` 里有验收标准，做到了才勾。
5. **弄坏了**：跑 `tools/reset-practice.ps1` 重来。练习仓库弄坏是常态，不是事故。

---

## 三、三条铁律（先记住，能省掉 90% 的麻烦）

1. **动手前先 `git status`。** 它会告诉你现在在哪个分支、有哪些改动、有没有未完成的合并。读懂它，一半的"诡异情况"就解释清楚了。
2. **提交前先 `git diff`。** 你以为什么改了，和实际改了什么，经常不是一回事。
3. **已经 push 到公共分支的历史，不要改写。** `rebase` / `reset` / `amend` 只用在还没推出去、只有你自己在用的分支上。

---

## 四、从这里开始

```powershell
cd project
python -m unittest discover -s tests -v      # 先确认程序本身是好的
cd ..
```

看到 `Ran 12 tests ... OK` 之后，打开 `labs/lab01-初始化与首次提交.md`。

---

## 五、学完自检

不看资料，能顺畅做完下面这些，日常开发就够用了：

- [ ] 从零建仓库、提交、看历史
- [ ] 开分支写功能，回主干修紧急 bug，再回来继续
- [ ] 解决一次多文件冲突，并且能让测试重新变绿
- [ ] 把分支推到远程，从远程拉别人的改动，处理 push 被拒
- [ ] 用 `rebase -i` 把三条垃圾提交压成一条，并改掉提交信息
- [ ] 误用 `reset --hard` 后，用 `reflog` 把提交捞回来
- [ ] 用 `bisect` 从 30 个提交里定位出哪次提交引入的 bug
- [ ] 说清楚 `git pull` 到底等于哪两条命令
