# super-flow-kit

`super-flow-kit` 是一个面向 Claude Code 的结构化软件交付工作流插件，目标是帮助用户从需求分析到部署上线，按阶段沉淀项目上下文、产出物和工作流状态。

当前版本从 **v0.1 MVP** 继续演进，已覆盖需求分析、UI 设计和系统设计的窄范围闭环：

```text
初始化项目 → 创建模块 → 需求分析 → UI 设计 → 系统设计 → 保存产出物 → 查看状态看板
```

## 当前状态

v0.1 已实现：

- `/sfk` — 唤醒插件并展示当前状态。
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

暂未完整实现：

- `/sfk-dev`
- `/sfk-test`
- `/sfk-deploy`
- `/sfk-export`
- `/sfk-reset`
- `/sfk-code-review`
- 自然语言 hook 动态唤醒
- 多人冲突自动合并

## 核心工作流

完整产品规划包含六个阶段：

```text
需求分析 → UI 设计 → 系统设计 → 软件开发 → 功能测试 → 部署上线
```

v0.1 完整实现 **需求分析** 阶段；v0.2 以 `/sfk-ui` 形式实现 **UI 设计** 的窄范围切片；v0.3 以 `/sfk-design` 形式实现带脚本层兜底的 **系统设计** 闭环。后续开发、测试和部署阶段已在规格和状态模型中预留。

## MVP 使用路径

在 Claude Code 中使用：

```text
/sfk-init
/sfk-module create 用户管理
/sfk-config set pluginName flow
/sfk-config set userName 阿杰
/sfk
/sfk-status
/sfk-req 开发用户登录功能
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
├── sfk.py
├── sfk_tui.py
├── sfk-init.sh
├── sfk-status.sh
├── sfk-module.sh
└── sfk-config.sh

tests/
└── test_sfk_cli.py

templates/
├── requirement.md
├── ui-design.md
└── system-design.md

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
        └── yyyyMMddHHmmss-{moduleId}-系统设计.md
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
python scripts/sfk.py artifact impact requirement
python scripts/sfk.py artifact impact system_design
python scripts/sfk.py phase check ui_design
python scripts/sfk.py phase check system_design
python scripts/sfk.py artifact current system_design
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
- `/sfk-design` 草稿必须包含系统设计必备章节；确认时不得残留模板占位符，否则脚本会拒绝更新为 `done/confirmed`。
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
