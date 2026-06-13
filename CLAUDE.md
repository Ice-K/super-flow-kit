# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 仓库现状

此仓库正在实现 `super-flow-kit` Claude Code 工作流插件。当前权威规格文档是 `super-flow-kit.md`，`super-flow-kit-v3.1.md` 是 v3.1 草稿副本。

v0.1 MVP 目标是实现最小闭环：初始化项目状态、创建/切换模块、查看看板、配置插件昵称和用户称呼，并通过 `/sfk-req` 引导生成需求分析文档。当前需求分析已具备脚本层质量门禁；v0.2 UI 设计窄范围切片已完成；v0.3 系统设计闭环已完成；v0.3.1 补强系统设计中的 API 设计和数据库设计；v0.4 已启动 `/sfk-dev` 基础开发阶段闭环，生成开发文档/开发计划；v0.4.1 增加源码实现二次确认门禁，开发文档确认不等于授权修改源码；v0.5 已实现 `/sfk-test` 功能测试阶段闭环，生成测试文档并增加脚本层质量门禁；v0.6 已实现 `/sfk-deploy` 部署上线阶段闭环，生成部署文档并在部署前检查所有模块测试产出物状态；v0.7 已实现 `/sfk-code-review` 代码审查阶段闭环，在实现授权后生成代码审查文档并记录问题处理回流策略。

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
    ├── sfk-design.md
    ├── sfk-dev.md
    ├── sfk-code-review.md
    ├── sfk-test.md
    └── sfk-deploy.md

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
├── system-design.md    # 系统设计文档模板
├── development.md      # 开发文档模板
├── code-review.md      # 代码审查文档模板
├── testing.md          # 测试文档模板
└── deployment.md       # 部署文档模板

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
python scripts/sfk.py context discover --phase development
python scripts/sfk.py context discover --phase code_review
python scripts/sfk.py context discover --phase testing
python scripts/sfk.py context discover --phase deployment
python scripts/sfk.py artifact impact requirement
python scripts/sfk.py artifact impact system_design
python scripts/sfk.py artifact impact development
python scripts/sfk.py artifact impact code_review
python scripts/sfk.py artifact impact testing
python scripts/sfk.py phase check ui_design
python scripts/sfk.py phase check system_design
python scripts/sfk.py phase check development
python scripts/sfk.py phase check code_review
python scripts/sfk.py phase check testing
python scripts/sfk.py phase check deployment
python scripts/sfk.py deployment readiness
python scripts/sfk.py artifact current system_design
python scripts/sfk.py artifact current development
python scripts/sfk.py artifact current code_review
python scripts/sfk.py artifact current testing
python scripts/sfk.py artifact current deployment
python scripts/sfk.py implementation current development
python scripts/sfk.py implementation approve development --summary "按已确认开发文档开始实现"
python scripts/sfk.py code-review readiness
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
/sfk-dev 制定用户管理开发计划
/sfk-code-review 审查用户管理实现
/sfk-test 制定用户管理测试计划
/sfk-deploy 制定用户管理部署计划
```

## 当前已实现能力

- `/sfk` — 唤醒插件并展示状态。
- `/sfk-init` — 初始化 `.sfk/` 和 `docs/super-flow-kit/`。
- `/sfk-status` — 查看项目和当前模块看板。
- `/sfk-module create/list/switch/status` — 管理模块，`create` 在 slash command 交互中可智能推荐 `moduleId`，`--id` 可用于显式指定。
- `/sfk-config` — 查看配置，支持设置 `pluginName` 和 `userName`。
- `/sfk-req` — 通过命令文档约束 Claude 执行需求分析流程：单题澄清 → 问题与选择汇总 → 总结确认（可修改/回退/重选/取消）→ 3–5 个方案 → 草稿 → 草稿确认（可继续修改/暂存/取消）→ 用户确认；已有主需求文档时默认合并更新并追加变更记录；脚本层会校验需求必备章节并在确认前阻塞模板占位符。
- `/sfk-ui` — v0.2 窄范围 UI 设计切片：基于需求产出物进入 UI 设计阶段，生成或更新 UI 设计草稿，并复用通用 artifact draft/confirm 状态机。
- `/sfk-design` — v0.3 系统设计闭环：基于已确认需求产出物进入系统设计阶段，可选结合 UI 设计和已有代码上下文，生成或更新系统设计草稿；脚本层强制需求硬依赖、系统设计必备章节和确认前模板占位符清理。
- v0.3.1 系统设计补强 — 系统设计模板和质量门禁明确要求数据库设计和 API / 接口设计；数据库设计覆盖概念模型、表结构、字段、关系、索引、唯一约束、生命周期和迁移策略，API 设计覆盖接口清单、请求/响应、错误码、鉴权、分页、幂等、限流和外部集成。
- `/sfk-dev` — v0.4 基础开发阶段闭环：基于已确认需求和系统设计生成或更新开发文档/开发计划，复用通用 artifact draft/confirm 状态机；本阶段不自动修改业务代码，也不将开发文档确认等同于代码实现完成。
- v0.4.1 源码实现二次确认 — `/sfk-dev` 在开发文档 confirmed 后必须通过 Gate C 和 `scripts/sfk.py implementation approve development --summary ...` 记录实现授权；Gate B 只确认开发文档，未通过实现授权前不得创建、编辑、删除、移动或覆盖业务源码文件。
- `/sfk-code-review` — v0.7 代码审查阶段闭环：在需求、系统设计、开发文档 confirmed 且源码实现授权 approved 后，生成或更新代码审查文档；记录 `pass` / `pass_with_risks` / `changes_required` / `blocked` 审查结果和 `Open` / `Fixed` / `Verified` / `Deferred` / `Accepted` / `Rejected` 问题状态；发现需修复问题时回流 `/sfk-dev`，不在代码审查阶段直接修改业务源码。
- `/sfk-test` — v0.5 功能测试阶段闭环：基于已确认需求以及可选系统设计/开发文档生成或更新测试文档，复用通用 artifact draft/confirm 状态机；脚本层强制需求硬依赖，系统设计、开发文档和代码审查作为软依赖提示风险，测试文档确认前会阻塞模板占位符。
- `/sfk-deploy` — v0.6 部署上线阶段闭环：生成或更新部署文档/上线计划，复用通用 artifact draft/confirm 状态机；测试作为部署软依赖，但命令流程必须通过 `scripts/sfk.py deployment readiness` 检查所有模块测试产出物是否已确认且可用，并向用户提示风险。
- `scripts/sfk.py deployment readiness` — 只读全模块部署准入检查，扫描所有模块的 testing 产出物状态、质量和文件可用性；该检查只证明测试产出物已确认且可用，不代表所有功能实际测试通过。
- `scripts/sfk.py code-review readiness` — 只读当前模块代码审查准入检查，汇总需求/系统设计/开发文档硬依赖和开发实现授权状态；该检查只证明可以生成代码审查产出物，不代表源码已通过审查。
- `scripts/sfk.py artifact draft/confirm/current` — 为阶段命令提供草稿、确认和当前产出物读取能力；`draft/confirm` 会触发通用产出物文档检查。
- `scripts/sfk.py context discover --phase <phase>` — 只读项目上下文发现入口，用于区分全新项目、已有业务文档、已有代码和已有 UI 代码；系统设计阶段额外输出架构线索 evidence。
- `scripts/sfk.py artifact impact <phase>` — 只读下游影响分析入口，用于补充或变更需求/UI/系统设计时提示后续产出物复核风险。
- `scripts/sfk.py phase check <phase>` — 只读阶段依赖检查入口，供 `/sfk-ui` 等阶段命令判断硬/软依赖和风险提示；`artifact draft/confirm` 写入层会强制硬依赖。
- `scripts/sfk.py tui select` — 通用键盘选择底层能力，支持单选/多选、上下键移动、空格多选、Enter 确认；非交互环境返回 `non_interactive`，slash command 仍需保留文本/编号兜底。

## 暂未完整实现能力

- `/sfk-export`。
- `/sfk-reset`。
- 自然语言 hook 动态唤醒。
- 多人冲突自动合并。

## 产品架构要点

`super-flow-kit` 计划作为 Claude Code 工作流插件，帮助用户按结构化软件交付流程推进项目：

```text
需求分析 → UI 设计 → 系统设计 → 软件开发 → 代码审查 → 功能测试 → 部署上线
```

核心交互模式是“产出物驱动 + 苏格拉底式引导”：每个环节先单题澄清关键问题，再基于澄清结果提供 3–5 个方案，引导用户确认，生成结构化产出物，并建议下一步。

## 工作流与状态模型

状态采用“全局索引 + 模块独立状态”的混合模型：

- `.sfk/index.json` 保存项目元数据、`currentModule`、模块注册表和 `globalConfig`。
- `.sfk/modules/{moduleId}/state.json` 保存模块负责人/协作者、当前阶段、模块依赖、产出物状态、文件引用、版本、时间戳和历史记录。
- 阶段状态流转为 `pending → in_progress → done`；依赖缺失时可进入 `blocked`。
- 产出物质量使用 `draft` / `confirmed`。
- `artifacts.requirement.files[-1]` 是当前主需求文档；重复执行 `/sfk-req` 默认更新该文件并追加变更记录，只有用户明确要求新版本时才新增需求文档。
- `/sfk-req` 草稿必须包含需求分析必备章节；确认前不得残留模板占位符，否则脚本拒绝写入 `done/confirmed`。
- `scripts/sfk.py phase check <phase>` 提供只读阶段依赖检查；`ui_design` 对 `requirement` 是软依赖，可带假设继续，`system_design` 等后续阶段会按硬依赖阻塞；`artifact draft/confirm` 写入层也会强制硬依赖。
- `scripts/sfk.py context discover --phase <phase>` 提供只读项目上下文发现；REQ/UI/系统设计阶段应先识别全新项目、已有业务文档、已有代码或已有 UI 代码，再开始澄清；系统设计阶段还应读取 `evidence.architecture` 中的入口、配置、API、服务、数据、测试和部署线索。
- `scripts/sfk.py artifact impact <phase>` 提供只读下游影响分析；补充或变更需求/UI/系统设计时应先提示后续产出物复核风险，不自动降级下游状态。
- `/sfk-design` 草稿必须包含系统设计必备章节，尤其是数据库设计和 API / 接口设计；确认前不得残留模板占位符，否则脚本拒绝写入 `done/confirmed`。
- `/sfk-test` 草稿必须包含测试文档必备章节；需求分析是硬依赖，系统设计、开发文档和代码审查是软依赖，可带假设继续但必须在文档中记录风险和依据不足；确认前不得残留模板占位符，否则脚本拒绝写入 `done/confirmed`。
- `/sfk-code-review` 草稿必须包含代码审查必备章节；需求分析、系统设计和开发文档是硬依赖，源码实现授权必须已批准且未过期；确认前不得残留模板占位符，审查结果必须是 `pass`、`pass_with_risks`、`changes_required` 或 `blocked`，问题状态必须是 `Open`、`Fixed`、`Verified`、`Deferred`、`Accepted` 或 `Rejected`。
- `/sfk-code-review` confirmed 只表示代码审查文档已确认，不代表问题已修复，也不代表测试已经执行通过；需要修复时必须回到 `/sfk-dev`，重新通过源码实现二次确认后再复审。
- `/sfk-test` confirmed 只表示测试文档已确认，不代表所有测试已经执行通过，也不代表部署已经获准。
- `/sfk-deploy` 草稿必须包含部署文档必备章节；测试在部署阶段是软依赖，但 `/sfk-deploy` 必须先执行 `scripts/sfk.py deployment readiness` 检查所有模块是否存在已确认且可用的测试产出物，并在部署文档中记录未就绪模块风险；确认前不得残留模板占位符，否则脚本拒绝写入 `done/confirmed`。
- `/sfk-deploy` confirmed 只表示部署文档已确认，不代表真实部署已经执行，也不代表生产环境已经变更。
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
