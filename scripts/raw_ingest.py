#!/usr/bin/env python3
"""将外部 Markdown 长原文稳定写入 knowledge-wiki 的 raw/articles/。

脚本只处理 vault 外部文件；Clippings 剪藏应由 agent 使用 Obsidian move 直接迁移。
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse


def die(message: str) -> None:
    print(json.dumps({"ok": False, "error": message}, ensure_ascii=False), file=sys.stderr)
    raise SystemExit(1)


def run_obsidian(vault: str, *args: str) -> str:
    command = ["obsidian", f"vault={vault}", *args]
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
    except FileNotFoundError:
        die("找不到 obsidian 命令，无法定位 vault。")
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        die(f"obsidian 命令失败：{' '.join(command)}\n{detail}")
    output = result.stdout.strip()
    if not output:
        die("obsidian 未返回 vault 路径，请确认 Obsidian 正在运行且目标 vault 已打开。")
    return output


def resolve_vault_root(vault: str, vault_path: str | None) -> Path:
    raw_path = vault_path or run_obsidian(vault, "vault", "info=path")
    root = Path(raw_path).expanduser().resolve()
    if not root.is_dir():
        die(f"vault 路径不存在或不是目录：{root}")
    return root


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        die(f"文件不是 UTF-8 Markdown：{path}")


def parse_frontmatter(content: str) -> dict[str, str]:
    if not content.startswith("---\n"):
        return {}
    end = content.find("\n---", 4)
    if end == -1:
        return {}
    data: dict[str, str] = {}
    for line in content[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and value:
            data[key] = value
    return data


def first_heading(content: str) -> str | None:
    for line in content.splitlines():
        match = re.match(r"^#\s+(.+?)\s*$", line)
        if match:
            return match.group(1).strip()
    return None


def pick_title(content: str, fallback: str, explicit: str | None) -> str:
    if explicit:
        return explicit.strip()
    meta = parse_frontmatter(content)
    for key in ("title", "标题"):
        if meta.get(key):
            return meta[key].strip()
    return first_heading(content) or fallback


def pick_source(content: str, explicit: str | None) -> str:
    if explicit:
        return explicit.strip()
    meta = parse_frontmatter(content)
    for key in ("source", "url", "URL", "original", "原文链接"):
        if meta.get(key):
            return meta[key].strip()
    for match in re.finditer(r"https?://[^\s)>\"']+", content):
        return match.group(0).rstrip(".,;")
    return "待验证"


def slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value[:80].strip("-")


def slug_from_source(source: str) -> str:
    parsed = urlparse(source)
    if parsed.scheme and parsed.netloc:
        parts = [parsed.netloc.replace("www.", "")]
        parts.extend(part for part in PurePosixPath(parsed.path).parts if part and part != "/")
        return slugify("-".join(parts))
    return slugify(source)


def make_slug(title: str, source: str, content: str, explicit: str | None) -> str:
    if explicit:
        slug = slugify(explicit)
    else:
        slug = slug_from_source(source)
        if not slug or slug == "待验证":
            slug = slugify(title)
    if not slug:
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()[:10]
        slug = f"article-{digest}"
    return slug


def yaml_scalar(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def build_raw_page(
    *,
    title: str,
    source: str,
    content: str,
    source_type: str,
    tool: str,
) -> str:
    today = dt.date.today().isoformat()
    return (
        "---\n"
        f"title: {yaml_scalar(title)}\n"
        "tags:\n"
        "  - raw/article\n"
        f"created: {today}\n"
        f"updated: {today}\n"
        "status: raw\n"
        f"source: {yaml_scalar(source)}\n"
        "---\n\n"
        f"# {title}\n\n"
        "## 获取方式\n\n"
        f"- 来源类型：{source_type}\n"
        f"- 获取工具：{tool}\n"
        f"- 访问日期：{today}\n"
        "- 保存内容：完整 Markdown 快照\n\n"
        "## 原文\n\n"
        f"{content.rstrip()}\n\n"
        "## 处理状态\n\n"
        "- 已入库到：待处理\n"
        "- 待处理：生成 wiki/sources 结构化总结并同步 index/log\n"
    )


def write_raw(
    *,
    vault_root: Path,
    title: str,
    source: str,
    content: str,
    slug: str,
    source_type: str,
    tool: str,
) -> tuple[str, Path]:
    raw_dir = vault_root / "raw" / "articles"
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / f"{slug}.md"
    if raw_path.exists():
        return "exists", raw_path
    raw_path.write_text(
        build_raw_page(
            title=title,
            source=source,
            content=content,
            source_type=source_type,
            tool=tool,
        ),
        encoding="utf-8",
    )
    return "created", raw_path


def relative_posix(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root).as_posix()


def ingest_file(args: argparse.Namespace) -> None:
    vault_root = resolve_vault_root(args.vault, args.vault_path)
    input_path = Path(args.input).expanduser().resolve()
    if not input_path.is_file():
        die(f"输入 Markdown 文件不存在：{input_path}")
    content = read_text(input_path)
    title = pick_title(content, input_path.stem, args.title)
    source = pick_source(content, args.source)
    slug = make_slug(title, source, content, args.slug)
    status, raw_path = write_raw(
        vault_root=vault_root,
        title=title,
        source=source,
        content=content,
        slug=slug,
        source_type=args.source_type,
        tool=args.tool,
    )
    print_result(vault_root, raw_path, status, title, source, slug)


def print_result(root: Path, raw_path: Path, status: str, title: str, source: str, slug: str) -> None:
    print(
        json.dumps(
            {
                "ok": True,
                "status": status,
                "raw_path": relative_posix(root, raw_path),
                "title": title,
                "source": source,
                "slug": slug,
            },
            ensure_ascii=False,
        )
    )


def add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--vault", default="knowledge-agent", help="Obsidian vault 名称")
    parser.add_argument("--vault-path", help=argparse.SUPPRESS)
    parser.add_argument("--title", help="覆盖自动识别的标题")
    parser.add_argument("--source", help="覆盖自动识别的来源 URL")
    parser.add_argument("--slug", help="指定 raw/articles 文件名 slug")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="将 vault 外部 Markdown 原文写入 raw/articles/")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    file_parser = subparsers.add_parser("file", help="从本地 Markdown 文件创建 raw")
    file_parser.add_argument("--input", required=True, help="本地 Markdown 文件路径")
    file_parser.add_argument("--source-type", default="URL", help="写入获取方式的来源类型")
    file_parser.add_argument("--tool", default="defuddle + scripts/raw_ingest.py", help="写入获取方式的获取工具")
    add_common(file_parser)
    file_parser.set_defaults(func=ingest_file)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
