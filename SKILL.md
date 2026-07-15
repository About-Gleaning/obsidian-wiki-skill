---
name: knowledge-wiki
description: Use when maintaining an Obsidian-based personal technical knowledge wiki, especially for ingesting articles, papers, docs, Obsidian Web Clipper Clippings, source-reading notes, or conversation outputs into a persistent LLM Wiki; querying existing wiki notes; linting links, stale claims, orphan pages, and missing sources; or updating index/log pages in a knowledge-agent style vault.
---

# Knowledge Wiki

## 核心原则

这个 skill 用于维护 Obsidian 技术知识库。默认目标是 `knowledge-agent` vault；如果用户指定其他 vault，只切换 vault 名称，不读取该 vault 的本地 `AGENTS.md` 作为规范来源。

本 skill 的唯一规范来源是当前 `SKILL.md`；`README.md` 和 `references/` 只作为开发说明与按需加载的细节参考。若 `references/` 与当前文件存在冲突，以当前文件为准。

涉及 Obsidian vault 的读写时，必须使用 `obsidian` 命令。不要用普通 shell、`apply_patch`、脚本或编辑器直接写 vault 内 Markdown 文件，除非用户明确取消这个约束。

唯一例外：本 skill 自带的 `scripts/raw_ingest.py` 可以把 vault 外部 Markdown 文件写入 `raw/articles/`。这个例外只用于 URL 抓取、PDF 提取等已落地到临时文件的完整原文或完整 Markdown 快照，避免让 LLM 输出长原文；Clippings 剪藏、`wiki/`、`wiki/index.md` 和 `wiki/log.md` 仍必须通过 Obsidian CLI 操作。

所有内容默认使用中文维护，英文技术术语保留原文。内部链接使用 Obsidian wikilink，外部来源使用标准 Markdown 链接。

知识库分三类内容：`raw/` 是原始资料层，保存来源、访问时间、获取方式、完整原文或完整 Markdown 快照、附件链接和处理状态；`Clippings/` 是浏览器插件下载的未处理暂存区；`wiki/` 是 LLM 维护的知识层，保存总结、实体、概念、比较、综合和回答沉淀。

`raw/` 是 source of truth。除补充元数据、处理状态或附件链接外，不改写原文正文，也不在 `raw/` 维护长期总结。`wiki/` 只保存摘要、个人理解、交叉链接和长期结论。

`Clippings/` 默认不参与 lint 的结构问题判定。除非用户明确要求处理剪藏或将剪藏入库，否则不要把 `Clippings/` 下的孤立页、无出链页作为需要修复的问题。

## 开始前检查

1. 确认 Obsidian 正在运行，目标 vault 已打开。
2. 用 Obsidian CLI 做只读检查：
   ```bash
   obsidian vault="knowledge-agent" read path="wiki/index.md"
   ```
3. 如果 Obsidian 未运行、目标 vault 未打开或 CLI 无法连接，先按“Obsidian CLI 使用约定”请求非沙箱执行；仍失败则停止并说明阻塞原因。
4. 如果 `wiki/index.md` 或 `wiki/log.md` 不存在，默认不要自行初始化；只有用户明确要求初始化或本轮任务就是创建知识库结构时，才创建基础 index/log。
5. 按“Obsidian CLI 使用约定”执行命令；仍然不能绕过 Obsidian 直接写文件。
6. 如果目标 vault 不是 `knowledge-agent`，使用用户指定 vault 名称，并在本轮说明假设。

## Obsidian CLI 使用约定

- 命令名固定优先使用 `obsidian`，不是 `obsidian-cli`。只有用户环境明确没有 `obsidian` 且存在 `obsidian-cli` 时，才等价替换命令名。
- 参数使用 `key=value` 形式，目标 vault 参数放在命令后：`obsidian vault="knowledge-agent" read path="wiki/index.md"`。
- 文件定位优先使用 `path=`，路径是 vault 根目录下的相对路径，例如 `wiki/index.md`。只有需要按 Obsidian wikilink 名称解析时才使用 `file=`。
- 读文件用 `read`；创建或覆盖文件用 `create path="..." overwrite content="..."`；追加日志用 `append path="wiki/log.md" content="..."`。
- 搜索和检查使用内置命令：`search`、`unresolved`、`orphans`、`deadends`、`backlinks`、`links`。不要用普通 shell 直接扫描 vault 文件来替代 Obsidian 的链接解析。
- Obsidian CLI 需要连接正在运行的 Obsidian。若沙箱内命令返回空输出、`code -1` 或疑似 socket 连接失败，立即用同一条 `obsidian ...` 命令请求非沙箱执行；不要反复在沙箱内重试。
- 写入 vault 时必须通过 Obsidian CLI，并优先一次写完整内容。短页面可用 `content="..."`，多行 `content=` 使用 `\n` 转义，避免 heredoc、重定向或直接编辑 vault Markdown。
- 长原文、代码块密集内容、包含大量引号或反引号的 raw 快照，不要强行塞进 shell 参数，也不要让 LLM 输出完整原文。URL 原文必须先落地为 vault 外部临时文件，再用 `scripts/raw_ingest.py file` 写入 `raw/articles/`；无法落地为文件时停止并说明阻塞原因。Clippings 剪藏已经是 vault 内 Markdown 文件，必须用 Obsidian `move` 直接迁移到 `raw/articles/`。
- 覆盖或更新已有页面前，必须先 `read` 当前内容；只改本轮请求需要维护的段落，不得整页重写导致人工内容、历史记录或无关段落丢失。
- 在 shell 命令参数中搜索包含反引号的文本时，用单引号包裹 pattern，避免 zsh 把反引号当成命令替换。

## 工作流选择

除纯只读审阅本 skill 源码外，凡涉及 Obsidian vault 的任务都先执行“开始前检查”。如果检查失败，停止并说明阻塞原因，不降级为直接文件写入。

### Ingest 硬闸门

执行 ingest 时必须维护并逐项完成以下清单。最终回复前逐项核对，不允许跳过任何闸门。

```text
[ ] preflight：已读取 wiki/index.md 和 wiki/log.md
[ ] baseline：已记录 unresolved 基线
[ ] dedupe：已按 URL / 标题 / slug 去重
[ ] raw：已创建、复用或迁移 raw/articles/ 页面
[ ] source：已创建或更新 wiki/sources/ 页面
[ ] area：已更新至少一个 wiki/areas/ 页面
[ ] index：已同步 wiki/index.md
[ ] log：已追加 wiki/log.md 记录
[ ] postcheck：已确认本轮没有新增 unresolved
```

不得以“已经保存总结”“已经移动文件”“用户没特别要求 index/log”为完成标准。任何 ingest 都必须满足以上闸门。

### Ingest 来源

用户提供文章、论文、博客、文档、源码笔记或原始资料时：

1. 执行“开始前检查”，读取 `wiki/index.md`、`wiki/log.md`，并按 `wiki/index.md` 的 Areas 分组识别候选 `wiki/areas/` 页面；按需读取相关主题页、概念页或来源页。
2. 运行 `obsidian vault="knowledge-agent" unresolved verbose counts format=tsv` 建立断链基线，用于结束前判断本轮是否新增 unresolved。
3. 先按 URL、标题或 canonical URL 搜索 `raw/articles/` 与 `wiki/sources/` 中是否已有记录；已有记录时更新已有 raw/source，不重复创建同源页面。用户提供 URL 时最少执行以下去重检查：
   ```bash
   obsidian vault="knowledge-agent" search query="完整 URL 或 canonical URL"
   obsidian vault="knowledge-agent" search query="标题关键词"
   obsidian vault="knowledge-agent" search query="核心 slug"
   ```
4. 如果用户提供 URL，主动获取内容；普通网页优先使用 `defuddle parse <url> --md -o <tmp.md>` 提取 clean Markdown 到 agent 指定的临时文件。`defuddle -o` 失败、未生成文件或工具不可用时，停止并说明阻塞原因，不允许退回到让 LLM 输出全文。论文、PDF、GitHub 或官方文档按对应 skill/工具读取，但长原文仍应先落地为文件。
5. 用 `scripts/raw_ingest.py file --input <tmp.md> --source <url> --vault knowledge-agent` 创建或复用 `raw/articles/` 下的原文记录：标题、作者、链接、访问日期、获取工具、完整原文或完整 Markdown 快照、附件链接、处理状态。raw 创建后视为 source of truth，除补充元数据、处理状态或附件链接外不改写原文。
6. 创建或更新 `wiki/sources/` 下的结构化总结页。
7. 执行 Areas 闸门：必须更新至少一个相关 `wiki/areas/` 页面，写入本来源带来的长期结论、关联 source/concept/entity/comparison；如果没有合适 area，创建一个最小 `wiki/areas/` 页面，并同步 `wiki/index.md` 的 Areas 分组。
8. 更新相关 `wiki/concepts/`、`wiki/entities/` 和 `wiki/comparisons/` 页面；发现新来源挑战旧结论时，明确标注矛盾、证据和待验证项。
9. 更新 `wiki/index.md`，为新增或重要更新页面补一行摘要和来源信息。
10. 向 `wiki/log.md` 追加 `## [YYYY-MM-DD] ingest | 标题` 记录，并在“更新”中列出已更新的 `wiki/areas/...`。
11. 再次运行 `obsidian vault="knowledge-agent" unresolved verbose counts format=tsv` 并与基线对比；本轮新增断链必须修复或移除链接后才能结束。

URL ingest 的目标是主动阅读并入库，不要停留在“请用户自己提供内容”。`raw/` 是原始资料层，应保存可获取的完整原文或完整 Markdown 快照；`wiki/` 是知识层，只保存总结、概念、交叉链接和长期结论。保存第三方内容时要记录来源 URL、访问日期和获取方式，回答用户时不要复述大段原文。

如果 `wiki/sources/` 页面的“相关概念”使用 wikilink，该概念页必须已存在或在本轮创建。暂不创建概念页时，使用普通文本或单独写入“待建概念”，不要创建 unresolved 链接。

每次 ingest 的成功标准是：raw/source 已创建或更新，Areas 闸门已满足，相关 concept/entity/comparison 已按需同步，index/log 已同步，本轮新增 unresolved 为 0。Areas 闸门已满足是指已更新或创建 `wiki/areas/` 页面。弱成功标准如“已经保存了总结”不算完成。

默认优先一次 ingest 一个来源，便于用户检查摘要和强调重点。用户明确要求批处理时，可以批量 ingest，但必须在日志里记录批量范围和未深入处理的风险。

### Clippings 入库

用户要求处理 Obsidian Web Clipper、`Clippings/`、剪藏、定时任务或自动入库时：

1. 执行“开始前检查”，读取 `wiki/index.md`、`wiki/log.md`，并运行 `obsidian vault="knowledge-agent" unresolved verbose counts format=tsv` 建立断链基线。
2. 用 `obsidian vault="knowledge-agent" files folder="Clippings" ext=md` 获取待处理 Markdown。只处理 `Clippings/` 入口目录下的文件，不处理任何子目录。
3. 按路径字典序逐条处理，不并发。每条先用原文件名、URL 或核心关键词执行去重搜索；命中同源 raw/source 时停止当前文件并说明冲突，不覆盖、不自动改名。
4. 用 Obsidian CLI 直接迁移剪藏，保留原文件名、原始标题和完整正文：
   ```bash
   obsidian vault="knowledge-agent" move path="Clippings/文件.md" to="raw/articles/文件.md"
   ```
5. 不使用 `scripts/raw_ingest.py` 处理 Clippings，不读取剪藏全文后再由 LLM 输出原文，不重新生成标题，也不重新包装 raw 模板。

迁移后必须继续完成本条的完整 ingest：读取 `raw/articles/` 中的页面，创建或更新 `wiki/sources/` 下的结构化总结，按需更新相关 `wiki/concepts/`、`wiki/entities/`、`wiki/comparisons/`，并执行 Areas 闸门、index/log 同步和 unresolved postcheck。定时任务与手动触发使用完全相同的流程，不得将总结或知识层更新留待后续任务。

任一步失败时，遇到失败立即停止本轮批次，不继续后续剪藏；在回复中说明已完成迁移、失败点和下一步。

Clippings 成功入库后，`raw/articles/` 保存 Web Clipper 生成的原始 Markdown。Clippings 文件移动必须使用 Obsidian `move`，不要让 LLM 输出剪藏全文来创建 raw。

### Query 知识库

用户向知识库提问时：

1. 先读 `wiki/index.md` 定位候选页面。
2. 读取相关主题页、概念页、来源页。
3. 必要时搜索 raw/source 页面核对原始证据。
4. 回答时说明依据来自哪些 wiki 页面或外部来源。
5. 如果回答形成长期价值，按用户要求写回 `wiki/`，形式可以是新概念页、比较页、分析页、表格、Marp 页面、图表说明或 canvas 规划，并更新 `wiki/index.md` 与 `wiki/log.md`。
6. 写回 query 结果时，日志使用 `## [YYYY-MM-DD] query | 问题标题`。

### Lint 健康检查

用户要求检查知识库时：

1. 使用 Obsidian CLI 检查 unresolved、orphans、deadends、backlinks、search，并先记录 unresolved 基线。
2. 找出断链、孤立页、无出链页、重复概念、重要概念缺页、过时结论、互相矛盾的页面、无来源断言、缺失交叉链接和数据缺口。
3. 默认忽略 `Clippings/` 下的孤立页和无出链页，只报告数量或状态；用户明确要求处理剪藏时才把它纳入 ingest。
4. 本轮新增问题必须修复；历史问题只报告，不擅自大改。用户指定忽略范围时，不把该范围作为问题。
5. 给出下一步可调查的问题和建议寻找的新来源。
6. 用户只要求“检查”时默认保持只读，不追加日志；只有执行修复、用户要求记录或本轮产生知识库写入时，才追加 `## [YYYY-MM-DD] lint | 主题` 到 `wiki/log.md`。

## 页面规范

创建或更新 Obsidian Markdown 页面时，使用 frontmatter：

```yaml
---
title: 页面标题
tags:
  - category/tag
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: active
---
```

URL 来源字段统一使用 `source`。访问日期和获取工具优先写在正文的“获取方式”中，不在 frontmatter 混用 `source_url`、`accessed`、`extracted_by` 等同义字段。

更详细的页面模板和链接规则见 `references/page-conventions.md`。只有在需要创建或重写页面时才读取该参考文件。

## 质量要求

- 每一行改动都要能追溯到用户请求或维护协议。
- 不确定内容标注“待验证”，不要伪造来源。
- 小规模知识库优先维护 `wiki/index.md`，不要过早引入数据库、向量索引或脚本工具。
