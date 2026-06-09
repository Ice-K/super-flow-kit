---
description: 查看 super-flow-kit 工作流看板
argument-hint: ""
---

# /sfk-status

请展示当前项目和当前模块的 `super-flow-kit` 工作流看板。

执行：

```bash
bash scripts/sfk-status.sh
```

然后根据脚本输出向用户展示：

- 项目名称
- 当前模块
- 模块列表
- 当前模块六阶段状态
- 已有产出物路径
- 下一步建议

如果脚本提示未初始化，请引导用户执行 `/sfk-init`。
