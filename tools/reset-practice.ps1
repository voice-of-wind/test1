<#
.SYNOPSIS
    把练习环境恢复到起点（代码回到最初版本，Git 历史清空）。

.DESCRIPTION
    做这几件事：
      1. 把 project\.git 移到 .backups\ 下（不删，万一你还想翻旧提交）
      2. 删掉 project 目录，用 tools\pristine-project.zip 里的原始代码重建
      3. 删掉 project-bob（"同事"那份）和 remotes（假的远程服务器）

    注意：你写在 project 里的代码改动**不会保留**——因为目的是"从头再练一遍"。
    真的想留，先自己复制出去。

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File tools\reset-practice.ps1
    powershell -ExecutionPolicy Bypass -File tools\reset-practice.ps1 -Force
#>
param([switch]$Force)

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$proj = Join-Path $root 'project'
$zip = Join-Path $PSScriptRoot 'pristine-project.zip'
$backupDir = Join-Path $root '.backups'

if (-not (Test-Path $zip)) { throw "找不到 $zip，没法恢复原始代码。" }

Write-Host "将要做这些事：" -ForegroundColor Cyan
Write-Host "  1. 备份 project\.git 到 .backups\（如果存在）"
Write-Host "  2. 用 pristine-project.zip 重建 project\（你写的代码改动会丢）"
Write-Host "  3. 删除 project-bob\ 和 remotes\"
Write-Host ""

if (-not $Force) {
    $answer = Read-Host "继续吗？输入 yes 再回车"
    if ($answer -ne 'yes') { Write-Host "取消了，什么都没动。"; return }
}

$gitDir = Join-Path $proj '.git'
if (Test-Path $gitDir) {
    New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $target = Join-Path $backupDir "project-git-$stamp"
    Move-Item $gitDir $target
    Write-Host "已备份 Git 历史 → $target" -ForegroundColor Green
}

if (Test-Path $proj) { Remove-Item -Recurse -Force $proj }
New-Item -ItemType Directory -Force -Path $proj | Out-Null
Expand-Archive -Path $zip -DestinationPath $proj -Force
Write-Host "project\ 已恢复成原始代码。" -ForegroundColor Green

foreach ($name in @('project-bob', 'remotes')) {
    $path = Join-Path $root $name
    if (Test-Path $path) {
        Remove-Item -Recurse -Force $path
        Write-Host "已删除 $name\"
    }
}

Write-Host ""
Write-Host "下一步：" -ForegroundColor Cyan
Write-Host "  cd project"
Write-Host "  python -m unittest discover -s tests -v      # 应该 12 个全过"
Write-Host "  git init -b main                              # 然后从 labs\lab01 重来"
