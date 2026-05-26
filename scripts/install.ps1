<#
.SYNOPSIS
    把本仓库里的 skills 通过符号链接安装到 Codex / Claude Code 的默认搜索路径。

.DESCRIPTION
    遍历仓库根目录下的 codex/ 和 claude/ 子目录，把每个 skill 目录用
    SymbolicLink 的方式链接到 ~/.codex/skills/ 和 ~/.claude/skills/。

    需求：
    - Windows: 管理员权限运行 PowerShell，或者在系统设置里启用「开发者模式」
      （后者允许普通用户创建 symlink）。
    - macOS / Linux: 直接跑，不需要 sudo。

.PARAMETER DryRun
    只打印将要做什么，不实际改动文件系统。

.PARAMETER Force
    遇到目标位置已存在的同名目录时，不询问直接备份并替换。

.EXAMPLE
    pwsh -File scripts/install.ps1

.EXAMPLE
    pwsh -File scripts/install.ps1 -DryRun
#>

[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
$CodexSrc = Join-Path $RepoRoot 'codex'
$ClaudeSrc = Join-Path $RepoRoot 'claude'

if ($IsWindows -or $env:OS -eq 'Windows_NT') {
    $CodexDst = Join-Path $env:USERPROFILE '.codex\skills'
    $ClaudeDst = Join-Path $env:USERPROFILE '.claude\skills'
} else {
    $CodexDst = Join-Path $HOME '.codex/skills'
    $ClaudeDst = Join-Path $HOME '.claude/skills'
}

function Write-Step([string]$Msg) { Write-Host "[install] $Msg" -ForegroundColor Cyan }
function Write-Skip([string]$Msg) { Write-Host "[install] $Msg" -ForegroundColor DarkGray }
function Write-Ok([string]$Msg)   { Write-Host "[install] $Msg" -ForegroundColor Green }
function Write-Warn2([string]$Msg) { Write-Host "[install] $Msg" -ForegroundColor Yellow }

function Ensure-Dir([string]$Path) {
    if (-not (Test-Path $Path)) {
        if ($DryRun) {
            Write-Step "would create directory $Path"
        } else {
            New-Item -ItemType Directory -Path $Path -Force | Out-Null
            Write-Step "created directory $Path"
        }
    }
}

function Install-SkillDir {
    param(
        [string]$SrcRoot,
        [string]$DstRoot,
        [string]$Label
    )

    if (-not (Test-Path $SrcRoot)) {
        Write-Skip "$Label source $SrcRoot does not exist, skipping"
        return
    }

    Ensure-Dir $DstRoot

    $skills = Get-ChildItem -Path $SrcRoot -Directory | Where-Object {
        $_.Name -notin @('.git', 'node_modules') -and -not $_.Name.StartsWith('.')
    }

    foreach ($skill in $skills) {
        $src = $skill.FullName
        $dst = Join-Path $DstRoot $skill.Name

        # already correctly linked?
        if (Test-Path $dst) {
            $item = Get-Item $dst -Force
            if ($item.LinkType -eq 'SymbolicLink' -and $item.Target -eq $src) {
                Write-Skip "$Label/$($skill.Name) already linked, skipping"
                continue
            }

            if ($item.LinkType -eq 'SymbolicLink') {
                # symlink but pointing somewhere else - replace
                if ($DryRun) {
                    Write-Warn2 "would remove stale symlink $dst (was -> $($item.Target))"
                } else {
                    Remove-Item $dst -Force
                    Write-Warn2 "removed stale symlink $dst (was -> $($item.Target))"
                }
            } else {
                # real directory - back up
                $stamp = Get-Date -Format 'yyyyMMddHHmmss'
                $backup = "$dst.bak-$stamp"

                if ($DryRun) {
                    Write-Warn2 "would back up $dst -> $backup"
                } else {
                    $interactive = [Environment]::UserInteractive -and -not [Console]::IsInputRedirected
                    if (-not $Force -and $interactive) {
                        $ans = Read-Host "[install] $dst already exists as a real directory. Back up to $backup and replace? [y/N]"
                        if ($ans -notin @('y', 'Y')) {
                            Write-Skip "skipped $($skill.Name) at user request"
                            continue
                        }
                    } elseif (-not $Force) {
                        Write-Warn2 "skipped $($skill.Name): real dir at $dst, run with -Force to back up and replace"
                        continue
                    }
                    Move-Item -Path $dst -Destination $backup
                    Write-Warn2 "backed up $dst -> $backup"
                }
            }
        }

        if ($DryRun) {
            Write-Ok "would link $dst -> $src"
        } else {
            try {
                New-Item -ItemType SymbolicLink -Path $dst -Target $src | Out-Null
                Write-Ok "linked $dst -> $src"
            } catch {
                Write-Warn2 "failed to link $($skill.Name): $($_.Exception.Message)"
                Write-Warn2 "  hint: run as Administrator, or enable Windows Developer Mode"
            }
        }
    }
}

Write-Step "repo root: $RepoRoot"
Write-Step "dry-run:   $DryRun"
Write-Step ''

Install-SkillDir -SrcRoot $CodexSrc  -DstRoot $CodexDst  -Label 'codex'
Install-SkillDir -SrcRoot $ClaudeSrc -DstRoot $ClaudeDst -Label 'claude'

Write-Step ''
Write-Ok 'done.'
