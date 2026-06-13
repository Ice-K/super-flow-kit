# super-flow-kit

`super-flow-kit` 是一个面向 Claude Code 的结构化软件交付工作流插件，目标是帮助用户从需求分析到部署上线，按阶段沉淀项目上下文、产出物和工作流状态。

当前版本从 **v0.1 MVP** 继续演进，已覆盖需求分析、UI 设计、系统设计、开发计划、代码审查、功能测试、部署上线、交付包导出、状态级重置和自然语言 hook 动态唤醒能力：

```text
初始化项目 → 创建模块 → 需求分析 → UI 设计 → 系统设计 → 开发计划 → 代码审查 → 功能测试 → 部署上线 → 保存产出物 → 查看状态看板
```

## 当前状态

v0.1 已实现：

- `/sfk` — 唤醒插件并展示当前状态。
- `/sfk-help` — 查询 super-flow-kit 指令清单和指令说明，支持按命令名或关键词筛选。
- `/sfk-init` — 初始化 `.sfk/` 状态目录和 `docs/super-flow-kit/` 产出物目录。
- `/sfk-status` — 查看项目和当前模块工作流看板。
- `/sfk-module create/list/switch/status` — 管理功能模块；`create` 在 slash command 交互中可智能推荐 `moduleId`，`--id` 可显式覆盖。
- `/sfk-config` — 查看配置，并支持设置 `pluginName` 和 `userName`。
- `/sfk-req` — 进入需求分析流程，指导 Claude 单题澄清、展示问题与选择汇总、总结确认、提供方案、生成草稿并等待用户确认；脚本层会校验必备章节并在确认前阻塞模板占位符。
- `scripts/sfk.py phase check <phase>` — 只读阶段依赖检查，用于判断后续阶段是否可继续。
- `scripts/sfk.py tui select` — 通用键盘选择底层能力，支持单选/多选；交互终端中可用上下键、空格和 Enter，非交互环境会安全降级。

v0.2 窄范围切片已实现：

- `/sfk-ui` — 进入 UI 设计阶段，复用通用 artifact draft/confirm 状态机生成或更新 UI 设计文档。

v0.3 系统设计闭环已实现：

- `/sfk-design` — 进入系统设计阶段，基于已确认需求并可选结合 UI/代码上下文生成或更新系统设计文档。
- 脚本层会强制系统设计依赖已确认且可用的需求产出物；草稿必须包含系统设计必备章节，确认时不得残留模板占位符。

v0.3.1 系统设计补强已实现：

- 系统设计模板明确包含数据库设计和 API / 接口设计。
- 数据库设计覆盖概念模型、表结构、字段、关系、索引、唯一约束、生命周期和迁移策略；不涉及数据库时也必须显式说明。
- API / 接口设计覆盖接口清单、请求/响应、错误码、鉴权、分页/排序/过滤、幂等、限流和外部集成。

v0.4 基础开发阶段已实现：

- `/sfk-dev` — 进入软件开发阶段，基于已确认需求和系统设计生成或更新开发文档/开发计划。
- v0.4 只建立开发阶段产出物闭环，不自动修改业务代码，也不把开发文档确认等同于代码实现完成。

v0.4.1 源码实现二次确认门禁已实现：

- 开发文档 confirmed 后，源码实现仍需要单独通过 `/sfk-dev` 的 Gate C 二次确认。
- `scripts/sfk.py implementation approve development --summary ...` 会记录实现授权；授权前 `/sfk-dev` 不得修改业务源码。
- 实现授权只表示允许开始按开发文档修改源码，不代表源码已经实现完成。

v0.5 功能测试阶段已实现：

- `/sfk-test` — 进入功能测试阶段，基于已确认需求以及可选系统设计/开发文档生成或更新测试文档。
- 测试阶段硬依赖已确认且可用的需求产出物；系统设计和开发文档是软依赖，缺失时可以带假设继续但必须记录风险。
- 脚本层会校验测试文档必备章节，确认前不得残留模板占位符；测试文档 confirmed 不代表所有测试已执行通过，也不代表部署已获准。

v0.6 部署上线阶段已实现：

- `/sfk-deploy` — 进入部署上线阶段，生成或更新部署文档/上线计划。
- 部署阶段将测试作为软依赖处理，但 `/sfk-deploy` 前必须执行 `scripts/sfk.py deployment readiness`，检查所有模块是否存在已确认且可用的测试产出物，并向用户提示风险。
- 脚本层会校验部署文档必备章节，确认前不得残留模板占位符；部署文档 confirmed 不代表真实部署已经执行，也不代表生产环境已经变更。

v0.7 代码审查阶段已实现：

- `/sfk-code-review` — 进入代码审查阶段，在需求、系统设计、开发文档确认且源码实现授权批准后生成或更新代码审查文档。
- 代码审查文档记录 `pass`、`pass_with_risks`、`changes_required`、`blocked` 四类审查结果，以及 `Open`、`Fixed`、`Verified`、`Deferred`、`Accepted`、`Rejected` 六类问题状态。
- 代码审查不直接修改业务源码；发现需修复问题时回流 `/sfk-dev`，重新通过源码实现二次确认后再复审。

v0.8 交付包导出能力已实现：

- `/sfk-export` — 导出 super-flow-kit 交付包，支持单模块交付包和全项目合并交付包。
- `python scripts/sfk.py export module [moduleId] [--zip]` — 导出当前模块或指定模块的交付包，可选生成 zip。
- `python scripts/sfk.py export project [--zip]` — 汇总所有模块为项目级交付包，可选生成 zip。
- 导出写入 `docs/super-flow-kit/exports/`，不修改 `.sfk` 状态，不导出业务源码、配置或密钥。

v0.9 状态级重置能力已实现：

- `/sfk-reset` — 支持当前模块或全项目工作流状态重置。
- `python scripts/sfk.py reset impact [--scope current-module|project]` — 只读展示影响范围。
- `python scripts/sfk.py reset apply --confirm 确认重置` — 严格匹配确认语后才执行状态重置。
- 默认保留 `docs/super-flow-kit/` 产出物文档、导出包和业务源码，只解除 `.sfk` 当前状态引用并追加 history。

只读帮助查询已实现：

- `/sfk-help` — 查询插件指令和说明，不要求项目初始化。
- `python scripts/sfk.py help` — 列出全部指令。
- `python scripts/sfk.py help <命令名|关键词>` — 按命令名或关键词筛选指令说明。

自然语言 hook 动态唤醒已实现：

- `.claude/settings.json` — 配置 Claude Code `UserPromptSubmit` hook，调用 `bash scripts/sfk-wake.sh`。
- `scripts/sfk.py wake --prompt "..."` — 便于脚本级测试自然语言唤醒匹配。
- `scripts/sfk.py wake --hook-json` — 从 hook stdin 读取 prompt，命中后输出只读 `additionalContext`。
- hook 只做高置信提示，不执行 `/sfk-status` 或任何 `/sfk-*` 命令；普通业务语境如“审批工作流”“上传进度条”不会因通用词单独触发。

暂未完整实现：

- 多人冲突自动合并

## 核心工作流

完整产品规划包含七个阶段：

```text
需求分析 → UI 设计 → 系统设计 → 软件开发 → 代码审查 → 功能测试 → 部署上线
```

v0.1 完整实现 **需求分析** 阶段；v0.2 以 `/sfk-ui` 形式实现 **UI 设计** 的窄范围切片；v0.3 以 `/sfk-design` 形式实现带脚本层兜底的 **系统设计** 闭环；v0.3.1 补强系统设计中的 **数据库设计** 和 **API / 接口设计**；v0.4 以 `/sfk-dev` 启动 **软件开发计划** 产出物闭环；v0.4.1 增加源码实现二次确认；v0.5 以 `/sfk-test` 实现 **功能测试** 产出物闭环；v0.6 以 `/sfk-deploy` 实现 **部署上线** 产出物闭环；v0.7 以 `/sfk-code-review` 实现 **代码审查** 产出物闭环；v0.8 实现交付包导出；v0.9 实现状态级重置；自然语言 hook 动态唤醒作为只读增强能力提供高置信提示。

## 推荐使用路径

在 Claude Code 中使用：

```text
/sfk-init
/sfk-help
/sfk-help 导出
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
/sfk-export module user-management --zip
/sfk-export project --zip
/sfk-reset current-module
```

在 slash command 交互中，`/sfk-module create 用户管理` 会先由 Claude 根据语义推荐合法的 `moduleId`（如 `user-management`），再调用底层脚本；如无法可靠推荐，可使用 `--id` 显式指定。

`/sfk-req` 的推荐交互流程：

```text
单题推进澄清关键问题
→ 展示所有问题与用户选择
→ 总结已确认信息
→ 基于总结提供 3–5 个方案
→ 用户选择、组合或自定义方案
→ 总结确认：确认 / 修改某题 / 返回上一题 / 全部重选 / 取消
→ 生成或更新需求分析草稿
→ 草稿确认：确认完成 / 继续修改 / 返回总结 / 暂存草稿 / 取消
→ 标记 done / confirmed
```

第一次执行 `/sfk-req` 会创建当前模块的主需求分析文档。后续再次执行 `/sfk-req` 时，默认会把补充内容合并到这份主文档，并在“变更记录”中追加记录；只有用户明确要求新建版本或另存新文档时，才会创建新的时间戳文件。需求草稿必须包含必备章节；确认前不得残留模板占位符，`artifact draft/confirm requirement` 会输出 `qualityCheck`。

## 项目结构

```text
.claude/
├── settings.json       # Claude Code UserPromptSubmit hook 配置
└── commands/
    ├── sfk.md
    ├── sfk-help.md
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
    ├── sfk-deploy.md
    ├── sfk-export.md
    └── sfk-reset.md

scripts/
├── sfk.py
├── sfk_tui.py
├── sfk-init.sh
├── sfk-status.sh
├── sfk-module.sh
├── sfk-config.sh
├── sfk-reset.sh
└── sfk-wake.sh

tests/
└── test_sfk_cli.py

templates/
├── requirement.md
├── ui-design.md
├── system-design.md
├── development.md
├── code-review.md
├── testing.md
└── deployment.md

docs/
└── MVP-PLAN.md

super-flow-kit.md          # 当前权威规格文档
super-flow-kit-v3.1.md     # v3.1 草稿副本
CLAUDE.md                  # Claude Code 项目指导
```

运行时会生成：

```text
.sfk/
├── index.json
└── modules/
    └── {moduleId}/
        └── state.json

docs/
└── super-flow-kit/
    └── {moduleId}/
        ├── yyyyMMddHHmmss-{moduleId}-需求分析.md
        ├── yyyyMMddHHmmss-{moduleId}-UI设计.md
        ├── yyyyMMddHHmmss-{moduleId}-系统设计.md
        ├── yyyyMMddHHmmss-{moduleId}-开发文档.md
        ├── yyyyMMddHHmmss-{moduleId}-代码审查.md
        ├── yyyyMMddHHmmss-{moduleId}-测试文档.md
        └── yyyyMMddHHmmss-{moduleId}-部署文档.md
```

这些运行时状态默认被 `.gitignore` 忽略：

```gitignore
/.sfk/
/docs/super-flow-kit/
```

## 脚本级验证

本项目当前不需要安装 npm 依赖，也没有 build/lint 脚本。核心状态工具使用 Python 标准库实现，回归测试同样只依赖 Python 标准库。

首选运行自动回归测试；测试会在临时目录中创建 `.sfk/` 和 `docs/super-flow-kit/`，不会污染当前仓库工作区：

```bash
python -m unittest discover -s tests -p "test_*.py"
```

也可以运行以下命令进行手动脚本级验证。注意：直接运行 `python scripts/sfk.py module create ...` 时没有 Claude 语义推荐能力，中文名称建议显式提供 `--id`；这些手动命令会在当前目录生成运行时状态。

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
python scripts/sfk.py export module
python scripts/sfk.py export module user-management --zip
python scripts/sfk.py export project
python scripts/sfk.py export project --zip
python scripts/sfk.py reset impact
python scripts/sfk.py reset apply --confirm 确认重置
python scripts/sfk.py wake --prompt "sfk 在吗"
python scripts/sfk.py wake --prompt "帮我做需求分析"
python scripts/sfk.py wake --prompt "项目中的审批工作流需要加一段说明"
python scripts/sfk.py tui select --title "选择方案" --mode single --option mvp="MVP 方案" --option full="完整方案"
python scripts/sfk.py status
```

验证完成后，如不希望保留本地运行状态，可以删除：

```bash
rm -rf .sfk docs/super-flow-kit
```

## 状态模型

`super-flow-kit` 使用“全局索引 + 模块独立状态”的混合模型：

```text
.sfk/index.json
.sfk/modules/{moduleId}/state.json
```

核心状态规则：

- 阶段状态：`pending`、`in_progress`、`blocked`、`done`
- 产出物质量：`draft`、`confirmed`
- 草稿保存后：`status = in_progress`，`quality = draft`
- 用户明确确认后：`status = done`，`quality = confirmed`
- `artifacts.requirement.files[-1]` 是当前主需求文档；重复执行 `/sfk-req` 默认更新该文件并追加变更记录。
- `/sfk-req` 草稿必须包含需求分析必备章节；确认时不得残留模板占位符，否则脚本会拒绝更新为 `done/confirmed`。
- `scripts/sfk.py phase check <phase>` 提供只读阶段依赖检查；`ui_design` 对 `requirement` 是软依赖，可带假设继续，`system_design` 等后续阶段会按硬依赖阻塞；`artifact draft/confirm` 写入层也会强制硬依赖。
- `scripts/sfk.py context discover --phase <phase>` 提供只读上下文发现，用于区分全新项目、已有业务文档、已有代码和已有 UI 代码；系统设计阶段额外输出 `evidence.architecture` 架构线索。
- `scripts/sfk.py artifact impact <phase>` 提供只读下游影响分析，用于补充或变更需求/UI/系统设计时提示后续产出物复核风险。
- `/sfk-design` 草稿必须包含系统设计必备章节，尤其是数据库设计和 API / 接口设计；确认时不得残留模板占位符，否则脚本会拒绝更新为 `done/confirmed`。
- `/sfk-dev` 草稿必须包含开发文档必备章节；确认时不得残留模板占位符。v0.4 的 `/sfk-dev` 只确认开发计划产出物，不代表业务代码已经实现。
- `/sfk-dev` 源码实现前必须通过 `scripts/sfk.py implementation approve development --summary ...` 记录二次确认；`implementationApproval.status = approved` 只表示允许开始实现，不表示实现完成。
- `/sfk-code-review` 草稿必须包含代码审查必备章节；确认时不得残留模板占位符，审查结果只能是 `pass`、`pass_with_risks`、`changes_required` 或 `blocked`。
- `/sfk-code-review` 硬依赖已确认且可用的需求、系统设计和开发文档，并要求 `implementationApproval` 已批准且未过期；`scripts/sfk.py code-review readiness` 提供只读准入检查。
- `/sfk-code-review` 只确认代码审查文档，不代表问题已修复，也不代表测试已通过；发现需修复问题时回流 `/sfk-dev`，源码修改仍需二次确认。
- `/sfk-test` 草稿必须包含测试文档必备章节；确认时不得残留模板占位符。需求是硬依赖，系统设计和开发文档是软依赖，可带假设继续但必须记录依据不足。
- `/sfk-test` 只确认测试文档，不代表所有测试已执行通过，也不代表部署已获准。
- `/sfk-deploy` 草稿必须包含部署文档必备章节；确认时不得残留模板占位符。测试在部署阶段作为软依赖，但必须通过 `scripts/sfk.py deployment readiness` 检查所有模块是否有已确认且可用的测试产出物，并向用户提示风险。
- `/sfk-deploy` 只确认部署文档，不代表真实部署已经执行，也不代表生产环境已经变更。
- `/sfk-export` 是横向导出工具，不新增阶段状态，不写入 `.sfk` 状态；导出包只包含工作流交付文档、索引、风险清单、检查清单和 manifest，不包含业务源码或密钥。
- `/sfk-reset` 是高风险状态重置工具，必须先通过 `scripts/sfk.py reset impact` 展示影响范围，再由用户单独输入完全一致的 `确认重置` 后才能执行 `reset apply`；默认不删除 `docs/super-flow-kit/` 产出物文档、导出包或业务源码。
- `scripts/sfk.py wake` 和 `scripts/sfk-wake.sh` 是自然语言 hook 动态唤醒能力，只读取 prompt 和 `.sfk/index.json` 中的 `globalConfig`，命中时向 Claude 注入只读提示上下文；不会执行 `/sfk-status`、不会创建或修改 `.sfk`、不会执行重置。
- `/sfk-req` 在写入草稿前会展示所有问题与用户选择，并提供确认、修改、回退、重选和取消分支。
- `scripts/sfk.py tui select` 是无状态的通用交互选择能力；slash command 仍保留文本/编号选择作为兜底。

## 规格文档

当前权威规格文档：

```text
super-flow-kit.md
```

MVP 实现计划：

```text
docs/MVP-PLAN.md
```

## 开发约束

- 优先使用项目相对路径。
- 状态文件中的路径统一使用 `/`。
- 不写入本机绝对路径。
- JSON 读写统一通过 `scripts/sfk.py` 处理。
- 不依赖 `jq` 或 npm 包。
- 不静默覆盖用户文件。
- 高风险操作必须二次确认。

## License

本项目许可证见 [LICENSE](LICENSE)。
