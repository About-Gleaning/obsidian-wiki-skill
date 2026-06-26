# 页面规范

本文件只提供页面模板、命名规则和链接格式。执行流程、Clippings 分支、URL 抓取失败策略和 ingest 成功标准以 SKILL.md 为准。

## 目录约定

- `raw/articles/`：原始资料层。保存链接、访问日期、获取方式、完整原文或完整 Markdown 快照和处理状态。
- `raw/assets/`：图片、附件、PDF 或网页下载资产。引用图片时优先使用本地附件。
- `wiki/sources/`：单个来源的结构化总结。
- `wiki/concepts/`：稳定概念页。
- `wiki/entities/`：人物、项目、工具、组织、论文等实体页。
- `wiki/comparisons/`：技术对比、方案权衡、综合分析。
- `wiki/areas/`：长期主题入口。
- `wiki/index.md`：内容导航。
- `wiki/log.md`：追加式时间线。

## 命名规则

- 文件名优先使用短横线 slug：小写英文、数字和连字符；中文标题可保留在 frontmatter `title` 与正文 H1。
- `raw/articles/` 与 `wiki/sources/` 的同一来源应使用同一核心 slug，例如 `raw/articles/example-rag-post.md` 与 `wiki/sources/example-rag-post.md`。
- URL 入库前先按 `source`、标题和核心 slug 搜索已有 raw/source 页面；命中同源页面时更新已有页面，不创建重复来源。
- 同名概念或实体必须在文件名中补充限定词，例如 `wiki/entities/openai-company.md` 与 `wiki/concepts/openai-api.md`。

## 来源页模板

```markdown
---
title: 来源标题
tags:
  - raw/article
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: raw
source: https://example.com
---

# 来源标题

## 获取方式

- 来源类型：URL / Obsidian Web Clipper / PDF / GitHub / 用户提供文本
- 获取工具：
- 访问日期：
- 保存内容：完整原文 / 完整 Markdown 快照 / PDF 文本提取 / 用户提供文本

## 原文

在这里保存可获取的完整原文或完整 Markdown 快照。不要在 `raw/` 中混入长期总结；总结写入 `wiki/sources/`。

## 处理状态

- 已入库到：
- 待处理：
```

raw 页面创建后视为 source of truth。后续只能补充元数据、处理状态或附件链接，不重写原文正文。

URL 入库使用 defuddle 等工具生成 vault 外部临时文件时，由 `scripts/raw_ingest.py` 写入 raw：

```bash
defuddle parse <url> --md -o /tmp/knowledge-wiki-ingest/<slug>.md
scripts/raw_ingest.py file --input /tmp/knowledge-wiki-ingest/<slug>.md --source <url> --vault knowledge-agent
```

更新已有页面前必须先读取当前内容，只改本轮需要维护的段落；不得用模板覆盖整页，避免丢失人工补充、历史上下文或无关内容。

## 概念页模板

```markdown
---
title: 概念名
tags:
  - concept
aliases:
  - English Name
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: active
---

# 概念名

## 定义

## 关键机制

## 适用场景

## 性能与安全取舍

## 相关页面
```

## Area 页模板

`wiki/areas/` 是长期主题入口，用于沉淀跨来源脉络，不保存单篇来源摘要。

```markdown
---
title: 主题名
tags:
  - area
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: active
---

# 主题名

## 覆盖范围

## 当前结论

## 关键来源

## 相关概念/实体/对比

## 待验证问题
```

## 比较页模板

```markdown
---
title: 对比主题
tags:
  - comparison
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: active
---

# 对比主题

## 结论摘要

## 对比维度

| 维度 | 方案 A | 方案 B | 备注 |
| --- | --- | --- | --- |

## 适用建议

## 证据来源

## 待验证问题
```

## 日志格式

```markdown
## [YYYY-MM-DD] ingest | 标题

- 操作：
- 新增：
- 更新：
- 决策：
- 后续：
```

日志标题必须保持 `## [YYYY-MM-DD] 类型 | 标题` 格式，类型使用 `ingest`、`query` 或 `lint`，便于之后用简单文本工具检索时间线。

## 索引格式

`wiki/index.md` 按 Areas、Concepts、Entities、Sources、Comparisons、Raw Sources 分组。每个条目至少包含链接和一句话摘要；来源页建议补充来源日期或 source count。

极简模板：

```markdown
# Knowledge Wiki Index

## Areas

- [[wiki/areas/example-area|示例主题]]：一句话说明覆盖范围。

## Concepts

- [[wiki/concepts/example-concept|示例概念]]：一句话定义或用途。

## Entities

- [[wiki/entities/example-entity|示例实体]]：人物、项目、工具、组织或论文说明。

## Sources

- [[wiki/sources/example-source|示例来源]]：来源日期或一句话摘要。

## Comparisons

- [[wiki/comparisons/example-comparison|示例对比]]：一句话说明对比问题。

## Raw Sources

- [[raw/articles/example-source|示例原文]]：原始资料入口和处理状态。
```

## 链接规则

- 内部链接优先使用显式路径：`[[wiki/concepts/rag|RAG]]`。
- 同名或别名容易产生 unresolved 时，不使用裸 `[[RAG]]`。
- 外部链接使用标准 Markdown：`[标题](https://example.com)`。
- 运行 unresolved 检查后，只修复本次变更引入的问题；已有历史问题单独报告。

## Lint 检查清单

- 未解析链接、孤立页、无出链页面。
- 被多次提及但没有页面的重要概念或实体。
- 新来源推翻旧结论但旧页面未更新。
- 来源页缺少 raw 链接、访问日期或处理状态。
- index 缺少新页面，log 缺少操作记录。
- 可通过下一次 web search、论文阅读或源码阅读补齐的数据缺口。
