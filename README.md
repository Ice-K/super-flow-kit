# super-flow-kit

`super-flow-kit` 是一个面向 Claude Code 的结构化软件交付工作流插件，目标是帮助用户从需求分析到部署上线，按阶段沉淀项目上下文、产出物和工作流状态。

当前版本是 **v0.1 MVP**，重点实现最小可用闭环：

```text
初始化项目 → 创建模块 → 需求分析 → 保存产出物 → 查看状态看板
```

## 当前状态

v0.1 已实现：

- `/sfk` — 唤醒插件并展示当前状态。
- `/sfk-init` — 初始化 `.sfk/` 状态目录和 `docs/super-flow-kit/` 产出物目录。
- `/sfk-status` — 查看项目和当前模块工作流看板。
- `/sfk-module create/list/switch/status` — 管理功能模块，`create` 支持 `--id`。
- `/sfk-config` — 查看配置，并支持设置 `pluginName` 和 `userName`。
- `/sfk-req` — 进入需求分析流程，指导 Claude 单题澄清、总结、提供方案、生成草稿并等待用户确认。

v0.1 暂未实现：

- `/sfk-ui`
- `/sfk-design`
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

v0.1 只完整实现 **需求分析** 阶段。后续阶段已在规格和状态模型中预留。

## MVP 使用路径

在 Claude Code 中使用：

```text
/sfk-init
/sfk-module create 用户认证 --id user-auth
/sfk-config set pluginName flow
/sfk-config set userName 阿杰
/sfk
/sfk-status
/sfk-req 开发用户登录功能
```

`/sfk-req` 的推荐交互流程：

```text
单题推进澄清关键问题
→ 总结已确认信息
→ 基于总结提供 3–5 个方案
→ 用户选择、组合或自定义方案
→ 生成需求分析草稿
→ 用户再次确认
→ 标记 done / confirmed
```

## 项目结构

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
├── sfk.py
├── sfk-init.sh
├── sfk-status.sh
├── sfk-module.sh
└── sfk-config.sh

templates/
└── requirement.md

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
        └── yyyyMMddHHmmss-{moduleId}-需求分析.md
```

这些运行时状态默认被 `.gitignore` 忽略：

```gitignore
/.sfk/
/docs/super-flow-kit/
```

## 脚本级验证

本项目当前不需要安装 npm 依赖，也没有 build/lint/test 脚本。核心状态工具使用 Python 标准库实现。

可以运行以下命令进行脚本级验证：

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
