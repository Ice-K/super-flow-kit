---
description: 配置 super-flow-kit 昵称和用户称呼
argument-hint: "[show|set pluginName <名称>|set userName <称呼>]"
---

# /sfk-config

配置当前项目的 super-flow-kit 行为。

v0.1 支持：

```text
/sfk-config
/sfk-config show
/sfk-config set pluginName flow
/sfk-config set userName 阿杰
```

执行：

```bash
bash scripts/sfk-config.sh $ARGUMENTS
```

行为要求：

- 无参数时等同于 `show`。
- v0.1 只允许修改 `pluginName` 和 `userName`。
- 修改后，后续回复应优先使用配置后的昵称和称呼。
- 如果项目未初始化，引导用户先执行 `/sfk-init`。
