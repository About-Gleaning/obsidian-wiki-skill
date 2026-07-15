#!/bin/sh
set -eu

ROOT_DIR=$(CDPATH= cd "$(dirname "$0")/.." && pwd)
INSTALL_DIR="/Users/liurui/.codex/skills/knowledge-wiki"

fail() {
  printf 'ERROR: %s\n' "$1" >&2
  exit 1
}

warn() {
  printf 'WARNING: %s\n' "$1" >&2
}

require_file() {
  file="$1"
  [ -f "$ROOT_DIR/$file" ] || fail "缺少文件：$file"
}

require_text() {
  file="$1"
  text="$2"
  if ! grep -Fq "$text" "$ROOT_DIR/$file"; then
    fail "$file 缺少关键规范：$text"
  fi
}

forbid_text() {
  file="$1"
  text="$2"
  if grep -Fq "$text" "$ROOT_DIR/$file"; then
    fail "$file 不应包含已废弃规范：$text"
  fi
}

require_file "SKILL.md"
require_file "README.md"
require_file "references/page-conventions.md"
require_file "scripts/raw_ingest.py"

require_text "SKILL.md" "唯一规范来源"
require_text "SKILL.md" "Obsidian CLI"
require_text "SKILL.md" "source of truth"
require_text "SKILL.md" "Ingest 硬闸门"
require_text "SKILL.md" "preflight"
require_text "SKILL.md" "baseline"
require_text "SKILL.md" "去重检查"
require_text "SKILL.md" "unresolved"
require_text "SKILL.md" "长原文"
require_text "SKILL.md" "Clippings 入库"
require_text "SKILL.md" "定时任务与手动触发使用完全相同的流程"
require_text "SKILL.md" "scripts/raw_ingest.py"
require_text "SKILL.md" "唯一例外"
require_text "SKILL.md" "完整 Markdown 快照"
require_text "SKILL.md" "obsidian vault=\"knowledge-agent\" move"
require_text "SKILL.md" "defuddle parse"
require_text "SKILL.md" "不允许退回到让 LLM 输出全文"
require_text "SKILL.md" "遇到失败立即停止"
require_text "SKILL.md" "Areas 闸门"
forbid_text "SKILL.md" "迁移-only"
forbid_text "SKILL.md" "迁移+总结"
forbid_text "SKILL.md" "未更新 area"
require_text "references/page-conventions.md" "极简模板"
require_text "references/page-conventions.md" "## Areas"
require_text "references/page-conventions.md" "以 SKILL.md 为准"
require_text "references/page-conventions.md" "defuddle parse"
require_text "references/page-conventions.md" "完整 Markdown 快照"
require_text "references/page-conventions.md" "## Area 页模板"
require_text "references/page-conventions.md" "  - area"
require_text "README.md" "sh scripts/validate-skill.sh"

python3 "$ROOT_DIR/scripts/raw_ingest.py" --help >/dev/null

if [ -d "$INSTALL_DIR" ]; then
  if [ -f "$INSTALL_DIR/SKILL.md" ] && ! cmp -s "$ROOT_DIR/SKILL.md" "$INSTALL_DIR/SKILL.md"; then
    warn "安装目录 SKILL.md 与源码不同步：$INSTALL_DIR"
  fi
  if [ -f "$INSTALL_DIR/references/page-conventions.md" ] && ! cmp -s "$ROOT_DIR/references/page-conventions.md" "$INSTALL_DIR/references/page-conventions.md"; then
    warn "安装目录 page-conventions.md 与源码不同步：$INSTALL_DIR"
  fi
  if [ ! -f "$INSTALL_DIR/scripts/raw_ingest.py" ]; then
    warn "安装目录缺少 raw_ingest.py：$INSTALL_DIR"
  elif ! cmp -s "$ROOT_DIR/scripts/raw_ingest.py" "$INSTALL_DIR/scripts/raw_ingest.py"; then
    warn "安装目录 raw_ingest.py 与源码不同步：$INSTALL_DIR"
  fi
fi

printf 'OK: knowledge-wiki skill 源码校验通过。\n'
