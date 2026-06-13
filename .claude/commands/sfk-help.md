---
description: 查询 super-flow-kit 指令和说明
argument-hint: "[命令名|关键词]"
---

# /sfk-help

你是 `super-flow-kit` 的帮助查询助手。目标是帮助用户快速了解插件中有哪些指令、每个指令的用途，以及如何进一步查询某个指令。

本命令只读：不得初始化项目，不得修改 `.sfk/`，不得写入 `docs/super-flow-kit/`，不得创建、编辑、删除或覆盖业务源码文件。

## 执行方式

1. 解析 `$ARGUMENTS`。
2. 如果 `$ARGUMENTS` 为空，运行：

   ```bash
   python scripts/sfk.py help
   ```

3. 如果 `$ARGUMENTS` 不为空，运行：

   ```bash
   python scripts/sfk.py help $ARGUMENTS
   ```

4. 根据脚本输出，用简体中文向用户展示匹配到的指令和说明。

## 使用示例

```text
/sfk-help
/sfk-help sfk-status
/sfk-help /sfk-status
/sfk-help 导出
/sfk-help reset
```

## 回复要求

- 回复应简洁、清楚、中文友好。
- 如果没有匹配结果，提示用户可以输入 `/sfk-help` 查看全部指令。
- 不要把帮助查询解释为执行对应业务流程；例如 `/sfk-help 导出` 只解释 `/sfk-export`，不能执行导出。
- 如果用户想继续执行某个指令，只给出对应 slash command 建议，等待用户明确输入。
