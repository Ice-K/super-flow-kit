# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 仓库现状

此仓库正在实现 `super-flow-kit` Claude Code 工作流插件。当前权威规格文档是 `super-flow-kit.md`，`super-flow-kit-v3.1.md` 是 v3.1 草稿副本。

v0.1 MVP 目标是实现最小闭环：初始化项目状态、创建/切换模块、查看看板、配置插件昵称和用户称呼，并通过 `/sfk-req` 引导生成需求分析文档。

## 当前实现结构

```text
.claude/
└── commands/
    ├── sfk.md
    ├── sfk-init.md
    ├── sfk-status.md
    ├── sfk-module.md
    ├── sfk-config.md
    └── sfk-req.md

scripts/
├── sfk.py              # 核心状态工具，使用 Python 标准库处理 JSON
├── sfk-init.sh         # 初始化包装脚本
├── sfk-status.sh       # 看板包装脚本
├── sfk-module.sh       # 模块管理包装脚本
└── sfk-config.sh       # 配置管理包装脚本

templates/
└── requirement.md      # 需求分析文档模板

docs/
└── MVP-PLAN.md         # v0.1 MVP 实现计划
```

运行时会在使用插件的项目中生成：

```text
.sfk/
├── index.json
└── modules/
    └── {moduleId}/
        └── state.json

docs/
└── super-flow-kit/
    └── {moduleId}/
```

## 常用验证命令

当前没有 package manifest、build、lint 或测试套件。v0.1 使用 Bash 命令入口 + Python 标准库脚本。

脚本级验证命令：

```bash
python scripts/sfk.py init
python scripts/sfk.py status
python scripts/sfk.py module create 用户认证 --id user-auth
python scripts/sfk.py module list
python scripts/sfk.py module status
python scripts/sfk.py config show
python scripts/sfk.py config set pluginName flow
python scripts/sfk.py config set userName 阿杰
python scripts/sfk.py status
```

Slash command 手动验证路径：

```text
/sfk-init
/sfk-module create 用户认证 --id user-auth
/sfk-config set pluginName flow
/sfk-config set userName 阿杰
/sfk
/sfk-status
/sfk-req 开发用户登录功能
```

## v0.1 已实现能力

- `/sfk` — 唤醒插件并展示状态。
- `/sfk-init` — 初始化 `.sfk/` 和 `docs/super-flow-kit/`。
- `/sfk-status` — 查看项目和当前模块看板。
- `/sfk-module create/list/switch/status` — 管理模块，`create` 支持 `--id`。
- `/sfk-config` — 查看配置，支持设置 `pluginName` 和 `userName`。
- `/sfk-req` — 通过命令文档约束 Claude 执行需求分析流程：单题澄清 → 总结 → 3–5 个方案 → 草稿 → 用户确认。
- `scripts/sfk.py artifact draft/confirm` — 为 `/sfk-req` 提供草稿和确认状态更新能力。

## v0.1 暂未实现能力

- `/sfk-ui`、`/sfk-design`、`/sfk-dev`、`/sfk-test`、`/sfk-deploy` 完整流程。
- `/sfk-export`。
- `/sfk-reset`。
- `/sfk-code-review`。
- 自然语言 hook 动态唤醒。
- 多人冲突自动合并。

## 产品架构要点

`super-flow-kit` 计划作为 Claude Code 工作流插件，帮助用户按结构化软件交付流程推进项目：

```text
需求分析 → UI 设计 → 系统设计 → 软件开发 → 功能测试 → 部署上线
```

核心交互模式是“产出物驱动 + 苏格拉底式引导”：每个环节先单题澄清关键问题，再基于澄清结果提供 3–5 个方案，引导用户确认，生成结构化产出物，并建议下一步。

## 工作流与状态模型

状态采用“全局索引 + 模块独立状态”的混合模型：

- `.sfk/index.json` 保存项目元数据、`currentModule`、模块注册表和 `globalConfig`。
- `.sfk/modules/{moduleId}/state.json` 保存模块负责人/协作者、当前阶段、模块依赖、产出物状态、文件引用、版本、时间戳和历史记录。
- 阶段状态流转为 `pending → in_progress → done`；依赖缺失时可进入 `blocked`。
- 产出物质量使用 `draft` / `confirmed`。
- 草稿保存时必须保持 `status: in_progress` 和 `quality: draft`。
- 用户明确确认后，才能更新为 `status: done` 和 `quality: confirmed`。

## 实现注意事项

- 状态文件路径必须使用相对项目根目录的路径，分隔符统一为 `/`。
- 不要写入本机绝对路径。
- JSON 读写应通过 `scripts/sfk.py` 的统一逻辑完成。
- 不要静默覆盖用户文件或状态。
- 高风险操作必须二次确认。
- 远程仓库为 `https://github.com/Ice-K/super-flow-kit.git`；不要 push，除非用户明确要求。
