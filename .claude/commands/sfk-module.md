---
description: 管理 super-flow-kit 模块
argument-hint: "create/list/switch/status ..."
---

# /sfk-module

管理当前项目中的功能模块。

支持：

```text
/sfk-module create <名称> [--id <moduleId>]
/sfk-module list
/sfk-module switch <moduleId 或 displayName>
/sfk-module status
```

执行：

```bash
bash scripts/sfk-module.sh $ARGUMENTS
```

行为要求：

- 创建模块时，推荐用户显式提供 `--id`，例如：
  ```text
  /sfk-module create 用户认证 --id user-auth
  ```
- `moduleId` 只能包含小写字母、数字和连字符，且不能以连字符开头或结尾。
- 创建模块后应自动切换为当前模块。
- 不要覆盖已有模块。
- 出错时说明原因和下一步建议。
