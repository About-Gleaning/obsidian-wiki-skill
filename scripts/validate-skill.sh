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

require_file "SKILL.md"
require_file "README.md"
require_file "references/page-conventions.md"

require_text "SKILL.md" "唯一规范来源"
require_text "SKILL.md" "Obsidian CLI"
require_text "SKILL.md" "source of truth"
require_text "SKILL.md" "去重检查"
require_text "SKILL.md" "unresolved"
require_text "SKILL.md" "长原文"
require_text "SKILL.md" "安装目录"
require_text "references/page-conventions.md" "极简模板"
require_text "references/page-conventions.md" "## Areas"
require_text "references/page-conventions.md" "canonical URL"
require_text "README.md" "sh scripts/validate-skill.sh"

if [ -d "$INSTALL_DIR" ]; then
  if [ -f "$INSTALL_DIR/SKILL.md" ] && ! cmp -s "$ROOT_DIR/SKILL.md" "$INSTALL_DIR/SKILL.md"; then
    warn "安装目录 SKILL.md 与源码不同步：$INSTALL_DIR"
  fi
  if [ -f "$INSTALL_DIR/references/page-conventions.md" ] && ! cmp -s "$ROOT_DIR/references/page-conventions.md" "$INSTALL_DIR/references/page-conventions.md"; then
    warn "安装目录 page-conventions.md 与源码不同步：$INSTALL_DIR"
  fi
fi

printf 'OK: knowledge-wiki skill 源码校验通过。\n'
