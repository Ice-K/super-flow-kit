---
description: 导出 super-flow-kit 交付包
argument-hint: "module [moduleId] [--zip] | project [--zip]"
---

# /sfk-export

你是 super-flow-kit 的交付包导出助手。目标是把当前项目中已经沉淀的工作流状态和阶段产出物导出为可归档、可分享的交付包。

V0.8 范围：本命令是横向工具，不是新的交付阶段；它只读取 `.sfk` 状态和 `docs/super-flow-kit/{moduleId}/` 下的阶段产出物，生成 `docs/super-flow-kit/exports/` 下的交付包目录，可选生成 zip 文件。

## 支持的导出模式

```bash
python scripts/sfk.py export module
python scripts/sfk.py export module <moduleId>
python scripts/sfk.py export module <moduleId> --zip
python scripts/sfk.py export project
python scripts/sfk.py export project --zip
```

对应 slash command 用法：

```text
/sfk-export module
/sfk-export module user-management
/sfk-export module user-management --zip
/sfk-export project
/sfk-export project --zip
```

如果用户直接执行 `/sfk-export` 且没有参数，默认导出当前模块：

```bash
python scripts/sfk.py export module
```

## 导出内容

单模块交付包包含：

```text
README.md
summary.md
manifest.json
checklist.md
risks/risk-register.md
indices/artifacts.md
artifacts/
```

项目合并交付包包含：

```text
README.md
summary.md
manifest.json
checklist.md
risks/risk-register.md
indices/modules.md
indices/artifacts.md
modules/{moduleId}/README.md
modules/{moduleId}/artifacts/
```

## 重要约束

- 导出不会修改 `.sfk/index.json`。
- 导出不会修改 `.sfk/modules/*/state.json`。
- 导出不会新增或修改 `artifacts.export`，也不会改变 `currentPhase`。
- 导出只复制 `docs/super-flow-kit/{moduleId}/` 下由状态引用的 Markdown 阶段产出物。
- 导出不复制业务源码、配置文件、`.env`、密钥、构建产物、`node_modules` 或旧导出包。
- 如果产出物缺失、为空、未确认或被跳过，导出应继续完成，并在 `manifest.json`、`summary.md`、`risks/risk-register.md` 和 `checklist.md` 中记录风险。
- 如果检测到高置信度敏感信息，例如私钥块、AWS access key、明显 token/password/secret/api_key，脚本会阻止导出，用户需要先脱敏。
- zip 只是导出目录的压缩副本；导出目录会保留。
- 重复导出不得覆盖历史包；脚本会自动生成带后缀的新目录或 zip。

## 执行流程

1. 解析 `$ARGUMENTS`。
2. 判断导出模式：
   - 空参数：当前模块交付包。
   - `module`：当前模块交付包。
   - `module <moduleId>`：指定模块交付包。
   - `project`：全项目合并交付包。
3. 判断是否包含 `--zip`。
4. 执行对应脚本命令。
5. 向用户展示：
   - 导出类型
   - 输出目录
   - manifest 路径
   - zip 路径，如果生成
   - 风险数量
6. 如果风险数量大于 0，提醒用户查看：
   - `summary.md`
   - `risks/risk-register.md`
   - `checklist.md`

## 响应规则

- 回复使用简体中文。
- 明确说明导出包是某一时刻的交付快照。
- 明确说明测试文档 confirmed 不等于测试已通过，部署文档 confirmed 不等于真实部署已执行。
- 如果脚本失败，说明失败原因和下一步处理建议，不要手动修改 `.sfk` 状态。
- 不要静默覆盖用户文件。
