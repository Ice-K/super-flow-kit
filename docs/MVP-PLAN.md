# super-flow-kit v0.1 MVP 实现计划

## Context

当前仓库已从文档型项目推进到实现阶段：`super-flow-kit.md` 已更新为 v3.1 规格文档，明确了 v0.1 MVP 范围、命令规格、状态 schema、交互流程和验收路径。远程仓库地址：`https://github.com/Ice-K/super-flow-kit.git`。

目标是实现一个最小可用的 Claude Code 工作流插件，完成以下闭环：

```text
/sfk-init
/sfk-module create 用户认证 --id user-auth
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
```

## 实现步骤

1. 初始化本地 git 仓库并关联远程 origin。
2. 创建 `.claude/commands/`、`scripts/`、`templates/`、`docs/`。
3. 实现 `scripts/sfk.py`，提供状态读写、初始化、模块管理、配置管理和看板渲染能力。
4. 实现 shell wrapper。
5. 实现 slash command 文件。
6. 更新 `CLAUDE.md`。
7. 运行脚本级验证。

## `/sfk-req` 交互要求

1. 检查项目和当前模块状态。
2. 单题推进澄清关键问题。
3. 每题可单选、多选或自由输入，必须保留“其他，我自己说明”。
4. 澄清后总结。
5. 基于总结提供 3–5 个方案。
6. 用户确认方案后生成需求分析草稿。
7. 保存文档到 `docs/super-flow-kit/{moduleId}/...`。
8. 草稿状态写入：`status: in_progress`、`quality: draft`。
9. 用户再次确认后，更新为 `status: done`、`quality: confirmed`。

## 脚本级验证命令

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

## 不在本轮实现

- 完整 `/sfk-ui`、`/sfk-design`、`/sfk-dev`、`/sfk-test`、`/sfk-deploy` 流程。
- `/sfk-export`。
- `/sfk-reset`。
- `/sfk-code-review`。
- hook 自然语言唤醒完整动态匹配。
- 多人冲突自动合并。
- 远程 push。
