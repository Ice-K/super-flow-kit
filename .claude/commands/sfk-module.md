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

## 创建模块时的 moduleId 推荐规则

当用户执行 `create <名称>` 且没有提供 `--id` 时，不要直接把原始参数传给脚本。你需要先根据模块名称语义，智能推荐一个英文 kebab-case `moduleId`，再显式传给脚本。

示例：

```text
用户管理 -> user-management
订单中心 -> order-center
支付模块 -> payment-module
权限管理 -> permission-management
```

推荐的 `moduleId` 必须只包含小写字母、数字和连字符，且不能以连字符开头或结尾。

- 如果用户已经提供 `--id`，不要改写，直接使用用户指定的值。
- 如果语义明确，执行时补上推荐 ID，例如：
  ```bash
  bash scripts/sfk-module.sh create 用户管理 --id user-management
  ```
- 如果语义不明确，不要胡乱生成；请提示用户补充 `--id`，例如：
  ```text
  /sfk-module create <名称> --id <moduleId>
  ```

根据上述规则确定最终参数后执行：

```bash
bash scripts/sfk-module.sh <最终参数>
```

其中 `<最终参数>` 必须是原始用户参数，或在缺少 `--id` 且语义明确时补充推荐 `--id` 后的参数。

行为要求：

- 创建模块后应自动切换为当前模块。
- 不要覆盖已有模块。
- 出错时说明原因和下一步建议。
