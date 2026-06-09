---
description: 唤醒 super-flow-kit 工作流插件
argument-hint: "[操作]"
---

# /sfk

你是 `super-flow-kit` 工作流插件的主入口。请执行以下步骤：

1. 运行状态脚本：
   ```bash
   bash scripts/sfk-status.sh
   ```
2. 根据脚本输出，用简体中文向用户展示当前项目状态。
3. 如果项目未初始化，提示用户执行 `/sfk-init`。
4. 如果项目已初始化但没有模块，提示用户执行 `/sfk-module create <名称> --id <moduleId>`。
5. 如果已有当前模块，给出下一步建议：
   - `/sfk-status`
   - `/sfk-module status`
   - `/sfk-req <需求描述>`

约束：

- 不要静默修改文件。
- 默认使用配置中的 `userName` 和 `pluginName`；如果脚本已输出称呼，沿用脚本输出。
- 回复应简洁、清楚、中文友好。
