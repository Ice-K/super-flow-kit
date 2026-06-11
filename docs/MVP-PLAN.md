# super-flow-kit 迭代记录与近期计划

## Context

本文件最初记录 `super-flow-kit` v0.1 MVP 实现计划；随着 v0.2 UI 设计、v0.3 系统设计和 v0.4 开发阶段切片推进，现在同时作为迭代记录与近期计划。`super-flow-kit.md` 仍是权威规格文档，远程仓库地址：`https://github.com/Ice-K/super-flow-kit.git`。

目标是实现一个最小可用的 Claude Code 工作流插件，完成以下闭环：

```text
/sfk-init
/sfk-module create 用户管理
/sfk-req 开发用户登录功能
/sfk-status
```

## 推荐实现方式

采用 **Bash 命令入口 + Python 处理 JSON**：

- Bash 脚本负责命令入口、参数转发、调用 Python。
- Python 标准库负责 JSON 读写、目录创建、slug 校验、状态渲染。
- 不依赖 `jq`、npm 包或额外构建链路。
- 状态文件中的路径统一使用 `/`，兼容 Windows + bash 的 Claude Code 场景。

## 关键文件

### Claude Code slash commands

```text
.claude/commands/sfk.md
.claude/commands/sfk-init.md
.claude/commands/sfk-status.md
.claude/commands/sfk-module.md
.claude/commands/sfk-config.md
.claude/commands/sfk-req.md
.claude/commands/sfk-ui.md
.claude/commands/sfk-design.md
.claude/commands/sfk-dev.md
```

### 脚本

```text
scripts/sfk.py
scripts/sfk-init.sh
scripts/sfk-status.sh
scripts/sfk-module.sh
scripts/sfk-config.sh
```

### 模板

```text
templates/requirement.md
templates/ui-design.md
templates/system-design.md
templates/development.md
```

### 测试

```text
tests/
└── test_sfk_cli.py      # Python 标准库回归测试
```

## 实现步骤

1. 初始化本地 git 仓库并关联远程 origin。
2. 创建 `.claude/commands/`、`scripts/`、`templates/`、`docs/`。
3. 实现 `scripts/sfk.py`，提供状态读写、初始化、模块管理、配置管理和看板渲染能力。
4. 实现 shell wrapper。
5. 实现 slash command 文件。
6. 更新 `CLAUDE.md`。
7. 新增 Python 标准库回归测试，覆盖 MVP 状态机、artifact 流转、安全边界和 TUI 非交互降级。
8. 运行脚本级验证。

## `/sfk-req` 交互要求

1. 检查项目和当前模块状态。
2. 单题推进澄清关键问题。
3. 每题可单选、多选或自由输入；交互控件已有 Type something / 自定义输入能力，不额外添加自定义说明选项。
4. 澄清后总结。
5. 基于总结提供 3–5 个方案。
6. 用户确认方案后生成或更新需求分析草稿。
7. 如果当前模块没有需求文档，创建新的时间戳文档；如果已有主需求文档，默认合并更新该文档。
8. 保存文档到 `docs/super-flow-kit/{moduleId}/...`，后续补充需求必须追加“变更记录”。
9. 草稿状态写入：`status: in_progress`、`quality: draft`。
10. 用户再次确认后，更新为 `status: done`、`quality: confirmed`。
11. 每次新增、编辑或合并产出物文档后，必须触发通用文档检查；检查器应自行修复标题编号、文档信息质量状态、确认后的变更记录负责人等可确定问题，并输出检查结果。

## 脚本级验证命令

首选运行自动回归测试；测试使用临时项目目录，不会污染当前仓库工作区：

```bash
python -m unittest discover -s tests -p "test_*.py"
```

也可以运行以下手动 smoke 命令。注意：这些命令会在当前目录生成 `.sfk/` 和 `docs/super-flow-kit/` 运行时状态。

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
python scripts/sfk.py artifact draft requirement docs/super-flow-kit/user-management/<需求文档>.md
python scripts/sfk.py artifact confirm requirement
python scripts/sfk.py status
```

## 后续开发记录

- v0.1 MVP 后新增 Python 标准库回归测试，覆盖 MVP 状态机、artifact 流转、安全边界和 TUI 非交互降级。
- v0.2 窄范围切片开始实现 `/sfk-ui`：复用通用 `artifact draft/confirm/current` 状态机进入 UI 设计阶段，并新增只读 `python scripts/sfk.py phase check <phase>` 阶段依赖检查。
- REQ/UI 阶段增强上下文发现和影响分析：新增只读 `python scripts/sfk.py context discover --phase <phase>` 和 `python scripts/sfk.py artifact impact <phase>`，用于先识别全新/已有项目，再提示下游产出物复核风险。

- v0.3 系统设计闭环实现 `/sfk-design`：基于已确认需求产出物进入系统设计阶段，可选结合 UI 设计和现有代码上下文，并复用通用 `artifact draft/confirm/current` 状态机；脚本层强制需求硬依赖、系统设计必备章节和确认前模板占位符清理。
- v0.3.1 系统设计补强：将 API 设计和数据库设计作为系统设计必备内容，模板覆盖表结构、字段、关系、索引、迁移、接口清单、请求/响应、错误码、鉴权、分页、幂等、限流和外部集成。
- v0.4 `/sfk-dev` 基础开发阶段计划：基于已确认需求和系统设计生成开发文档/开发计划，复用通用 `artifact draft/confirm/current` 状态机；本阶段不自动修改业务代码，不将开发文档确认等同于代码实现完成。
- v0.4.1 源码实现二次确认门禁：开发文档 confirmed 后仍需通过 `scripts/sfk.py implementation approve development --summary ...` 记录实现授权；授权前不得修改业务源码，授权也不代表实现完成。
- REQ 阶段补齐脚本层质量门禁：`artifact draft/confirm requirement` 会检查必备章节和模板占位符，输出 `qualityCheck`，确认前不得残留模板占位符。

## 不在本轮实现

- 完整 `/sfk-test`、`/sfk-deploy` 流程。
- 自动修改业务代码并验证真实实现完成的 `/sfk-dev` 增强流程。
- `/sfk-export`。
- `/sfk-reset`。
- `/sfk-code-review`。
- hook 自然语言唤醒完整动态匹配。
- 多人冲突自动合并。
- 远程 push。
