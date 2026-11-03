<#
.SYNOPSIS
    生成一个"脏历史"沙盒仓库，专门用来练 rebase -i / reset / reflog / cherry-pick / bisect。

.DESCRIPTION
    在 gitlearn\sandbox\broken-history 下创建一个独立的 git 仓库：
      * 8 个提交，提交信息故意写得很烂（update / 111 / fix），用来练 squash 和 reword
      * 第 6 个提交埋了一个 bug（整除当除法），HEAD 上测试是红的，用来练 bisect
      * 分支 exp/formatting 上有个"想搬到 main"的提交，用来练 cherry-pick
    这个仓库随便弄坏，加 -Force 重跑本脚本就回到初始状态。

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File tools\new-sandbox.ps1
    powershell -ExecutionPolicy Bypass -File tools\new-sandbox.ps1 -Force
#>
[CmdletBinding()]
param(
    [switch]$Force
)

$ErrorActionPreference = 'Continue'

$root = Split-Path -Parent $PSScriptRoot
$repo = Join-Path $root 'sandbox\broken-history'

if (Test-Path $repo) {
    if (-not $Force) {
        Write-Host "已存在：$repo" -ForegroundColor Yellow
        Write-Host "想重建请加 -Force（会删掉里面所有东西）。" -ForegroundColor Yellow
        exit 0
    }
    Remove-Item -Recurse -Force $repo
}

New-Item -ItemType Directory -Force -Path $repo | Out-Null
$utf8 = New-Object System.Text.UTF8Encoding($false)

function Write-Src {
    param([string]$RelPath, [string]$Content)
    $full = Join-Path $repo $RelPath
    [System.IO.File]::WriteAllText($full, $Content, $utf8)
}

function Commit {
    param([string]$Message, [string]$Date)
    git -C $repo add -A
    $env:GIT_AUTHOR_DATE = $Date
    $env:GIT_COMMITTER_DATE = $Date
    git -C $repo commit -q -m $Message
    if ($LASTEXITCODE -ne 0) { throw "git commit 失败：$Message" }
    Remove-Item Env:\GIT_AUTHOR_DATE
    Remove-Item Env:\GIT_COMMITTER_DATE
}

git init -q --initial-branch=main $repo
git -C $repo config user.name "沙盒用户"
git -C $repo config user.email "sandbox@example.com"
git -C $repo config core.autocrlf false
git -C $repo config core.quotepath false

# ---------------------------------------------------------------- 1. 干净的起点
Write-Src '.gitattributes' @'
* text=auto eol=lf
'@

Write-Src '.gitignore' @'
__pycache__/
*.py[cod]
'@

Write-Src 'calc.py' @'
def add(a, b):
    return a + b


def sub(a, b):
    return a - b
'@

Write-Src 'test_calc.py' @'
import unittest

from calc import add, sub


class CalcTest(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)

    def test_sub(self):
        self.assertEqual(sub(5, 3), 2)


if __name__ == "__main__":
    unittest.main()
'@

Write-Src 'notes.txt' @'
随手记
======
- 先只做加减法
'@

Commit 'init: 加法和减法' '2026-10-20T09:12:00+08:00'

# ---------------------------------------------------------------- 2. 垃圾提交
Write-Src 'README.md' @'
# calc

一个用来练 git 的小模块。
'@
Commit 'update' '2026-10-20T15:40:00+08:00'

# ---------------------------------------------------------------- 3. 又一条垃圾提交
Write-Src 'notes.txt' @'
随手记
======
- 先只做加减法
- 除法要处理除零
'@
Commit '111' '2026-10-21T10:05:00+08:00'

# ---------------------------------------------------------------- 4. 真功能
Write-Src 'calc.py' @'
def add(a, b):
    return a + b


def sub(a, b):
    return a - b


def mul(a, b):
    return a * b
'@

Write-Src 'test_calc.py' @'
import unittest

from calc import add, mul, sub


class CalcTest(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)

    def test_sub(self):
        self.assertEqual(sub(5, 3), 2)

    def test_mul(self):
        self.assertEqual(mul(4, 3), 12)


if __name__ == "__main__":
    unittest.main()
'@
Commit '加乘法' '2026-10-22T11:30:00+08:00'

# ---------------------------------------------------------------- 5. 含糊提交
Write-Src 'calc.py' @'
def add(a, b):
    """两数相加。"""
    return a + b


def sub(a, b):
    return a - b


def mul(a, b):
    return a * b
'@
Commit 'fix' '2026-10-22T16:02:00+08:00'

# ---------------------------------------------------------------- 6. 埋雷（故意写错）
Write-Src 'calc.py' @'
def add(a, b):
    """两数相加。"""
    return a + b


def sub(a, b):
    return a - b


def mul(a, b):
    return a * b


def div(a, b):
    return a // b
'@

Write-Src 'test_calc.py' @'
import unittest

from calc import add, div, mul, sub


class CalcTest(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)

    def test_sub(self):
        self.assertEqual(sub(5, 3), 2)

    def test_mul(self):
        self.assertEqual(mul(4, 3), 12)

    def test_div(self):
        self.assertEqual(div(5, 2), 2.5)


if __name__ == "__main__":
    unittest.main()
'@
Commit '加除法' '2026-10-23T09:45:00+08:00'

# ---------------------------------------------------------------- 7. 噪声
Write-Src 'notes.txt' @'
随手记
======
- 先只做加减法
- 除法要处理除零
- TODO: 补文档
'@
Commit 'update' '2026-10-23T17:20:00+08:00'

# ---------------------------------------------------------------- 8. 类型注解
Write-Src 'calc.py' @'
"""四则运算（沙盒用，故意带一个 bug）。"""

from __future__ import annotations


def add(a: float, b: float) -> float:
    """两数相加。"""
    return a + b


def sub(a: float, b: float) -> float:
    return a - b


def mul(a: float, b: float) -> float:
    return a * b


def div(a: float, b: float) -> float:
    return a // b
'@
Commit '加类型注解' '2026-10-24T10:00:00+08:00'

# ---------------------------------------------------------------- 9. 分支：等 cherry-pick 的提交
git -C $repo checkout -q -b exp/formatting

Write-Src 'calc.py' @'
"""四则运算（沙盒用，故意带一个 bug）。"""

from __future__ import annotations


def add(a: float, b: float) -> float:
    """两数相加。"""
    return a + b


def sub(a: float, b: float) -> float:
    return a - b


def mul(a: float, b: float) -> float:
    return a * b


def div(a: float, b: float) -> float:
    return a // b


def fmt(value: float, digits: int = 2) -> str:
    """把数字格式化成固定小数位，给以后的报告用。"""
    return f"{value:.{digits}f}"
'@

Write-Src 'test_calc.py' @'
import unittest

from calc import add, div, fmt, mul, sub


class CalcTest(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)

    def test_sub(self):
        self.assertEqual(sub(5, 3), 2)

    def test_mul(self):
        self.assertEqual(mul(4, 3), 12)

    def test_div(self):
        self.assertEqual(div(5, 2), 2.5)

    def test_fmt(self):
        self.assertEqual(fmt(3.14159), "3.14")


if __name__ == "__main__":
    unittest.main()
'@
Commit '加数字格式化 fmt()' '2026-10-24T14:10:00+08:00'

git -C $repo checkout -q main

Write-Host ""
Write-Host "沙盒仓库已生成：$repo" -ForegroundColor Green
Write-Host ""
Push-Location $repo
git --no-pager log --oneline --graph --all --decorate
Write-Host ""
Write-Host "当前 main 上的测试状态（应该是红的，这是故意的）：" -ForegroundColor Cyan
cmd /c "python -m unittest -q 2>&1" | Select-Object -Last 6
Pop-Location
