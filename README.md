# Knowledge Wiki Skill

这是 `knowledge-wiki` Codex skill 的源码目录，用于维护 Obsidian 技术知识库。

## 规范来源

本 skill 采用单一规范源：`SKILL.md`。vault 内已有 `AGENTS.md` 可以作为普通历史文档保留，但不再参与知识库维护规则解析，也不覆盖 `SKILL.md` 中的流程、目录、字段或质量要求。

## 文件结构

- `SKILL.md`：唯一规范来源，包含核心工作流、目录规则、字段约定和验证闭环。
- `references/page-conventions.md`：页面模板和链接格式参考。

## 同步说明

当前运行版本安装在：

```text
/Users/liurui/.codex/skills/knowledge-wiki
```

修改本目录后，需要同步到安装目录，新的 Codex 线程或刷新技能列表后才会使用更新后的 skill。

本仓库只作为源码目录维护；同步到安装目录是独立步骤，本仓库内的修改不会自动写入安装目录。

## 开发后验证

修改源码后运行：

```bash
sh scripts/validate-skill.sh
```

该脚本只做源码结构和关键规范检查；如果发现安装目录存在但内容不同，只输出 warning，不阻断源码验证。
