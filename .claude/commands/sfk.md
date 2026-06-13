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
4. 如果项目已初始化但没有模块，提示用户执行 `/sfk-module create <名称>`；创建模块时 sfk 会在交互中推荐 `moduleId`，无法可靠推荐时再提示补充 `--id`。
5. 如果已有当前模块，优先沿用状态脚本输出的下一步建议；需要补充菜单时按阶段给出：
   - `/sfk-status`
   - `/sfk-help [命令名|关键词]`
   - `/sfk-module status`
   - `/sfk-req <需求描述>`
   - `/sfk-ui <UI 目标>`
   - `/sfk-design <系统/架构目标>`
   - `/sfk-dev <开发目标/实现范围>`
   - `/sfk-code-review <审查目标/审查范围>`
   - `/sfk-test <测试目标/测试范围>`
   - `/sfk-deploy <部署目标/上线范围>`
   - `/sfk-export module [moduleId] [--zip]`
   - `/sfk-export project [--zip]`
   - `/sfk-reset [current-module|project]`（高风险状态重置；第一次调用只展示影响范围，必须二次确认）

约束：

- 不要静默修改文件。
- 默认使用配置中的 `userName` 和 `pluginName`；如果脚本已输出称呼，沿用脚本输出。
- 回复应简洁、清楚、中文友好。
