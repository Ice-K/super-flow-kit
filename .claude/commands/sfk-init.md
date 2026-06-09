---
description: 初始化 super-flow-kit 项目状态
argument-hint: "[项目名称]"
---

# /sfk-init

请初始化当前项目的 `super-flow-kit` 工作流状态。

执行：

```bash
bash scripts/sfk-init.sh $ARGUMENTS
```

然后把脚本输出转述给用户。

行为要求：

- 如果项目尚未初始化，脚本会创建：
  - `.sfk/index.json`
  - `.sfk/modules/`
  - `docs/super-flow-kit/`
- 如果项目已初始化，不要覆盖已有状态。
- 初始化完成后，建议用户创建第一个模块：
  ```text
  /sfk-module create 用户认证 --id user-auth
  ```
