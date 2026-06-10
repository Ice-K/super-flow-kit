# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 仓库现状

此仓库正在实现 `super-flow-kit` Claude Code 工作流插件。当前权威规格文档是 `super-flow-kit.md`，`super-flow-kit-v3.1.md` 是 v3.1 草稿副本。

v0.1 MVP 目标是实现最小闭环：初始化项目状态、创建/切换模块、查看看板、配置插件昵称和用户称呼，并通过 `/sfk-req` 引导生成需求分析文档。当前已完成 v0.2 UI 设计窄范围切片，并完成 v0.3 系统设计闭环：通过 `/sfk-design` 进入系统设计阶段，脚本层会强制需求硬依赖、必备章节和确认前占位符清理。

## 当前实现结构

```text
.claude/
└── commands/
    ├── sfk.md
    ├── sfk-init.md
    ├── sfk-status.md
    ├── sfk-module.md
    ├── sfk-config.md
    ├── sfk-req.md
    ├── sfk-ui.md
    └── sfk-design.md

scripts/
├── sfk.py              # 核心状态工具，使用 Python 标准库处理 JSON
├── sfk_tui.py          # 通用键盘选择能力，只负责交互选择，不读写 .sfk 状态
├── sfk-init.sh         # 初始化包装脚本
├── sfk-status.sh       # 看板包装脚本
├── sfk-module.sh       # 模块管理包装脚本
└── sfk-config.sh       # 配置管理包装脚本

tests/
└── test_sfk_cli.py     # Python 标准库回归测试

templates/
├── requirement.md      # 需求分析文档模板
├── ui-design.md        # UI 设计文档模板
└── system-design.md    # 系统设计文档模板

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

当前没有 package manifest、build 或 lint 脚本。v0.1 使用 Bash 命令入口 + Python 标准库脚本，并提供 Python 标准库回归测试。语义化 `moduleId` 推荐发生在 Claude slash command 交互层，Python 脚本只做确定性的状态管理、校验和兜底。

首选自动回归测试命令（使用临时目录，不污染当前仓库）：

```bash
python -m unittest discover -s tests -p "test_*.py"
```

手动 smoke 验证命令（会在当前目录生成 `.sfk/` 和 `docs/super-flow-kit/`）：

```bash
python scripts/sfk.py init
python scripts/sfk.py status
python scripts/sfk.py module create 用户管理 --id user-management
python scripts/sfk.py module list
python scripts/sfk.py module status
python scripts/sfk.py config show
python scripts/sfk.py config set pluginName flow
python scripts/sfk.py config set userName 阿杰
python scripts/sfk.py artifact current requirement
python scripts/sfk.py context discover --phase requirement
python scripts/sfk.py context discover --phase ui_design
python scripts/sfk.py context discover --phase system_design
python scripts/sfk.py artifact impact requirement
python scripts/sfk.py artifact impact system_design
python scripts/sfk.py phase check ui_design
python scripts/sfk.py phase check system_design
python scripts/sfk.py artifact current system_design
python scripts/sfk.py tui select --title "选择方案" --mode single --option mvp="MVP 方案" --option full="完整方案"
python scripts/sfk.py status
```

Slash command 手动验证路径：

```text
/sfk-init
/sfk-module create 用户管理
/sfk-config set pluginName flow
/sfk-config set userName 阿杰
/sfk
/sfk-status
/sfk-req 开发用户登录功能
/sfk-ui 设计用户登录界面
/sfk-design 设计用户管理系统架构
```

## v0.1 已实现能力

- `/sfk` — 唤醒插件并展示状态。
- `/sfk-init` — 初始化 `.sfk/` 和 `docs/super-flow-kit/`。
- `/sfk-status` — 查看项目和当前模块看板。
- `/sfk-module create/list/switch/status` — 管理模块，`create` 在 slash command 交互中可智能推荐 `moduleId`，`--id` 可用于显式指定。
- `/sfk-config` — 查看配置，支持设置 `pluginName` 和 `userName`。
- `/sfk-req` — 通过命令文档约束 Claude 执行需求分析流程：单题澄清 → 问题与选择汇总 → 总结确认（可修改/回退/重选/取消）→ 3–5 个方案 → 草稿 → 草稿确认（可继续修改/暂存/取消）→ 用户确认；已有主需求文档时默认合并更新并追加变更记录。
- `/sfk-ui` — v0.2 窄范围 UI 设计切片：基于需求产出物进入 UI 设计阶段，生成或更新 UI 设计草稿，并复用通用 artifact draft/confirm 状态机。
- `/sfk-design` — v0.3 系统设计闭环：基于已确认需求产出物进入系统设计阶段，可选结合 UI 设计和已有代码上下文，生成或更新系统设计草稿；脚本层强制需求硬依赖、系统设计必备章节和确认前模板占位符清理。
- `scripts/sfk.py artifact draft/confirm/current` — 为阶段命令提供草稿、确认和当前产出物读取能力；`draft/confirm` 会触发通用产出物文档检查。
- `scripts/sfk.py context discover --phase <phase>` — 只读项目上下文发现入口，用于区分全新项目、已有业务文档、已有代码和已有 UI 代码；系统设计阶段额外输出架构线索 evidence。
- `scripts/sfk.py artifact impact <phase>` — 只读下游影响分析入口，用于补充或变更需求/UI/系统设计时提示后续产出物复核风险。
- `scripts/sfk.py phase check <phase>` — 只读阶段依赖检查入口，供 `/sfk-ui` 等阶段命令判断硬/软依赖和风险提示；`artifact draft/confirm` 写入层会强制硬依赖。
- `scripts/sfk.py tui select` — 通用键盘选择底层能力，支持单选/多选、上下键移动、空格多选、Enter 确认；非交互环境返回 `non_interactive`，slash command 仍需保留文本/编号兜底。

## 暂未完整实现能力

- `/sfk-dev`、`/sfk-test`、`/sfk-deploy` 完整流程。
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
- `artifacts.requirement.files[-1]` 是当前主需求文档；重复执行 `/sfk-req` 默认更新该文件并追加变更记录，只有用户明确要求新版本时才新增需求文档。
- `scripts/sfk.py phase check <phase>` 提供只读阶段依赖检查；`ui_design` 对 `requirement` 是软依赖，可带假设继续，`system_design` 等后续阶段会按硬依赖阻塞；`artifact draft/confirm` 写入层也会强制硬依赖。
- `scripts/sfk.py context discover --phase <phase>` 提供只读项目上下文发现；REQ/UI/系统设计阶段应先识别全新项目、已有业务文档、已有代码或已有 UI 代码，再开始澄清；系统设计阶段还应读取 `evidence.architecture` 中的入口、配置、API、服务、数据、测试和部署线索。
- `scripts/sfk.py artifact impact <phase>` 提供只读下游影响分析；补充或变更需求/UI/系统设计时应先提示后续产出物复核风险，不自动降级下游状态。
- `/sfk-design` 草稿必须包含系统设计必备章节；确认前不得残留模板占位符，否则脚本拒绝写入 `done/confirmed`。
- `/sfk-req` 在写入草稿前必须展示所有问题与用户选择，并通过总结确认门禁；用户可修改某题、返回上一题、全部重选或取消。
- 草稿保存时必须保持 `status: in_progress` 和 `quality: draft`。
- 用户在草稿确认门禁中明确确认后，才能更新为 `status: done` 和 `quality: confirmed`。
- 所有阶段的产出物文档在新增、编辑、合并后，都必须通过 `scripts/sfk.py artifact draft/confirm` 触发通用文档检查；检查器应尽量自行修复标题编号、文档信息质量状态、确认后的变更记录负责人等可确定问题。

## 实现注意事项

- 状态文件路径必须使用相对项目根目录的路径，分隔符统一为 `/`。
- 不要写入本机绝对路径。
- JSON 读写应通过 `scripts/sfk.py` 的统一逻辑完成。
- 阶段产出物文档检查应作为通用兜底能力，不要只在需求阶段特判；后续 `/sfk-ui`、`/sfk-design`、`/sfk-dev` 等阶段也应复用同一 `artifact draft/confirm` 检查入口。
- 通用 TUI 能力必须保持无状态：只返回选择结果，不直接读写 `.sfk`。
- 不要静默覆盖用户文件或状态。
- 高风险操作必须二次确认。
- 远程仓库为 `https://github.com/Ice-K/super-flow-kit.git`；不要 push，除非用户明确要求。
