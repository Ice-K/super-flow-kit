# super-flow-kit 插件需求与实现规格文档 v3.1

## 0. 文档说明

### 0.1 文档定位

本文档是 `super-flow-kit` 的产品需求与实现规格合一文档，是后续设计、实现、测试和迭代插件时的主要依据。

`super-flow-kit` 计划作为 Claude Code 工作流插件，帮助用户把一个软件项目从想法推进到可交付结果。它不只提供命令集合，还提供一套结构化协作流程：通过阶段引导、模块管理、状态记录和产出物沉淀，让用户和 Claude 可以围绕同一套项目上下文持续工作。

本文档同时回答两类问题：

1. **产品要做什么**：插件的目标用户、核心工作流、交互风格和功能边界。
2. **实现要怎么做**：插件文件结构、命令行为、状态 schema、产出物规则、依赖检测、错误处理和 MVP 验收标准。

后续如果文档内容与实现代码发生冲突，应优先修正文档或代码，使两者重新保持一致。MVP 实现阶段以本文档的 v0.1 范围为准，避免功能范围失控。

### 0.2 目标读者

本文档的主要读者是：

1. **项目作者本人**：用于明确产品边界、实现优先级和后续迭代方向。
2. **Claude / Claude Code**：用于在后续实现插件时快速理解需求、生成代码、补充测试和维护文档。

次要读者是未来可能参与维护的开发者。文档应尽量做到：即使读者没有参与前期讨论，也能看懂插件要解决什么问题、MVP 要实现什么、每个命令应该产生什么效果。

本文档不是最终用户手册。面向普通插件用户的安装与使用说明，应在插件实现后整理到 `README.md` 或单独的用户文档中。

### 0.3 当前版本目标

v3.1 的目标是把 v3.0 中较完整但偏产品草案的内容，收敛为一份可以直接指导 MVP 实现的规格文档。

本版本重点完成以下事情：

1. 明确 v0.1 MVP 做什么、不做什么。
2. 明确 Claude Code 插件的基础文件结构和命令组织方式。
3. 明确核心命令的输入、前置条件、执行动作、状态变更、输出示例和错误处理。
4. 明确 `.sfk/` 状态目录和 `docs/super-flow-kit/` 产出物目录的职责。
5. 明确模块、阶段、产出物、草稿、用户确认和依赖检测等核心规则。
6. 保留中文友好、轻量拟人化的交互体验，例如“小主，sfk 在呢～”，但实现规格本身保持清晰、可执行、可验收。

v3.1 完成后，下一步应进入 v0.1 MVP 实现，而不是继续无限扩展规格。

### 0.4 术语约定

| 术语                 | 说明                                                                                |
| -------------------- | ----------------------------------------------------------------------------------- |
| `super-flow-kit`     | 插件正式名称。                                                                      |
| `sfk`                | 插件默认唤醒昵称，也是主要命令前缀。                                                |
| 小主                 | 默认用户称呼，可通过配置修改。                                                      |
| 项目                 | 用户当前正在 Claude Code 中工作的代码仓库或文档目录。                               |
| 模块                 | 项目中的一个相对独立功能单元，例如“用户认证”“支付模块”。                            |
| `moduleId`           | 模块的内部 ID，用于目录名、状态索引和命令参数，必须适合文件路径，例如 `user-auth`。 |
| `displayName`        | 模块展示名称，用于对用户显示，例如 `用户认证`。                                     |
| 阶段                 | 软件交付流程中的一个环节，例如需求分析、UI 设计、系统设计。                         |
| 产出物               | 每个阶段生成的结构化 Markdown 文档，例如需求分析文档。                              |
| 草稿 / `draft`       | AI 基于已有上下文生成但尚未由用户确认的产出物质量状态。                             |
| 已确认 / `confirmed` | 用户明确认可后的产出物质量状态。                                                    |
| 硬依赖               | 进入某阶段前必须满足的依赖；缺失时默认阻止继续，除非用户显式选择跳过。              |
| 软依赖               | 建议具备但不强制的依赖；缺失时只提示风险。                                          |
| 当前模块             | 命令默认作用的模块，记录在 `.sfk/index.json` 的 `currentModule` 字段中。            |
| 状态文件             | `.sfk/index.json` 和 `.sfk/modules/{moduleId}/state.json`。                         |

---

## 1. 产品定位与核心理念

### 1.1 产品定位

`super-flow-kit` 是面向 Claude Code 的结构化软件交付工作流插件。它的目标不是替代用户做决策，而是帮助用户和 Claude 按清晰的阶段共同推进项目：先澄清需求，再设计界面和系统，再实现、测试和部署。

插件的核心价值是：

1. **降低启动成本**：用户只需要用 `/sfk` 或自然语言唤醒插件，就可以看到当前项目状态和下一步建议。
2. **减少上下文丢失**：通过 `.sfk/` 状态文件记录当前模块、阶段进度、产出物路径和历史记录。
3. **沉淀项目资产**：每个阶段都生成 Markdown 产出物，保存到 `docs/super-flow-kit/{moduleId}/`，方便复盘、修改和继续协作。
4. **支持渐进式交付**：用户可以只从一个模块、一个阶段开始，不需要一次性完成完整流程。
5. **保持用户主导**：关键产出物需要用户确认，Claude 负责引导、整理、补全和执行。

### 1.2 核心工作流

完整工作流包含六个阶段：

```text
需求分析 → UI 设计 → 系统设计 → 软件开发 → 功能测试 → 部署上线
```

各阶段职责如下：

| 阶段     | 阶段 ID         | 核心目标                                         | 主要产出物         |
| -------- | --------------- | ------------------------------------------------ | ------------------ |
| 需求分析 | `requirement`   | 澄清业务目标、用户场景、功能范围和验收标准。     | 需求分析文档       |
| UI 设计  | `ui_design`     | 设计页面结构、交互流程、视觉风格和组件清单。     | UI 设计文档        |
| 系统设计 | `system_design` | 明确技术架构、数据模型、接口设计和关键技术选型。 | 系统设计文档       |
| 软件开发 | `development`   | 根据已确认需求和设计实现功能代码。               | 功能代码、开发文档 |
| 功能测试 | `testing`       | 设计并执行测试，验证功能是否满足验收标准。       | 测试用例、测试报告 |
| 部署上线 | `deployment`    | 规划部署、监控、回滚和上线操作。                 | 部署文档、运维说明 |

v0.1 MVP 只完整实现“需求分析”阶段，其余阶段先保留状态字段、命令占位和文档模板预留，后续版本逐步实现。

### 1.3 核心交互原则

`super-flow-kit` 的交互应遵循以下原则：

| 原则           | 要求                                                               |
| -------------- | ------------------------------------------------------------------ |
| 苏格拉底式引导 | 当需求不明确时，先提问澄清，不直接替用户做不可逆决策。             |
| 多方案选择     | 对重要决策提供 3–5 个可选方案，并允许用户自由输入其他方案。        |
| 产出物驱动     | 每个阶段都应生成可保存、可查看、可修改、可确认的 Markdown 产出物。 |
| 用户确认优先   | 进入下一阶段前，应让用户确认当前阶段产出物是否可作为后续依据。     |
| 灵活衔接       | 支持从任意阶段开始，但要检测依赖并提示风险。                       |
| 模块化管理     | 支持按功能模块拆分状态和产出物，降低复杂项目中的上下文混乱。       |
| 中文友好       | 默认使用简体中文交流，保留轻量亲切风格，但不能影响信息清晰度。     |
| 可恢复         | 中断后应能通过状态文件恢复当前模块、当前阶段和已生成产出物。       |

推荐语气示例：

```text
嗨！小主，sfk 在呢～
我先看一下当前模块和工作流状态，然后给你几个下一步选项。
```

不推荐过度拟人化或过度卖萌。交互风格应服务于推进项目，而不是喧宾夺主。

### 1.4 产出物驱动机制

插件的核心不是“聊天记录”，而是“可持续使用的项目产出物”。因此每个阶段完成时，都应至少产生一个 Markdown 文档，并记录到模块状态文件中。

产出物驱动机制包括：

1. **生成**：阶段执行过程中，Claude 根据用户输入和上下文生成结构化 Markdown 文档。
2. **保存**：文档保存到 `docs/super-flow-kit/{moduleId}/`。
3. **登记**：文档路径、版本、质量状态、更新时间、负责人等信息写入 `.sfk/modules/{moduleId}/state.json`。
4. **确认**：用户确认后，产出物质量状态从 `draft` 变为 `confirmed`，阶段状态可进入 `done`。
5. **复用**：后续阶段依赖前序阶段产出物，而不是依赖聊天上下文。
6. **修改**：用户可以后续编辑产出物；插件应能在状态看板中提示产出物位置和当前状态。

MVP 阶段优先保证“需求分析文档”的完整闭环：提问澄清 → 生成文档 → 保存文件 → 更新状态 → 引导确认 → 看板可见。

---

## 2. MVP 范围

### 2.1 v0.1 必须实现

v0.1 的目标是实现一个最小可用但闭环完整的 `super-flow-kit`。它应能在一个项目中初始化状态，创建和切换模块，完成需求分析产出物，并通过看板查看进度。

v0.1 必须实现以下能力：

| 类别       | 必须实现内容                                   | 说明                                                                  |
| ---------- | ---------------------------------------------- | --------------------------------------------------------------------- |
| 初始化     | `/sfk-init`                                    | 在当前项目创建 `.sfk/` 状态目录和 `docs/super-flow-kit/` 产出物目录。 |
| 唤醒       | `/sfk`                                         | 显示当前项目、当前模块、阶段状态和下一步建议。                        |
| 状态看板   | `/sfk-status`                                  | 展示项目模块列表、当前模块阶段进度、产出物路径和风险提示。            |
| 模块管理   | `/sfk-module create <名称>`                    | 创建模块，生成 `moduleId`，写入全局索引和模块状态文件。               |
| 模块管理   | `/sfk-module list`                             | 列出所有模块及其状态。                                                |
| 模块管理   | `/sfk-module switch <moduleId 或 displayName>` | 切换当前模块。                                                        |
| 模块管理   | `/sfk-module status`                           | 查看当前模块详细状态。                                                |
| 需求分析   | `/sfk-req [需求描述]`                          | 进入需求分析阶段，通过提问和整理生成需求分析文档。                    |
| 状态持久化 | `.sfk/index.json`                              | 保存项目级配置、当前模块和模块注册表。                                |
| 状态持久化 | `.sfk/modules/{moduleId}/state.json`           | 保存模块级阶段状态、产出物、负责人和历史记录。                        |
| 产出物保存 | `docs/super-flow-kit/{moduleId}/`              | 保存需求分析 Markdown 文档。                                          |
| 交互文案   | 中文友好提示                                   | 保留“小主 / sfk 在呢”的默认风格，并允许后续配置。                     |

v0.1 中，“需求分析”必须形成完整闭环：

```text
用户输入需求 → Claude 澄清关键问题 → 生成需求分析文档 → 保存产出物 → 更新 state.json → 用户确认 → /sfk-status 可查看
```

### 2.2 v0.1 暂不实现

以下内容不进入 v0.1，以避免 MVP 范围过大：

| 暂不实现内容                                      | 推迟原因                                                      |
| ------------------------------------------------- | ------------------------------------------------------------- |
| `/sfk-export` 导出 ZIP                            | v0.8 已实现为单模块和全项目交付包导出能力。                  |
| `/sfk-code-review`                                | v0.7 已实现为开发实现后的代码审查闭环。                    |
| 完整六阶段自动化                                  | v0.1 只验证一个阶段的完整闭环，避免一次性实现过多命令。       |
| UI 设计、系统设计、开发、测试、部署的完整执行逻辑 | 先保留 schema 和模板预留，后续版本逐步补齐。                  |
| 多人冲突自动合并                                  | v0.1 只设计目录结构降低冲突，不实现复杂合并。                 |
| 模板市场                                          | 属于生态扩展，不影响 MVP 闭环。                               |
| PDF / Word / Confluence 导出                      | 属于导出增强，不影响核心使用路径。                            |
| CI/CD 集成                                        | 属于部署和自动化扩展，后续版本再考虑。                        |
| 复杂权限管理                                      | v0.1 默认在本地项目内运行，不处理团队权限模型。               |
| 完整自然语言 hook 路由                            | v0.1 可以实现基础唤醒增强，但核心能力必须依赖 slash command。 |

这些能力可以保留在路线图和预留命令中，但实现时不得阻塞 v0.1 发布。

### 2.3 MVP 验收标准

v0.1 完成时，至少应满足以下验收标准：

#### 初始化验收

1. 在未初始化项目中执行 `/sfk-init` 后，应创建：
   - `.sfk/index.json`
   - `.sfk/modules/`
   - `docs/super-flow-kit/`
2. 初始化完成后，执行 `/sfk-status` 不应报错。
3. 重复执行 `/sfk-init` 时，应识别项目已初始化，并提示用户选择保留、修复或重置，而不是直接覆盖。

#### 模块管理验收

1. 执行 `/sfk-module create 用户认证` 后，应创建一个模块。
2. 模块应同时具备：
   - 文件系统安全的 `moduleId`，例如 `user-auth` 或自动生成的 slug。
   - 用户可读的 `displayName`，例如 `用户认证`。
3. `.sfk/index.json` 应记录该模块，并把它设为 `currentModule`。
4. `.sfk/modules/{moduleId}/state.json` 应存在且 JSON 合法。
5. `/sfk-module list` 应能列出该模块。
6. `/sfk-module switch <moduleId 或 displayName>` 应能切换当前模块。

#### 需求分析验收

1. 在已有当前模块时执行 `/sfk-req 开发用户登录功能`，应进入需求分析流程。
2. 当需求描述不足时，插件应提出澄清问题，而不是直接生成最终文档。
3. 插件应能基于用户回答生成需求分析文档。
4. 需求分析文档应保存到：

   ```text
   docs/super-flow-kit/{moduleId}/
   ```

5. 模块状态文件应记录需求分析产出物路径、阶段状态、质量状态、更新时间和历史记录。
6. 用户确认后，需求分析阶段应标记为 `done`，产出物质量应标记为 `confirmed`。

#### 看板验收

1. 执行 `/sfk` 应显示当前项目状态、当前模块和下一步建议。
2. 执行 `/sfk-status` 应显示：
   - 当前模块
   - 模块列表
   - 当前模块六阶段状态
   - 已保存的需求分析产出物路径
   - 缺失阶段提示
3. 如果项目未初始化，`/sfk` 和 `/sfk-status` 应提示用户先执行 `/sfk-init`。

#### 文件与状态验收

1. 所有状态文件必须是合法 JSON。
2. 所有状态文件应包含 `schemaVersion`。
3. 状态文件中记录的产出物路径应能在文件系统中找到。
4. 文件路径应优先使用相对项目根目录的路径，避免写入本机绝对路径。
5. 插件执行过程中不得静默覆盖用户已有产出物。

#### 体验验收

1. 默认交互语言为简体中文。
2. 默认称呼为“小主”，默认插件昵称为 `sfk`。
3. 关键决策需要提供明确选项，并允许用户自由输入。
4. 错误提示应包含：发生了什么、影响是什么、建议下一步怎么做。
5. MVP 完成后，用户应能从一个空项目开始，通过命令完成以下闭环：

```text
/sfk-init
/sfk-module create 用户认证
/sfk-req 开发用户登录功能
/sfk-status
```

---

## 3. 用户使用流程

本章描述用户从安装插件到完成 MVP 闭环的主要路径。v0.1 的核心路径应尽量短，保证用户可以从空项目开始，通过少量命令完成初始化、建模块、生成需求分析文档和查看状态。

v0.1 推荐主路径：

```text
安装插件 → /sfk-init → /sfk-module create 用户认证 → /sfk-req 开发用户登录功能 → /sfk-status
```

### 3.1 初次安装

用户通过 Claude Code 插件机制安装 `super-flow-kit`。安装方式以实际发布时的 Claude Code 插件系统为准，本文档保留以下目标体验：

```bash
# 1. 添加插件市场
/plugin marketplace add Ice-K/super-flow-kit-marketplace

# 2. 安装插件
/plugin install super-flow-kit
```

安装完成后，插件应提示用户进行初始化，而不是立即创建项目状态文件。原因是插件安装是全局或环境级行为，而 `.sfk/` 状态目录应属于用户当前项目。

推荐提示：

```text
🔧 检测到已安装 super-flow-kit。

小主，接下来需要在当前项目中初始化工作流状态：

  /sfk-init

初始化后，sfk 会创建 .sfk/ 状态目录和 docs/super-flow-kit/ 产出物目录。
```

如果未来支持 `/sfk-config`，安装完成后也可以提示用户先配置昵称、称呼和默认策略。但 v0.1 中 `/sfk-config` 可以作为预留命令，不阻塞 MVP。

### 3.2 初始化项目

用户在项目根目录执行：

```text
/sfk-init
```

插件应完成以下动作：

1. 检查当前目录是否已经存在 `.sfk/index.json`。
2. 如果未初始化，则创建：
   - `.sfk/index.json`
   - `.sfk/modules/`
   - `docs/super-flow-kit/`
3. 写入默认全局配置。
4. 提示用户创建第一个模块。

推荐响应：

```text
✅ 小主，super-flow-kit 已在当前项目初始化完成。

已创建：
  - .sfk/index.json
  - .sfk/modules/
  - docs/super-flow-kit/

下一步建议：
  1️⃣ 创建第一个模块：/sfk-module create 用户认证
  2️⃣ 查看当前状态：/sfk-status
```

如果项目已初始化，插件不得直接覆盖已有状态，应提示用户选择查看、修复或重置。

### 3.3 唤醒插件

用户可以通过主命令唤醒插件：

```text
/sfk
```

`/sfk` 应读取当前项目状态，并根据状态给出下一步建议。

#### 未初始化时

```text
嗨！小主，sfk 在呢～

当前项目还没有初始化 super-flow-kit 工作流状态。

请先执行：
  /sfk-init
```

#### 已初始化但没有模块时

```text
嗨！小主，sfk 在呢～

📋 当前项目已初始化，但还没有创建模块。

建议下一步：
  /sfk-module create 用户认证
```

#### 已有当前模块时

```text
嗨！小主，sfk 在呢～

📋 当前项目状态：
  当前模块：用户认证（user-auth）
  当前阶段：需求分析
  已完成：无
  待开始：需求分析、UI 设计、系统设计、软件开发、功能测试、部署上线

请选择要进行的操作：
  1️⃣ 继续当前环节：/sfk-req
  2️⃣ 查看完整看板：/sfk-status
  3️⃣ 创建新模块：/sfk-module create <名称>
```

自然语言唤醒（例如“sfk”“嗨 sfk”“sfk 需求分析”）属于增强体验。v0.1 可以保留 hook 设计，但核心能力必须通过 slash command 可用。

### 3.4 创建模块

用户通过以下命令创建模块：

```text
/sfk-module create 用户认证
```

插件应完成以下动作：

1. 接收用户输入的展示名称 `displayName`，例如 `用户认证`。
2. 生成文件系统安全的 `moduleId`，例如 `user-auth`。
3. 创建 `.sfk/modules/{moduleId}/state.json`。
4. 创建 `docs/super-flow-kit/{moduleId}/`。
5. 更新 `.sfk/index.json` 的 `modules` 和 `currentModule`。
6. 提示用户进入需求分析。

推荐响应：

```text
✅ 已创建模块：【用户认证】

模块信息：
  - moduleId：user-auth
  - 产出物目录：docs/super-flow-kit/user-auth/
  - 状态文件：.sfk/modules/user-auth/state.json

下一步建议：
  /sfk-req 开发用户登录功能
```

如果用户输入的模块名称无法自动生成合适的 `moduleId`，插件应提供建议值并请求确认。

### 3.5 完成需求分析

MVP 阶段最重要的业务流程是 `/sfk-req`。

用户可以输入：

```text
/sfk-req 开发用户登录功能
```

插件应按以下流程执行：

1. 检查项目是否已初始化。
2. 检查是否存在当前模块。
3. 将当前模块的 `requirement` 阶段标记为 `in_progress`。
4. 分析用户输入的初始需求。
5. 如果信息不足，先提出澄清问题。
6. 澄清问题采用单题推进方式逐个确认；每个问题可根据场景设计为单选、多选或自由输入，并允许用户自定义回答。
7. 关键问题澄清完成后，先总结已确认信息。
8. 基于澄清结果提供 3–5 个可选需求方案或范围方案，并允许用户选择、组合或自定义方案。
9. 用户确认方案后，生成需求分析文档草稿。
10. 保存文档到 `docs/super-flow-kit/{moduleId}/`。
11. 更新模块状态文件中的产出物记录。
12. 请求用户确认该文档是否可作为后续阶段依据。
13. 用户确认后，将阶段状态标记为 `done`，产出物质量标记为 `confirmed`。

推荐澄清方式：

```text
小主，我先帮你把【用户登录功能】需求分析清楚。

为了避免后面返工，我先确认一个关键点。

1. 登录方式希望支持哪些？（可多选）
   A. 账号密码
   B. 手机验证码
   C. 第三方登录
   D. 多种方式都支持

你可以直接回复选项，也可以用自己的话说明。
如果这是多选问题，可以回复多个选项，例如：A、C。
```

用户回答后，插件应先确认理解，再继续下一个问题：

```text
收到，我理解为：登录方式优先支持账号密码，同时保留后续扩展空间。

接下来确认下一个问题：

2. 是否需要记住登录状态？（单选）
   A. 需要
   B. 不需要
   C. 先记录为待确认
```

所有关键问题回答完成后，插件应先总结，再基于澄清结果提供 3–5 个可选方案。用户确认或调整方案后，才进入草稿生成：

```text
好的，小主，我先总结一下刚才确认的信息：

1. 登录方式：账号密码。
2. 登录状态：需要记住登录状态。
3. 安全策略：密码输错多次后先记录为待确认。

基于这些信息，我建议下面几个需求范围方案：

1️⃣ 标准登录 MVP（推荐）
   包含账号密码登录、密码找回、记住登录状态。
   适合先快速完成可用版本。

2️⃣ 安全增强版
   在标准登录基础上，增加密码错误次数限制和账号临时锁定。
   适合对安全要求更高的项目。

3️⃣ 可扩展登录版
   在标准登录基础上，预留手机号验证码和第三方登录扩展点。
   适合后续登录方式可能增加的项目。


请选择一个方案，或者告诉我你想怎么组合。
```

澄清问题设计要求：

1. 每次只提出一个关键问题。
2. 每个问题都应提供清晰选项，也可以根据场景设计为单选、多选或自由输入。
3. 交互控件已有 Type something / 自定义输入能力，无需额外添加自定义说明选项。
4. 不应强迫用户只能从预设选项中选择。
5. 如果用户直接输入自由文本，插件应理解并归纳到需求文档中。
6. 所有关键问题完成后，必须先总结。
7. 总结后应基于澄清结果提供 3–5 个可选方案，并允许用户选择、组合或自定义。
8. 用户确认方案后，才进入草稿生成。
需求分析文档生成后，推荐提示：

```text
📝 【需求分析】草稿已生成 - 模块：用户认证（user-auth）

📄 产出物已保存至：
  docs/super-flow-kit/user-auth/20260609143000-user-auth-需求分析.md

当前状态：
  requirement.status = in_progress
  requirement.quality = draft

请确认：这份需求分析文档是否可以作为后续设计和开发依据？

  1️⃣ 确认，标记为已完成
  2️⃣ 继续修改
  3️⃣ 暂存为草稿
```

用户明确确认后，才允许输出完成提示并更新为 `done` / `confirmed`。
### 3.6 查看状态看板

用户执行：

```text
/sfk-status
```

插件应展示项目级和当前模块级状态。

推荐输出：

```text
📊 super-flow-kit 工作流看板

项目：当前项目
当前模块：用户认证（user-auth）

📦 模块列表：
  ✅ 用户认证（user-auth） - 当前模块
  ⬜ 支付模块（payment-module）

📋 当前模块阶段：
  ✅ 需求分析    confirmed  docs/super-flow-kit/user-auth/20260609143000-user-auth-需求分析.md
  ⬜ UI 设计      pending
  ⬜ 系统设计    pending
  ⬜ 软件开发    pending
  ⬜ 功能测试    pending
  ⬜ 部署上线    pending

💡 下一步建议：
  /sfk-ui 进入 UI 设计（后续版本完整支持）
```

v0.1 中，即使后续阶段尚未完整实现，看板也应显示六阶段状态，帮助用户理解完整流程。

### 3.7 后续阶段预留流程

v0.1 只完整实现需求分析阶段，但应为后续阶段保留一致的入口和状态字段：

| 命令          | 阶段     | v0.1 行为                                                      |
| ------------- | -------- | -------------------------------------------------------------- |
| `/sfk-ui`     | UI 设计  | 提示该阶段将在后续版本完整支持，可先查看需求分析文档。         |
| `/sfk-design` | 系统设计 | 提示该阶段将在后续版本完整支持，并说明依赖需求分析。           |
| `/sfk-dev`    | 软件开发 | 提示该阶段将在后续版本完整支持，并说明依赖需求分析和系统设计。 |
| `/sfk-test`   | 功能测试 | 提示该阶段将在后续版本完整支持，并说明依赖需求分析。           |
| `/sfk-deploy` | 部署上线 | 提示该阶段将在后续版本完整支持，并说明依赖测试报告。           |

预留命令不应假装已经完成能力。若用户在 v0.1 中调用这些命令，应明确说明当前版本限制，并给出可执行的替代建议。

---

## 4. Claude Code 插件结构

本章描述目标插件结构。具体实现时可以根据 Claude Code 插件系统的实际约定微调，但必须保持命令、状态和产出物职责清晰。

### 4.1 插件文件结构

目标插件仓库结构建议如下：

```text
super-flow-kit/
├── README.md
├── CLAUDE.md
├── .claude/
│   ├── commands/
│   │   ├── sfk.md
│   │   ├── sfk-init.md
│   │   ├── sfk-status.md
│   │   ├── sfk-module.md
│   │   ├── sfk-req.md
│   │   ├── sfk-ui.md
│   │   ├── sfk-design.md
│   │   ├── sfk-dev.md
│   │   ├── sfk-test.md
│   │   └── sfk-deploy.md
│   └── settings.json
├── scripts/
│   ├── sfk-init.sh
│   ├── sfk-status.sh
│   ├── sfk-module.sh
│   ├── sfk-state.sh
│   ├── sfk-render.sh
│   └── sfk-utils.sh
├── templates/
│   ├── requirement.md
│   ├── ui-design.md
│   ├── system-design.md
│   ├── development.md
│   ├── testing.md
│   └── deployment.md
└── super-flow-kit.md
```

v0.1 可以先实现最少文件：

```text
.claude/commands/sfk.md
.claude/commands/sfk-init.md
.claude/commands/sfk-status.md
.claude/commands/sfk-module.md
.claude/commands/sfk-req.md
scripts/sfk-init.sh
scripts/sfk-status.sh
scripts/sfk-module.sh
scripts/sfk-state.sh
templates/requirement.md
```

### 4.2 Slash command 设计

每个 slash command 文件应负责向 Claude 提供命令意图、执行步骤和约束。复杂的状态读写逻辑应尽量下沉到 `scripts/`，避免在多个命令文档中重复。

MVP 命令职责：

| 命令文件                         | 用户命令          | 职责                                 |
| -------------------------------- | ----------------- | ------------------------------------ |
| `.claude/commands/sfk.md`        | `/sfk`            | 主入口，读取状态并展示下一步菜单。   |
| `.claude/commands/sfk-init.md`   | `/sfk-init`       | 初始化 `.sfk/` 和产出物目录。        |
| `.claude/commands/sfk-status.md` | `/sfk-status`     | 渲染项目和模块看板。                 |
| `.claude/commands/sfk-module.md` | `/sfk-module ...` | 管理模块 create/list/switch/status。 |
| `.claude/commands/sfk-req.md`    | `/sfk-req ...`    | 执行需求分析流程并保存产出物。       |

后续阶段命令可以先创建占位文件，也可以延后创建。若创建占位文件，必须明确提示“当前版本暂未完整实现”。

Slash command 的设计原则：

1. 命令应可独立执行，不依赖用户先读文档。
2. 命令应先检查状态，再执行动作。
3. 命令遇到缺失依赖时，应给出可选处理方式。
4. 命令不得静默覆盖用户文件。
5. 命令执行完成后，应给出下一步建议。

### 4.3 Hooks 设计

自然语言唤醒可以通过 `UserPromptSubmit` hook 增强体验。需要注意：`sfk` 只是默认唤醒昵称，实际唤醒词应优先读取项目配置中的 `globalConfig.pluginName`；同理，AI 回复中的“小主”只是默认用户称呼，应优先读取 `globalConfig.userName`。

因此，用户可以通过配置把默认体验从：

```text
嗨！小主，sfk 在呢～
```

调整为类似：

```text
嗨！阿杰，flow 在呢～
```

Hook 的匹配规则应支持“默认唤醒词 + 用户自定义唤醒词”的组合。示例配置可以先包含默认值：

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": ".*(sfk|嗨 sfk|SFK).*",
        "hooks": [
          {
            "type": "command",
            "command": "scripts/sfk-wake.sh"
          }
        ]
      }
    ]
  }
}
```

但实现时不应把 `sfk` 写死为唯一名称。`sfk-wake.sh` 或等价逻辑应读取 `.sfk/index.json` 中的配置：

```json
{
  "globalConfig": {
    "pluginName": "sfk",
    "userName": "小主"
  }
}
```

若项目尚未初始化，hook 可以使用默认值：

- `pluginName`: `sfk`
- `userName`: `小主`

Hook 设计约束：

1. Hook 是增强体验，不是核心能力依赖。
2. `sfk` 是默认唤醒词，不是唯一唤醒词；用户配置 `pluginName` 后，应支持新的唤醒昵称。
3. “小主”是默认称呼，不是固定称呼；用户配置 `userName` 后，AI 回复应使用新称呼。
4. 即使 hook 不可用，用户也必须能通过 `/sfk`、`/sfk-status` 等命令完成核心流程。
5. Hook 不应直接执行破坏性操作，例如重置状态或覆盖文件。
6. Hook 可以读取状态并提示建议，但涉及写入时应要求用户通过明确命令触发。
7. Hook 脚本失败时，应尽量静默降级或给出简短提示，不应阻塞用户正常输入。

### 4.4 Scripts 设计

`scripts/` 目录用于承载可复用的状态读写和渲染逻辑。v0.1 不追求复杂架构，但应避免把所有逻辑散落到命令文档中。

建议脚本职责：

| 脚本            | 职责                                                  |
| --------------- | ----------------------------------------------------- |
| `sfk-init.sh`   | 创建 `.sfk/`、初始化 `index.json`、创建产出物根目录。 |
| `sfk-status.sh` | 读取状态并输出看板所需信息。                          |
| `sfk-module.sh` | 处理模块创建、列表、切换和状态查询。                  |
| `sfk-state.sh`  | 提供状态读取、写入、校验、备份等通用函数。            |
| `sfk-render.sh` | 渲染状态看板和通用提示文案。                          |
| `sfk-utils.sh`  | 提供 slug 生成、时间戳、路径处理等工具函数。          |
| `sfk-wake.sh`   | 自然语言唤醒增强，可选实现。                          |

脚本实现要求：

1. 优先使用项目相对路径。
2. 写入 JSON 前应尽量校验结构合法性。
3. 写入重要状态前可创建备份，避免损坏后无法恢复。
4. 输出应适合 Claude 读取和转述，也适合用户直接阅读。
5. 脚本失败时应返回非零状态，并输出明确错误信息。

#### v0.1 技术约束

v0.1 应优先选择简单、跨平台、容易在 Claude Code 环境中运行的实现方式。

推荐约束：

1. 命令入口可以使用 Bash 脚本，但 JSON 读写不应强依赖 `jq`。
2. 如需稳定处理 JSON，优先使用 Node.js 或 Python 小脚本，因为它们比手写 shell 字符串处理更可靠。
3. 脚本应兼容 Claude Code 在 Windows + bash 环境下运行的场景，路径写入状态文件时统一使用 `/`。
4. v0.1 不引入复杂构建链路；除非后续确定包管理器，否则不要求 `npm install` 或额外依赖安装。
5. 如果运行环境缺少 Node.js 或 Python，脚本应给出明确错误提示，而不是静默失败。
6. 所有核心状态变更应通过统一的状态读写逻辑完成，避免多个命令各自拼接 JSON。

可接受实现形态：

```text
Bash 命令入口
  → 调用 Node.js / Python 处理 JSON
  → 输出给 Claude 或用户阅读的纯文本结果
```

不推荐实现形态：

```text
纯 Bash 手写复杂 JSON 拼接和转义
```

### 4.5 配置文件设计

插件配置分为两类：

1. **插件默认配置**：随插件发布，定义默认昵称、默认称呼、默认补全策略等。
2. **项目级配置**：保存在 `.sfk/index.json` 的 `globalConfig` 中，作用于当前项目。

v0.1 推荐默认配置：

| 配置项            | 默认值  | 说明                               |
| ----------------- | ------- | ---------------------------------- |
| `pluginName`      | `sfk`   | 插件默认唤醒昵称。                 |
| `userName`        | `小主`  | 默认用户称呼。                     |
| `defaultStrategy` | `draft` | 缺失依赖时默认补全策略。           |
| `autoSave`        | `true`  | 阶段产出物默认自动保存。           |
| `verbose`         | `true`  | 默认输出较详细的状态和下一步建议。 |

`.sfk/index.json` 中应包含：

```json
{
  "globalConfig": {
    "pluginName": "sfk",
    "userName": "小主",
    "defaultStrategy": "draft",
    "autoSave": true,
    "verbose": true
  }
}
```

`/sfk-config` 在 v0.1 中应实现最小可用配置能力，至少支持查看配置，以及修改 `pluginName` 和 `userName`。其他配置项可以先保留在 schema 中，后续版本再提供完整交互式配置。

---

## 5. 命令规格

本章定义核心命令的行为。后续实现时，每个命令都应至少覆盖：用途、输入、前置条件、执行动作、状态变更、输出和错误处理。

### 5.1 /sfk-config

#### 用途

配置插件在当前项目中的默认行为，例如插件昵称、用户称呼、默认补全策略、自动保存和详细输出模式。

#### MVP 状态

v0.1 中 `/sfk-config` 应实现最小可用配置能力：

1. 无参数时显示当前 `globalConfig`。
2. 支持修改 `pluginName`。
3. 支持修改 `userName`。
4. 其他配置项可以先只读展示，后续版本再完整支持。

这样可以保证默认唤醒昵称 `sfk` 和默认称呼“小主”确实可配置，而不是只停留在 schema 预留层面。

#### 输入

```text
/sfk-config
/sfk-config set pluginName flow
/sfk-config set userName 阿杰
/sfk-config set defaultStrategy draft
```

#### 前置条件

- 项目已执行 `/sfk-init`。
- `.sfk/index.json` 存在且 JSON 合法。

#### 执行动作

v0.1 最小行为：

1. 读取 `.sfk/index.json`。
2. 无参数时输出当前 `globalConfig`。
3. 当用户执行 `/sfk-config set pluginName <名称>` 时，校验名称非空并更新 `globalConfig.pluginName`。
4. 当用户执行 `/sfk-config set userName <称呼>` 时，校验称呼非空并更新 `globalConfig.userName`。
5. 对 `defaultStrategy`、`autoSave`、`verbose` 可以先只读展示，提示后续版本完整支持。
6. 写入配置后，更新 `project.updatedAt`。

后续完整行为：

1. 支持交互式配置向导。
2. 校验所有配置项是否合法。
3. 更新 `.sfk/index.json`。
4. 记录配置变更历史。

#### 错误处理

- 未初始化：提示先执行 `/sfk-init`。
- 配置项不存在：列出支持的配置项。
- 配置值非法：提示允许值，例如 `draft/sequential/skip`。

### 5.2 /sfk-init

#### 用途

在当前项目初始化 `super-flow-kit` 工作流状态。

#### 输入

```text
/sfk-init
/sfk-init 电商平台
```

可选参数为项目展示名称。如果用户未提供，则默认使用当前目录名或“当前项目”。

#### 前置条件

- 当前目录可写。
- 当前目录尚未初始化，或用户明确选择修复/重置。

#### 执行动作

1. 检查 `.sfk/index.json` 是否存在。
2. 若不存在，创建基础目录：
   - `.sfk/`
   - `.sfk/modules/`
   - `docs/super-flow-kit/`
3. 写入 `.sfk/index.json`。
4. 初始化 `schemaVersion`、`project`、`currentModule`、`modules`、`globalConfig`。
5. 输出初始化结果和下一步建议。

#### 状态变更

创建 `.sfk/index.json`，示例：

```json
{
  "schemaVersion": "1.0.0",
  "project": {
    "name": "当前项目",
    "createdAt": "2026-06-09T00:00:00Z",
    "updatedAt": "2026-06-09T00:00:00Z"
  },
  "currentModule": null,
  "modules": {},
  "globalConfig": {
    "pluginName": "sfk",
    "userName": "小主",
    "defaultStrategy": "draft",
    "autoSave": true,
    "verbose": true
  }
}
```

#### 输出示例

```text
✅ 小主，super-flow-kit 初始化完成。

下一步建议：
  /sfk-module create 用户认证
```

#### 错误处理

- 已初始化：提示查看 `/sfk-status`，或要求用户确认是否修复/重置。
- 无写入权限：说明无法创建目录，并建议检查项目目录权限。
- `index.json` 损坏：提示备份当前文件后执行修复流程。

### 5.3 /sfk

#### 用途

唤醒插件，展示当前项目状态和下一步建议。

#### 输入

```text
/sfk
/sfk 需求分析
/sfk status
```

v0.1 中可以只完整支持 `/sfk`，其他参数作为路由提示处理。

#### 前置条件

无。未初始化项目中也应可执行，并提示用户执行 `/sfk-init`。

#### 执行动作

1. 检查 `.sfk/index.json` 是否存在。
2. 未初始化则输出初始化引导。
3. 已初始化则读取 `currentModule` 和模块列表。
4. 如果没有模块，提示创建模块。
5. 如果有当前模块，读取模块状态并输出下一步建议。

#### 状态变更

默认不修改状态。

#### 输出示例

```text
嗨！小主，sfk 在呢～

📋 当前项目状态：
  当前模块：用户认证（user-auth）
  需求分析：已完成
  UI 设计：待开始
  系统设计：待开始

下一步建议：
  1️⃣ 查看完整看板：/sfk-status
  2️⃣ 继续需求分析：/sfk-req
```

#### 错误处理

- 未初始化：提示 `/sfk-init`。
- 当前模块不存在：提示执行 `/sfk-module list` 或选择新的当前模块。
- 状态文件损坏：提示修复，不继续渲染错误状态。

### 5.4 /sfk-status

#### 用途

查看项目级和当前模块级工作流看板。

#### 输入

```text
/sfk-status
/sfk-status --module user-auth
```

v0.1 可以优先支持无参数形式，默认查看当前模块。

#### 前置条件

- 项目已初始化。
- `.sfk/index.json` JSON 合法。

#### 执行动作

1. 读取 `.sfk/index.json`。
2. 列出所有模块。
3. 定位当前模块。
4. 读取当前模块 `state.json`。
5. 渲染六阶段状态、产出物路径和下一步建议。

#### 状态变更

默认不修改状态。若检测到状态和文件系统不一致，可以只提示风险，不自动修改。

#### 输出要求

看板至少包含：

- 项目名称。
- 当前模块。
- 模块列表。
- 当前模块六阶段状态。
- 已有产出物路径。
- 缺失依赖或风险提示。
- 下一步建议命令。

#### 错误处理

- 未初始化：提示 `/sfk-init`。
- 没有模块：提示 `/sfk-module create <名称>`。
- 当前模块状态文件缺失：提示状态不一致，并建议修复。
- 产出物文件缺失：看板中标记风险，不假装完成。

### 5.5 /sfk-module

#### 用途

管理项目中的功能模块。

#### 支持子命令

v0.1 必须支持：

```text
/sfk-module create <名称>
/sfk-module create <名称> --id <moduleId>
/sfk-module list
/sfk-module switch <moduleId 或 displayName>
/sfk-module status
```

后续可扩展：

```text
/sfk-module dep <模块> <依赖模块>
/sfk-module rename <模块> <新名称>
/sfk-module archive <模块>
```

#### `/sfk-module create <名称>`

用途：创建新模块。

支持输入：

```text
/sfk-module create 用户认证
/sfk-module create 用户认证 --id user-auth
```

执行动作：

1. 校验项目已初始化。
2. 解析用户输入为 `displayName`。
3. 如果用户通过 `--id` 显式提供 `moduleId`，优先使用该值，并校验是否符合安全格式。
4. 如果用户未提供 `--id`，插件生成建议 `moduleId`，必要时请求用户确认。
5. 检查 `moduleId` 和 `displayName` 是否冲突。
6. 创建 `.sfk/modules/{moduleId}/state.json`。
7. 创建 `docs/super-flow-kit/{moduleId}/`。
8. 更新 `.sfk/index.json` 的 `modules`。
9. 将新模块设为 `currentModule`。
10. 输出下一步建议 `/sfk-req <需求描述>`。

错误处理：

- 名称为空：提示输入模块名称。
- 模块已存在：提示切换到已有模块或换一个名称。
- `moduleId` 冲突：提供可选 `moduleId`。
- 文件写入失败：说明失败路径和建议动作。

#### `/sfk-module list`

用途：列出所有模块。

输出至少包含：

- `moduleId`
- `displayName`
- 是否为当前模块
- 当前阶段
- 已完成阶段数量

无模块时应提示创建第一个模块。

#### `/sfk-module switch <moduleId 或 displayName>`

用途：切换当前模块。

执行动作：

1. 查找目标模块。
2. 如果唯一匹配，则更新 `.sfk/index.json` 的 `currentModule`。
3. 输出切换后的模块状态摘要。

错误处理：

- 未找到：列出可用模块。
- 多个匹配：要求用户指定 `moduleId`。
- 状态文件缺失：提示状态不完整，不应静默切换。

#### `/sfk-module status`

用途：查看当前模块详细状态。

输出至少包含：

- 模块名称和 `moduleId`
- 负责人和协作者
- 当前阶段
- 六阶段状态
- 产出物文件
- 模块依赖
- 最近历史记录

### 5.6 /sfk-req

#### 用途

进入需求分析阶段，帮助用户澄清需求并生成需求分析文档。

#### 输入

```text
/sfk-req
/sfk-req 开发用户登录功能
/sfk-req --edit
```

v0.1 必须支持普通生成流程。`--edit` 可以作为后续增强。

#### 前置条件

- 项目已初始化。
- 当前模块存在。
- 当前模块状态文件合法。

需求分析阶段没有硬依赖，因此可以作为第一个业务阶段执行。

#### 执行动作

1. 读取当前模块状态。
2. 读取 `artifacts.requirement.files[-1]`，判断是否已有当前主需求文档。
3. 将 `requirement.status` 更新为 `in_progress`。
4. 读取用户输入的初始需求。
5. 通过苏格拉底式提问澄清需求；澄清过程应采用单题推进，每次只提出一个关键问题。
6. 每个问题可根据场景设计为单选、多选或自由输入，并必须保留用户自定义入口。
7. 所有关键问题回答完成后，先总结用户已确认的信息，并请求用户确认是否生成或更新草稿。
8. 用户确认总结后，生成结构化需求分析文档草稿：首次需求分析创建新文档；已有主需求文档时默认合并更新该文档；只有用户明确要求新版本时才创建新文件。
9. 保存 Markdown 文件到 `docs/super-flow-kit/{moduleId}/`，或更新已有主需求文档。
10. 更新 `state.json` 中 `artifacts.requirement`，此时默认保持 `status: in_progress` 和 `quality: draft`。
11. 记录历史事件；合并更新已有文档时，必须在文档“变更记录”中追加一条记录。
12. 请求用户确认该文档是否可作为后续阶段依据。
13. 用户明确确认后，才将 `requirement.status` 标记为 `done`，质量标记为 `confirmed`。

#### 需求分析文档至少包含

- 背景与目标
- 用户画像或使用场景
- 功能范围
- 用户故事
- 验收标准
- 非功能需求
- 风险与待确认问题
- 变更记录

#### 状态变更

草稿生成并保存后，`artifacts.requirement` 应先记录为草稿状态：

```json
{
  "status": "in_progress",
  "quality": "draft",
  "files": [
    "docs/super-flow-kit/user-auth/20260609143000-user-auth-需求分析.md"
  ],
  "version": "0.1.0",
  "updatedAt": "2026-06-09T14:30:00Z",
  "confirmedAt": null,
  "owner": null
}
```

用户明确确认后，才允许更新为完成状态：

```json
{
  "status": "done",
  "quality": "confirmed",
  "files": [
    "docs/super-flow-kit/user-auth/20260609143000-user-auth-需求分析.md"
  ],
  "version": "1.0.0",
  "updatedAt": "2026-06-09T14:35:00Z",
  "confirmedAt": "2026-06-09T14:35:00Z",
  "owner": null
}
```

实现要求：

1. 保存草稿时不得直接写入 `status: done`。
2. 保存草稿时不得直接写入 `quality: confirmed`。
3. 用户选择“暂存为草稿”时，应保持 `status: in_progress` 和 `quality: draft`。
4. 只有用户明确确认后，才写入 `status: done` 和 `quality: confirmed`。
5. `files[-1]` 表示当前主需求文档；后续补充需求默认更新该文件，不新增文件路径。
6. 用户明确要求新版本时，才创建新的时间戳文档并追加到 `files`。

#### 错误处理

- 未初始化：提示 `/sfk-init`。
- 没有当前模块：提示 `/sfk-module create <名称>`。
- 文件写入失败：保留已生成内容并提示用户手动保存。
- 用户不确认：保持 `quality: draft`，并提示可稍后继续修改。
- 已存在已确认需求文档：默认继续编辑并合并到当前主文档，在“变更记录”中追加记录；只有用户明确要求新版本时才生成新文件。

### 5.7 后续阶段命令预留

以下命令在 v0.1 中作为预留入口：

| 命令          | 阶段     | v0.1 响应                                                            |
| ------------- | -------- | -------------------------------------------------------------------- |
| `/sfk-ui`     | UI 设计  | 当前版本暂未完整实现 UI 设计流程；建议先确认需求分析文档。           |
| `/sfk-design` | 系统设计 | 当前版本暂未完整实现系统设计流程；该阶段依赖已确认需求文档。         |
| `/sfk-dev`    | 软件开发 | 当前版本暂未完整实现开发流程；该阶段依赖需求分析和系统设计。         |
| `/sfk-test`   | 功能测试 | 当前版本暂未完整实现测试流程；该阶段依赖需求分析，建议已有开发代码。 |
| `/sfk-deploy` | 部署上线 | 当前版本暂未完整实现部署流程；该阶段依赖测试报告。                   |

预留命令应遵循两个原则：

1. 不夸大能力：明确告诉用户当前版本尚未完整支持。
2. 给出替代路径：提示用户当前能做什么，例如完善需求分析或查看状态。

---

## 6. 工作流阶段设计

本章定义 `super-flow-kit` 的阶段模型。v0.1 只完整实现需求分析阶段，但状态模型必须从一开始支持完整六阶段，避免后续版本迁移成本过高。

### 6.1 六阶段总览

完整工作流固定为六个阶段：

```text
需求分析 → UI 设计 → 系统设计 → 软件开发 → 功能测试 → 部署上线
```

阶段定义如下：

| 阶段顺序 | 阶段 ID         | 展示名称 | 核心职责                                       | 产出物后缀    | v0.1 状态 |
| -------- | --------------- | -------- | ---------------------------------------------- | ------------- | --------- |
| 1        | `requirement`   | 需求分析 | 澄清目标、范围、用户故事和验收标准。           | `需求分析.md` | 完整实现  |
| 2        | `ui_design`     | UI 设计  | 设计页面结构、交互流程、视觉规范和组件清单。   | `UI设计.md`   | 预留      |
| 3        | `system_design` | 系统设计 | 定义架构、技术选型、接口、数据模型和关键约束。 | `系统设计.md` | 预留      |
| 4        | `development`   | 软件开发 | 实现功能代码，并记录关键开发说明。             | `开发文档.md` | 预留      |
| 5        | `testing`       | 功能测试 | 设计测试策略、测试用例并记录测试结果。         | `测试文档.md` | 预留      |
| 6        | `deployment`    | 部署上线 | 设计部署流程、监控告警、回滚方案和上线说明。   | `部署文档.md` | 预留      |

阶段 ID 必须稳定，不应随展示文案变化而变化。展示名称可以在文案层调整，但状态文件、依赖规则和命令内部逻辑必须使用阶段 ID。

### 6.2 阶段依赖关系

依赖分为两类：

- **硬依赖**：进入阶段前必须满足。缺失时默认阻止继续，除非用户明确选择 `skip`。
- **软依赖**：建议具备。缺失时提示风险，但不阻止继续。

阶段依赖定义：

| 阶段 ID         | 展示名称 | 硬依赖                         | 软依赖                         |
| --------------- | -------- | ------------------------------ | ------------------------------ |
| `requirement`   | 需求分析 | 无                             | 无                             |
| `ui_design`     | UI 设计  | 无                             | `requirement`                  |
| `system_design` | 系统设计 | `requirement`                  | 无                             |
| `development`   | 软件开发 | `requirement`、`system_design` | `ui_design`                    |
| `testing`       | 功能测试 | `requirement`                  | `development`、`system_design` |
| `deployment`    | 部署上线 | `testing`                      | `system_design`                |

v0.1 中只有 `requirement` 完整执行，因此依赖检测主要用于：

1. 看板展示后续阶段为什么尚未开始。
2. 用户调用预留命令时给出明确提示。
3. 为后续版本实现完整依赖补全策略预留结构。

### 6.3 阶段状态流转

每个阶段都应有一个状态字段 `status`。

允许的阶段状态：

| 状态          | 含义                                         |
| ------------- | -------------------------------------------- |
| `pending`     | 尚未开始。                                   |
| `in_progress` | 正在进行。                                   |
| `blocked`     | 因硬依赖缺失或状态异常暂时阻塞。             |
| `done`        | 已完成，并且有可作为后续依据的产出物或结果。 |

基础状态流转：

```text
pending → in_progress → done
         ↘ blocked    → in_progress → done
```

状态规则：

1. 新模块创建后，所有阶段默认 `pending`。
2. 用户进入某阶段时，该阶段变为 `in_progress`。
3. 如果硬依赖缺失且用户不选择跳过，该阶段可标记为 `blocked`。
4. 阶段产出物生成但尚未确认时，阶段可保持 `in_progress`，产出物质量为 `draft`。
5. 用户确认产出物后，阶段可标记为 `done`，产出物质量为 `confirmed`。
6. 如果状态文件标记为 `done`，但产出物文件不存在，看板应提示风险，不应假装完全正常。

### 6.4 draft / confirmed 机制

阶段状态描述“流程是否完成”，产出物质量描述“内容是否可作为依据”。两者不能混淆。

产出物质量允许值：

| 质量状态    | 含义                                | 是否可作为硬依赖                       |
| ----------- | ----------------------------------- | -------------------------------------- |
| `draft`     | AI 或用户生成的草稿，尚未明确确认。 | 默认不可作为硬依赖，除非用户显式允许。 |
| `confirmed` | 用户确认过，可作为后续阶段依据。    | 可以作为硬依赖。                       |

推荐规则：

1. 自动生成的文档初始质量为 `draft`。
2. 用户明确确认后，质量变为 `confirmed`。
3. 如果用户选择“暂存为草稿”，阶段保持 `in_progress` 或 `pending`，由具体命令决定；v0.1 建议保持 `in_progress`，方便继续编辑。
4. 如果用户后续修改已确认文档，应根据修改方式决定是否降级为 `draft`。v0.1 可先不自动降级，只记录历史。
5. 依赖检测默认要求硬依赖阶段同时满足：`status: done` 且 `quality: confirmed`。

### 6.5 阶段完成后的下一步引导

每个阶段完成后，插件都应输出：

1. 完成状态。
2. 当前模块。
3. 产出物保存路径。
4. 状态更新结果。
5. 下一步建议。

需求分析阶段完成示例：

```text
✅ 【需求分析】已完成 - 模块：用户认证（user-auth）

📄 产出物已保存至：
  docs/super-flow-kit/user-auth/20260609143000-user-auth-需求分析.md

📌 状态已更新：
  requirement.status = done
  requirement.quality = confirmed

🔗 下一步建议：
  1️⃣ 查看状态看板：/sfk-status
  2️⃣ 进入 UI 设计：/sfk-ui（后续版本完整支持）
  3️⃣ 进入系统设计：/sfk-design（后续版本完整支持）
```

v0.1 中，后续阶段尚未完整实现，因此下一步建议必须明确标注“后续版本完整支持”，避免误导用户。

---

## 7. 模块管理设计

模块是 `super-flow-kit` 管理复杂项目的基本单位。所有阶段状态和产出物都归属于某个模块。

### 7.1 moduleId 与 displayName

模块必须同时具备内部 ID 和展示名称：

| 字段          | 示例        | 用途                                       | 是否可变          |
| ------------- | ----------- | ------------------------------------------ | ----------------- |
| `moduleId`    | `user-auth` | 用于目录名、状态索引、命令参数和文件路径。 | v0.1 不建议修改。 |
| `displayName` | `用户认证`  | 用于向用户展示。                           | 后续可支持修改。  |

设计原则：

1. `moduleId` 必须适合文件路径，只允许小写字母、数字和连字符，推荐格式为 kebab-case。
2. `displayName` 可以使用中文、英文或混合文本。
3. 状态文件和产出物路径使用 `moduleId`，用户提示中同时展示 `displayName` 和 `moduleId`。
4. 当用户输入中文模块名时，插件应尽量生成合理的 `moduleId`；如果无法可靠生成，应请求用户确认。

示例：

```json
{
  "moduleId": "user-auth",
  "displayName": "用户认证"
}
```

### 7.2 模块创建

模块创建命令：

```text
/sfk-module create 用户认证
```

创建规则：

1. 用户输入首先作为 `displayName`。
2. 插件生成建议 `moduleId`。
3. 检查 `moduleId` 是否已存在。
4. 检查 `displayName` 是否与已有模块重复。
5. 创建模块状态文件和产出物目录。
6. 将新模块设为当前模块。

推荐 slug 规则：

1. 如果用户通过 `--id` 显式提供 `moduleId`，优先使用用户提供的值。
2. `moduleId` 只允许小写字母、数字和连字符，且不能以连字符开头或结尾。
3. 如果输入已是安全英文，例如 `user-auth`，可直接作为 `moduleId`。
4. 如果输入包含空格，转为连字符并小写。
5. 如果输入是常见中文名称，可使用语义化英文 slug，例如 `用户认证` → `user-auth`。
6. 如果无法确定英文 slug，应请求用户确认，不应擅自生成难以理解的 ID。
7. 如果发生冲突，可建议追加数字后缀，例如 `user-auth-2`，但仍应请求用户确认。

创建后的最小状态：

```json
{
  "module": {
    "moduleId": "user-auth",
    "displayName": "用户认证"
  },
  "currentPhase": "requirement",
  "artifacts": {
    "requirement": { "status": "pending", "quality": null, "files": [] },
    "ui_design": { "status": "pending", "quality": null, "files": [] },
    "system_design": { "status": "pending", "quality": null, "files": [] },
    "development": { "status": "pending", "quality": null, "files": [] },
    "testing": { "status": "pending", "quality": null, "files": [] },
    "deployment": { "status": "pending", "quality": null, "files": [] }
  }
}
```

### 7.3 模块切换

模块切换命令：

```text
/sfk-module switch user-auth
/sfk-module switch 用户认证
```

切换规则：

1. 优先按 `moduleId` 精确匹配。
2. 如果未匹配，再按 `displayName` 精确匹配。
3. 如果仍未匹配，可做模糊提示，但不要自动切换。
4. 如果匹配到多个候选，要求用户指定 `moduleId`。
5. 切换成功后，只更新 `.sfk/index.json` 的 `currentModule`，不修改模块自身状态。

切换成功示例：

```text
✅ 已切换当前模块：用户认证（user-auth）

当前阶段：需求分析
下一步建议：/sfk-req
```

### 7.4 模块依赖

模块之间可以存在依赖关系。例如“支付模块”依赖“用户认证”。

v0.1 可以在 schema 中保留依赖字段，但不必完整实现依赖管理命令。后续可通过以下命令设置：

```text
/sfk-module dep 支付模块 用户认证
```

模块依赖建议保存在模块状态文件中：

```json
{
  "dependencies": [
    {
      "moduleId": "user-auth",
      "requiredPhases": ["requirement", "system_design"],
      "type": "hard"
    }
  ]
}
```

依赖检查规则：

1. 如果当前模块依赖其他模块，则进入相关阶段时应检查被依赖模块的必要阶段是否完成。
2. 模块依赖可以是硬依赖或软依赖。
3. v0.1 看板可以展示依赖字段，但不强制执行复杂跨模块检查。
4. 后续版本实现 `/sfk-module dep` 时，应同步更新当前模块 `state.json` 和 `.sfk/index.json` 中的摘要信息。

### 7.5 当前模块机制

`currentModule` 保存在 `.sfk/index.json` 中，用于决定命令默认作用对象。

规则：

1. `/sfk-req`、`/sfk-status`、`/sfk-module status` 默认作用于当前模块。
2. 创建第一个模块后，应自动设为当前模块。
3. 创建新模块后，默认切换到新模块，除非用户显式选择不切换。
4. 如果 `currentModule` 为空，业务阶段命令应提示用户先创建或切换模块。
5. 如果 `currentModule` 指向不存在的模块，看板应提示状态不一致，并引导用户选择新的当前模块。

---

## 8. 状态管理设计

状态管理采用“全局索引 + 模块独立状态”的混合方案。

```text
.sfk/
├── index.json
└── modules/
    └── {moduleId}/
        └── state.json
```

设计目标：

1. 全局状态读取快。
2. 模块状态相互隔离，减少多人协作冲突。
3. 状态结构足够稳定，支持后续六阶段扩展。
4. 所有路径优先使用相对项目根目录的路径。

### 8.1 `.sfk/index.json` schema

`.sfk/index.json` 保存项目级状态和模块注册表。

推荐 schema：

```json
{
  "schemaVersion": "1.0.0",
  "project": {
    "name": "当前项目",
    "createdAt": "2026-06-09T00:00:00Z",
    "updatedAt": "2026-06-09T00:00:00Z",
    "root": "."
  },
  "currentModule": "user-auth",
  "modules": {
    "user-auth": {
      "moduleId": "user-auth",
      "displayName": "用户认证",
      "statePath": ".sfk/modules/user-auth/state.json",
      "docsPath": "docs/super-flow-kit/user-auth/",
      "status": "active",
      "owner": null,
      "currentPhase": "requirement",
      "updatedAt": "2026-06-09T00:00:00Z"
    }
  },
  "globalConfig": {
    "pluginName": "sfk",
    "userName": "小主",
    "defaultStrategy": "draft",
    "autoSave": true,
    "verbose": true
  }
}
```

字段规则：

| 字段            | 必填 | 说明                               |
| --------------- | ---- | ---------------------------------- |
| `schemaVersion` | 是   | 状态 schema 版本。                 |
| `project`       | 是   | 项目元数据。                       |
| `currentModule` | 否   | 当前模块 ID。没有模块时为 `null`。 |
| `modules`       | 是   | 模块注册表，key 为 `moduleId`。    |
| `globalConfig`  | 是   | 项目级插件配置。                   |

### 8.2 `.sfk/modules/{moduleId}/state.json` schema

模块状态文件保存单个模块的完整工作流状态。

推荐 schema：

```json
{
  "schemaVersion": "1.0.0",
  "module": {
    "moduleId": "user-auth",
    "displayName": "用户认证",
    "createdAt": "2026-06-09T00:00:00Z",
    "updatedAt": "2026-06-09T00:00:00Z",
    "version": "0.1.0",
    "owner": null,
    "collaborators": []
  },
  "currentPhase": "requirement",
  "dependencies": [],
  "artifacts": {
    "requirement": {
      "status": "pending",
      "quality": null,
      "files": [],
      "version": null,
      "updatedAt": null,
      "confirmedAt": null,
      "owner": null
    },
    "ui_design": {
      "status": "pending",
      "quality": null,
      "files": [],
      "version": null,
      "updatedAt": null,
      "confirmedAt": null,
      "owner": null
    },
    "system_design": {
      "status": "pending",
      "quality": null,
      "files": [],
      "version": null,
      "updatedAt": null,
      "confirmedAt": null,
      "owner": null
    },
    "development": {
      "status": "pending",
      "quality": null,
      "files": [],
      "version": null,
      "updatedAt": null,
      "confirmedAt": null,
      "owner": null
    },
    "testing": {
      "status": "pending",
      "quality": null,
      "files": [],
      "version": null,
      "updatedAt": null,
      "confirmedAt": null,
      "owner": null
    },
    "deployment": {
      "status": "pending",
      "quality": null,
      "files": [],
      "version": null,
      "updatedAt": null,
      "confirmedAt": null,
      "owner": null
    }
  },
  "history": []
}
```

### 8.3 状态字段说明

| 字段                      | 位置        | 说明                                           |
| ------------------------- | ----------- | ---------------------------------------------- |
| `schemaVersion`           | index/state | 用于未来迁移。v0.1 使用 `1.0.0`。              |
| `project.name`            | index       | 项目展示名称。                                 |
| `currentModule`           | index       | 当前模块 ID。                                  |
| `modules`                 | index       | 项目模块摘要注册表。                           |
| `globalConfig.pluginName` | index       | 插件唤醒昵称，默认 `sfk`，可配置。             |
| `globalConfig.userName`   | index       | 用户称呼，默认 `小主`，可配置。                |
| `module.moduleId`         | state       | 模块内部 ID。                                  |
| `module.displayName`      | state       | 模块展示名称。                                 |
| `currentPhase`            | state       | 当前推荐处理阶段。                             |
| `dependencies`            | state       | 当前模块依赖的其他模块。                       |
| `artifacts`               | state       | 六阶段产出物状态。                             |
| `artifacts.*.status`      | state       | 阶段状态：`pending/in_progress/blocked/done`。 |
| `artifacts.*.quality`     | state       | 产出物质量：`draft/confirmed/null`。           |
| `artifacts.*.files`       | state       | 产出物相对路径列表。                           |
| `history`                 | state       | 模块历史事件。                                 |

历史事件建议格式：

```json
{
  "action": "complete_requirement",
  "timestamp": "2026-06-09T14:35:00Z",
  "user": null,
  "detail": "用户确认需求分析文档",
  "files": [
    "docs/super-flow-kit/user-auth/20260609143000-user-auth-需求分析.md"
  ]
}
```

### 8.4 文件路径规则

路径规则：

1. 状态文件中保存的路径必须优先使用相对项目根目录的路径。
2. 不应把本机绝对路径写入状态文件，例如 `C:\Users\...` 或 `F:\...`。
3. `.sfk/index.json` 中的 `statePath` 应形如 `.sfk/modules/user-auth/state.json`。
4. 产出物路径应形如 `docs/super-flow-kit/user-auth/20260609143000-user-auth-需求分析.md`。
5. 路径分隔符在状态文件中统一使用 `/`。
6. `moduleId` 必须文件系统安全，避免路径转义和跨平台问题。

### 8.5 状态更新规则

不同命令的状态更新规则：

| 命令                 | 读取                              | 写入                                      |
| -------------------- | --------------------------------- | ----------------------------------------- |
| `/sfk-init`          | 检查 `.sfk/index.json` 是否存在。 | 创建 `.sfk/index.json` 和基础目录。       |
| `/sfk`               | 读取 index 和当前模块 state。     | 默认不写入。                              |
| `/sfk-status`        | 读取 index 和当前模块 state。     | 默认不写入。                              |
| `/sfk-module create` | 读取 index。                      | 写入 index，创建模块 state 和 docs 目录。 |
| `/sfk-module switch` | 读取 index 和目标模块 state。     | 更新 index 的 `currentModule`。           |
| `/sfk-module list`   | 读取 index。                      | 默认不写入。                              |
| `/sfk-module status` | 读取 index 和当前模块 state。     | 默认不写入。                              |
| `/sfk-req`           | 读取 index 和当前模块 state。     | 更新 requirement 阶段、产出物和 history。 |

写入规则：

1. 写入 JSON 前应先读取当前文件，避免覆盖外部修改。
2. 写入前应保证 JSON 可序列化。
3. 写入后应保证 JSON 可解析。
4. 重要写入前建议创建备份，例如 `state.json.bak`。v0.1 可视实现复杂度决定是否实现。
5. 若写入失败，应向用户说明失败路径，并尽可能保留已生成内容。

---

## 9. 产出物设计

产出物是插件沉淀项目上下文的核心。v0.1 必须完整支持需求分析文档产出物。

### 9.1 产出物目录结构

产出物统一保存到：

```text
docs/super-flow-kit/{moduleId}/
```

示例：

```text
docs/
└── super-flow-kit/
    └── user-auth/
        ├── 20260609143000-user-auth-需求分析.md
        ├── 20260610100000-user-auth-UI设计.md
        └── 20260611100000-user-auth-系统设计.md
```

目录规则：

1. 每个模块有独立产出物目录。
2. 目录名使用 `moduleId`，不使用 `displayName`。
3. 文档标题和正文中应展示 `displayName`，方便用户阅读。
4. 历史版本通过时间戳文件名保留，不直接覆盖旧文件。

### 9.2 文件命名规范

推荐文件名格式：

```text
yyyyMMddHHmmss-{moduleId}-{阶段后缀}.md
```

示例：

```text
20260609143000-user-auth-需求分析.md
20260610100000-user-auth-UI设计.md
20260611100000-user-auth-系统设计.md
```

命名规则：

1. 时间戳使用本地时间或 UTC 均可，但同一实现中必须一致。
2. `moduleId` 用于文件名，避免中文路径和特殊字符带来的兼容问题。
3. 阶段后缀使用中文，提升可读性。
4. 新生成文档默认创建新文件，不覆盖旧文件。
5. 如果同一秒内生成冲突，可追加序号，例如 `-2`。

### 9.3 需求分析文档模板

v0.1 必须实现需求分析文档模板。

推荐模板：

```md
# {displayName} - 需求分析文档

## 1. 文档信息

| 字段     | 内容          |
| -------- | ------------- |
| 模块名称 | {displayName} |
| 模块 ID  | {moduleId}    |
| 阶段     | 需求分析      |
| 版本     | {version}     |
| 质量状态 | {quality}     |
| 创建时间 | {createdAt}   |
| 更新时间 | {updatedAt}   |

## 2. 背景与目标

[说明为什么要做这个功能，以及期望达成什么业务或产品目标。]

## 3. 用户画像与使用场景

[说明目标用户、典型使用场景和触发条件。]

## 4. 功能范围

### 4.1 本期包含

[列出本期明确要做的功能。]

### 4.2 本期不包含

[列出暂不实现或明确排除的范围。]

## 5. 用户故事

- 作为 [用户角色]，我希望 [完成某件事]，以便 [获得某种价值]。

## 6. 验收标准

- Given [前置条件]，When [用户行为]，Then [预期结果]。

## 7. 非功能需求

[性能、安全、兼容性、可用性、可维护性等要求。]

## 8. 风险与待确认问题

| 问题         | 影响   | 建议处理方式 |
| ------------ | ------ | ------------ |
| [待确认问题] | [影响] | [建议]       |

## 9. 变更记录

| 时间        | 变更     | 负责人  |
| ----------- | -------- | ------- |
| {createdAt} | 初版创建 | {owner} |
```

模板要求：

1. 即使用户输入较少，也应保留章节结构。
2. 不确定内容必须标注为“待确认”，不能编造成事实。
3. 用户自定义回答应被整理进对应章节。
4. 验收标准应尽量具体，可执行、可验证。

### 9.4 UI 设计文档模板

v0.1 预留，后续实现。

建议章节：

- 文档信息
- 设计目标
- 页面清单
- 用户流程
- 信息架构
- 视觉风格
- 组件清单
- 响应式设计
- 可访问性要求
- 待确认问题
- 变更记录

### 9.5 系统设计文档模板

v0.1 预留，后续实现。

建议章节：

- 文档信息
- 设计目标
- 技术选型
- 系统架构
- 模块划分
- 数据模型
- API 设计
- 权限与安全
- 性能与扩展性
- 风险与备选方案
- 变更记录

### 9.6 开发文档模板

v0.1 预留，后续实现。

建议章节：

- 文档信息
- 实现范围
- 代码结构
- 关键实现说明
- 配置项
- 本地运行方式
- 数据迁移
- 已知限制
- 后续 TODO
- 变更记录

### 9.7 测试文档模板

v0.1 预留，后续实现。

建议章节：

- 文档信息
- 测试范围
- 测试策略
- 测试环境
- 测试用例
- 测试结果
- 缺陷记录
- 风险评估
- 是否满足验收标准
- 变更记录

### 9.8 部署文档模板

v0.1 预留，后续实现。

建议章节：

- 文档信息
- 部署目标
- 环境要求
- 配置清单
- 部署步骤
- 验证步骤
- 监控告警
- 回滚方案
- 上线检查清单
- 变更记录

---

## 10. 依赖检测与补全策略

依赖检测用于在用户跳转到后续阶段时提示风险，避免缺少关键上下文导致返工。

### 10.1 硬依赖与软依赖

硬依赖和软依赖定义：

| 类型   | 行为                                 | 示例                             |
| ------ | ------------------------------------ | -------------------------------- |
| 硬依赖 | 缺失时默认阻止继续，并提示补全策略。 | 软件开发依赖需求分析和系统设计。 |
| 软依赖 | 缺失时提示风险，但允许继续。         | UI 设计是软件开发的软依赖。      |

依赖检测结果应清晰告诉用户：

1. 当前要进入哪个阶段。
2. 缺失哪些硬依赖。
3. 缺失哪些软依赖。
4. 可以选择哪些处理方式。

示例：

```text
小主，检测到你想进入【软件开发】阶段。

当前模块：用户认证（user-auth）

缺失硬依赖：
  - 需求分析
  - 系统设计

缺失软依赖：
  - UI 设计

请选择处理方式：
  1️⃣ 快速生成草稿（draft）
  2️⃣ 按顺序补全缺失阶段（sequential）
  3️⃣ 跳过检查继续（skip）
```

### 10.2 依赖满足规则

某个阶段可作为依赖，默认必须同时满足：

1. `artifacts.{phase}.status === "done"`
2. `artifacts.{phase}.quality === "confirmed"`
3. `artifacts.{phase}.files` 至少包含一个路径。
4. 至少一个记录的产出物文件在文件系统中存在。
5. 产出物文件不是空文件。

如果只满足 `status: done`，但 `quality` 不是 `confirmed`，应视为“存在草稿但未确认”。

如果状态文件记录完成，但文件缺失，应视为“状态异常”，不能作为已满足依赖。

v0.1 中完整依赖检测主要用于看板和预留命令提示；真正的阻塞逻辑在后续阶段完整实现时启用。

### 10.3 draft 策略

`draft` 策略表示：为缺失阶段快速生成 AI 草稿，让用户可以继续推进。

行为规则：

1. 插件根据当前用户描述和已有上下文生成缺失阶段草稿。
2. 草稿保存为产出物文件。
3. 草稿质量标记为 `draft`。
4. 默认不把草稿视为已确认硬依赖。
5. 用户确认后，草稿才能变为 `confirmed`。

适用场景：

- 用户想快速推进，不想完整走完前序阶段。
- 当前只是探索原型，不要求文档完全严谨。

风险提示：

```text
⚠️ 这是 AI 快速生成的草稿，可能包含假设。
建议你确认后再把它作为后续设计或开发依据。
```

### 10.4 sequential 策略

`sequential` 策略表示：按推荐顺序补全缺失阶段。

行为规则：

1. 插件列出缺失硬依赖阶段。
2. 按工作流顺序引导用户逐个完成。
3. 每个阶段都需要生成并确认产出物。
4. 全部硬依赖满足后，再回到用户原本想进入的阶段。

示例：

```text
小主，我们先按顺序补齐依赖：

1. 需求分析
2. 系统设计

完成后，我会再带你回到【软件开发】阶段。
```

适用场景：

- 用户希望稳妥推进。
- 项目复杂，后续返工成本较高。
- 准备进入开发、测试或部署等风险较高阶段。

### 10.5 skip 策略

`skip` 策略表示：用户明确选择跳过依赖检查并继续。

行为规则：

1. 插件必须先提示缺失依赖和风险。
2. 用户明确选择跳过后，才允许继续。
3. 状态历史中应记录本次跳过行为。
4. 后续看板应继续提示缺失依赖风险。

风险提示示例：

```text
⚠️ 小主，你选择跳过依赖检查。

当前缺失：
  - 需求分析
  - 系统设计

这可能导致后续实现缺少依据、验收标准不清或返工。
如果确认继续，请回复：确认跳过
```

`skip` 不应成为默认策略。即使 `defaultStrategy` 设置为 `skip`，涉及高风险阶段时也应要求用户确认。

### 10.6 用户确认规则

用户确认是产出物从 `draft` 变为 `confirmed` 的唯一默认方式。

确认方式：

1. 用户明确回复确认，例如“确认”“可以”“标记完成”。
2. 用户选择菜单中的“确认，标记为已完成”。
3. 用户通过后续命令显式确认某个产出物。该能力可在后续版本实现。

确认后应更新：

```json
{
  "status": "done",
  "quality": "confirmed",
  "confirmedAt": "2026-06-09T14:35:00Z"
}
```

不应视为确认的情况：

1. 用户只是说“先这样”。
2. 用户要求“暂存”。
3. 用户继续提出修改意见。
4. 用户没有明确回复。

如果用户不确认，插件应保留草稿并提示：

```text
好的，小主，我先把这份文档保留为草稿。

你之后可以继续修改，确认后我再把需求分析标记为已完成。
```

---

## 11. 错误处理与恢复策略

错误处理的目标不是只告诉用户“失败了”，而是让用户知道：发生了什么、影响是什么、下一步应该怎么做。

通用错误提示结构：

```text
⚠️ 小主，sfk 遇到一个问题：{问题摘要}

原因：{原因}
影响：{影响}
建议：{下一步动作}
```

### 11.1 未初始化项目

触发场景：

- 用户在没有 `.sfk/index.json` 的项目中执行 `/sfk`、`/sfk-status`、`/sfk-module` 或 `/sfk-req`。

处理规则：

1. 不应报技术错误。
2. 不应自动创建状态文件，除非用户执行 `/sfk-init`。
3. 应提示用户当前项目尚未初始化。
4. 应给出明确下一步命令。

推荐提示：

```text
嗨！小主，sfk 在呢～

当前项目还没有初始化 super-flow-kit 工作流状态。

请先执行：
  /sfk-init

初始化后，我会创建：
  - .sfk/index.json
  - .sfk/modules/
  - docs/super-flow-kit/
```

### 11.2 状态文件损坏

触发场景：

- `.sfk/index.json` 不是合法 JSON。
- `.sfk/modules/{moduleId}/state.json` 不是合法 JSON。
- 缺少必要字段，例如 `schemaVersion`、`modules` 或 `artifacts`。
- `schemaVersion` 高于当前插件支持版本。

处理规则：

1. 不应继续基于损坏状态执行写入操作。
2. 应提示损坏文件路径。
3. 应建议用户备份或修复。
4. 如果存在备份文件，后续版本可提供恢复选项。

推荐提示：

```text
⚠️ 小主，sfk 读取状态文件失败。

文件：.sfk/index.json
原因：JSON 格式不合法或缺少必要字段。
影响：暂时无法判断当前模块和工作流进度。

建议：
  1️⃣ 手动检查并修复该文件
  2️⃣ 从备份恢复
  3️⃣ 确认后重新初始化项目状态
```

v0.1 可以只提示修复，不必自动修复复杂损坏状态。

### 11.3 当前模块不存在

触发场景：

- `.sfk/index.json` 中的 `currentModule` 指向的模块不存在。
- `modules` 中存在模块记录，但对应 `.sfk/modules/{moduleId}/state.json` 缺失。

处理规则：

1. 不应静默切换到其他模块。
2. 应提示状态不一致。
3. 应列出当前注册表中仍然可用的模块。
4. 应引导用户执行 `/sfk-module switch <moduleId>`。

推荐提示：

```text
⚠️ 当前模块状态不一致。

index.json 中记录的 currentModule 是：user-auth
但没有找到对应状态文件：.sfk/modules/user-auth/state.json

你可以：
  1️⃣ 查看模块列表：/sfk-module list
  2️⃣ 切换到其他模块：/sfk-module switch <moduleId>
  3️⃣ 手动恢复缺失的 state.json
```

### 11.4 产出物缺失

触发场景：

- `state.json` 中记录了产出物路径，但文件系统中找不到该文件。
- 产出物文件存在但为空。

处理规则：

1. 看板中应标记风险。
2. 不应把该阶段当作完全满足依赖。
3. 不应自动删除状态记录。
4. 应提示用户恢复文件、重新生成或修正状态。

看板提示示例：

```text
⚠️ 需求分析状态异常

状态文件显示该阶段已完成，但产出物文件缺失：
  docs/super-flow-kit/user-auth/20260609143000-user-auth-需求分析.md

建议：
  1️⃣ 恢复该文件
  2️⃣ 重新执行 /sfk-req 生成新版本
  3️⃣ 手动修正 state.json
```

### 11.5 模块重名

触发场景：

- 新建模块时 `displayName` 与已有模块相同。
- 自动生成的 `moduleId` 与已有模块相同。

处理规则：

1. 不应覆盖已有模块。
2. 应展示冲突对象。
3. 应提供新名称或新 `moduleId` 建议。
4. 用户确认后才创建新模块。

推荐提示：

```text
⚠️ 已存在同名模块：【用户认证】

已有模块：
  - displayName：用户认证
  - moduleId：user-auth

你可以：
  1️⃣ 切换到已有模块：/sfk-module switch user-auth
  2️⃣ 使用新名称创建：/sfk-module create 用户认证二期
  3️⃣ 指定新的 moduleId（后续版本支持）
```

### 11.6 文件写入失败

触发场景：

- 当前目录不可写。
- 目标目录不存在且创建失败。
- 磁盘或权限异常。
- 文件被其他程序锁定。

处理规则：

1. 应说明写入失败的路径。
2. 如果已生成产出物内容但保存失败，应把内容保留在回复中或提示用户复制保存。
3. 不应把状态标记为已完成。
4. 不应写入部分状态造成不一致。

推荐提示：

```text
⚠️ 小主，需求分析文档生成成功，但保存文件失败。

目标路径：docs/super-flow-kit/user-auth/20260609143000-user-auth-需求分析.md
可能原因：目录无写入权限或文件被占用。

影响：我不会把需求分析阶段标记为完成，避免状态和文件不一致。

建议：
  1️⃣ 检查目录权限后重试
  2️⃣ 手动复制本次生成内容保存
  3️⃣ 再执行 /sfk-status 检查状态
```

### 11.7 reset 二次确认

`/sfk-reset` 属于高风险操作。即使 v0.1 不实现，也必须在规格中明确：任何重置、删除或覆盖状态的操作都需要二次确认。

规则：

1. 第一次调用只展示影响范围。
2. 必须要求用户输入明确确认语，例如“确认重置”。
3. 不接受模糊确认，例如“好”“行”“继续”。
4. 重置前应提示用户备份 `.sfk/` 和 `docs/super-flow-kit/`。
5. 默认不删除产出物文档，除非用户明确选择。

推荐提示：

```text
⚠️ 高风险操作：重置 super-flow-kit 状态

这可能影响：
  - .sfk/index.json
  - .sfk/modules/
  - 当前模块状态

默认不会删除 docs/super-flow-kit/ 下的产出物。

如果确认重置，请回复：确认重置
```

---

## 12. 交互文案规范

交互文案应服务于推进项目。默认风格是中文友好、轻量拟人化、清楚直接。

### 12.1 语气风格

默认语气：

- 使用简体中文。
- 可以使用“小主”作为默认称呼，但必须支持通过 `globalConfig.userName` 修改。
- 可以使用 `sfk` 作为默认插件昵称，但必须支持通过 `globalConfig.pluginName` 修改。
- 适度使用 emoji 增强可读性。
- 不过度卖萌，不用无关闲聊稀释信息密度。
- 关键操作必须清楚说明影响和下一步。

推荐风格：

```text
嗨！小主，sfk 在呢～
我先看一下当前模块状态，然后给你几个可选下一步。
```

不推荐风格：

```text
哇咔咔小主我来啦让我魔法般解决一切吧！
```

### 12.2 通用响应模板

#### 唤醒模板

```text
嗨！{userName}，{pluginName} 在呢～

📋 当前项目状态：
  当前模块：{displayName}（{moduleId}）
  当前阶段：{currentPhase}
  已完成：{completedPhases}
  待开始：{pendingPhases}

请选择要进行的操作：
  1️⃣ 继续当前环节：{nextCommand}
  2️⃣ 查看完整看板：/sfk-status
  3️⃣ 创建新模块：/sfk-module create <名称>
```

#### 无状态模板

```text
嗨！{userName}，{pluginName} 在呢～

当前项目还没有初始化工作流状态。

请先执行：
  /sfk-init
```

#### 无模块模板

```text
✅ 当前项目已初始化，但还没有模块。

建议下一步：
  /sfk-module create <模块名称>
```

### 12.3 提问模板

苏格拉底式提问用于澄清需求，而不是审问用户。提问应采用**单题推进**方式：每次只提出一个关键问题，等待用户选择或自定义回答后，再提出下一个问题。单题推进不等于只能单选；每个问题可以根据场景设计为单选、多选或纯自由输入。所有关键问题回答完成后，插件先总结用户选择，再进入产出物生成或下一步确认。

不推荐一次性列出所有问题。一次性列出过多问题会增加用户负担，也不利于根据用户上一题的回答动态调整下一题。

单题提问模板：

```text
{userName}，为了避免后面返工，我先确认一个关键点。

{问题序号}. {问题内容}？（{单选/多选/自由输入}）
   A. {选项 A}
   B. {选项 B}
   C. {选项 C}

你可以直接回复选项，也可以用自己的话说明。
如果这是多选问题，可以回复多个选项，例如：A、C。
```

用户回答后，插件应先简短确认理解，再提出下一个问题：

```text
收到，我理解为：{对用户回答的归纳}。

接下来确认下一个问题：

{下一个问题序号}. {下一个问题内容}？（{单选/多选/自由输入}）
   A. {选项 A}
   B. {选项 B}
   C. 先记录为待确认
```

所有关键问题完成后，插件应先总结，再基于澄清结果提供 3–5 个可选方案。用户确认或调整方案后，才进入下一步：

```text
好的，{userName}，我先总结一下刚才确认的信息：

1. {确认点一}
2. {确认点二}
3. {确认点三}

基于这些信息，我建议下面几个方案：

1️⃣ {方案一名称}
   适合：{适用场景}
   包含：{核心范围}

2️⃣ {方案二名称}
   适合：{适用场景}
   包含：{核心范围}

3️⃣ {方案三名称}
   适合：{适用场景}
   包含：{核心范围}


你可以选择一个方案，也可以告诉我想怎么组合。
```

提问规则：

1. 每次只提出一个关键问题。
2. 单题推进不限制选择类型；问题可以是单选、多选或自由输入。
3. 每个问题都应允许用户自定义回答。
4. 如果提供选项，不应额外添加自定义说明选项；依赖交互控件的 Type something / 自定义输入能力承接用户补充。
5. 不确定的问题可以提供“先记录为待确认”。
6. 多选问题应明确标注“可多选”，并允许用户回复多个选项。
7. 用户自由输入时，插件应归纳总结，不应要求用户重新按格式填写。
8. 下一个问题可以根据用户上一题回答动态调整。
9. 所有问题回答完成后，必须先总结。
10. 总结后应基于澄清结果提供 3–5 个可选方案，并允许用户选择、组合或自定义。
11. 用户确认方案后，才进入文档生成或下一步确认。
12. 如果用户已经给出足够上下文，不应重复提问。

### 12.4 多方案选择模板

重要决策应提供 3–5 个方案，并允许用户自定义。

模板：

```text
{userName}，这里有几种处理方式：

1️⃣ {方案一名称}
   适合：{适用场景}
   影响：{影响}

2️⃣ {方案二名称}
   适合：{适用场景}
   影响：{影响}

3️⃣ {方案三名称}
   适合：{适用场景}
   影响：{影响}


你想选哪一种？
```

规则：

1. 推荐项可以标注“推荐”，但不能强迫用户选择。
2. 方案数量通常为 3–5 个。
3. 每次选择都要允许用户自由输入。
4. 高风险操作需要额外确认。

### 12.5 完成提示模板

阶段产出物生成后，不应立即默认标记为最终完成。插件必须先展示产出物位置和状态，并请求用户再次确认。只有用户明确确认后，才能把阶段状态更新为 `done`，并把产出物质量更新为 `confirmed`。

#### 草稿生成后的确认模板

```text
📝 【{phaseName}】草稿已生成 - 模块：{displayName}（{moduleId}）

📄 产出物已保存至：
  {artifactPath}

当前状态：
  {phaseId}.status = in_progress
  {phaseId}.quality = draft

请确认：这份【{phaseName}】产出物是否可以作为后续阶段依据？

  1️⃣ 确认，标记为已完成
  2️⃣ 继续修改
  3️⃣ 暂存为草稿
```

#### 用户确认后的完成模板

```text
✅ 【{phaseName}】已完成 - 模块：{displayName}（{moduleId}）

📄 已确认产出物：
  {artifactPath}

📌 状态已更新：
  {phaseId}.status = done
  {phaseId}.quality = confirmed

🔗 下一步建议：
  1️⃣ {nextAction1}
  2️⃣ {nextAction2}
  3️⃣ 查看状态看板：/sfk-status
```

#### 用户暂存草稿后的模板

```text
好的，{userName}，我先把这份【{phaseName}】产出物保留为草稿。

📄 草稿路径：
  {artifactPath}

当前状态：
  {phaseId}.status = in_progress
  {phaseId}.quality = draft

你之后可以继续修改；确认后，我再把该阶段标记为完成。
```

完成提示规则：

1. 生成产出物后必须请求用户再次确认。
2. 用户确认前，不得把 `quality` 标记为 `confirmed`。
3. 用户确认前，不得默认把阶段标记为 `done`。
4. 用户选择继续修改时，应回到编辑或澄清流程。
5. 用户选择暂存草稿时，应保留文件路径并保持 `draft` 状态。
6. 用户明确确认后，才能输出“已完成”模板。

### 12.6 错误提示模板

错误提示必须包含原因、影响和建议动作。

模板：

```text
⚠️ {userName}，{pluginName} 遇到一个问题：{summary}

原因：{reason}
影响：{impact}
建议：
  1️⃣ {suggestion1}
  2️⃣ {suggestion2}
  3️⃣ 其他，我自己处理
```

规则：

1. 不只输出“失败”或“报错”。
2. 不暴露过多无意义堆栈，除非用户需要调试细节。
3. 文件路径必须明确。
4. 可恢复错误应给出恢复路径。
5. 不可自动恢复的错误应停止写入，避免扩大损坏。

---

## 13. 多人协作支持

v0.1 的多人协作目标是“降低冲突”，不是实现完整协作平台。

### 13.1 状态目录版本控制建议

建议将 `.sfk/` 纳入版本控制，以共享工作流状态。

推荐 `.gitignore` 规则：

```gitignore
# 保留 super-flow-kit 状态管理目录
!.sfk/
!.sfk/index.json
!.sfk/modules/
!.sfk/modules/**/state.json

# 保留 super-flow-kit 产出物
!docs/super-flow-kit/
!docs/super-flow-kit/**
```

如果项目不希望共享本地状态，也可以选择不提交 `.sfk/`。但团队协作时，至少建议提交 `docs/super-flow-kit/` 产出物。

### 13.2 模块级状态降低冲突

采用混合状态模型的原因：

```text
.sfk/index.json                    # 项目级索引
.sfk/modules/{moduleId}/state.json # 模块级状态
```

优势：

1. 多人修改不同模块时，主要修改不同的 `state.json`。
2. `.sfk/index.json` 只保存模块摘要，减少频繁冲突。
3. 产出物按模块目录隔离，方便评审和归档。
4. 模块迁移时可以整体移动模块状态和产出物目录。

限制：

1. 创建新模块仍会修改 `.sfk/index.json`，可能发生冲突。
2. 多人同时修改同一模块仍可能冲突。
3. v0.1 不自动合并冲突，需要用户或 Git 工具处理。

### 13.3 产出物冲突处理

产出物文件使用时间戳命名，默认不覆盖旧文件，因此一般不应出现同名覆盖冲突。

仍可能出现的冲突：

- 两人同时修改同一个 Markdown 产出物。
- 两人同时修改同一个模块状态文件。
- Git 合并时 `.sfk/index.json` 冲突。

推荐提示：

```text
⚠️ 检测到可能的产出物或状态冲突。

建议处理方式：
  1️⃣ 查看 Git diff
  2️⃣ 保留两个版本并人工合并
  3️⃣ 选择其中一个版本作为最新确认版
  4️⃣ 其他，我自己处理
```

v0.1 不实现自动冲突合并。后续版本可提供辅助 diff 和合并建议。

### 13.4 协作者字段

模块状态中预留协作者字段：

```json
{
  "module": {
    "owner": "张三",
    "collaborators": ["李四", "王五"]
  }
}
```

字段说明：

| 字段                | 说明                         |
| ------------------- | ---------------------------- |
| `owner`             | 模块负责人，可为空。         |
| `collaborators`     | 协作者列表，默认为空数组。   |
| `artifacts.*.owner` | 某阶段产出物负责人，可为空。 |

v0.1 可以只保留字段，不实现完整人员管理。后续版本可扩展模块分配、责任人筛选和团队看板。

---

## 14. 版本路线图

路线图应围绕“先闭环，再扩展”推进。

### 14.1 v0.1 MVP

目标：完成最小可用闭环。

必须交付：

- `/sfk-init`
- `/sfk`
- `/sfk-status`
- `/sfk-module create/list/switch/status`
- `/sfk-req`
- `.sfk/index.json`
- `.sfk/modules/{moduleId}/state.json`
- `docs/super-flow-kit/{moduleId}/` 需求分析产出物
- 需求分析文档模板

验收路径：

```text
/sfk-init
/sfk-module create 用户认证
/sfk-req 开发用户登录功能
/sfk-status
```

完成标准：用户能从空项目开始，生成一份已确认的需求分析文档，并在看板中看到状态。

### 14.2 v0.2 扩展工作流阶段

目标：把单阶段闭环扩展到前置设计阶段。

建议交付：

- `/sfk-ui` 完整 UI 设计流程
- `/sfk-design` 完整系统设计流程
- UI 设计文档模板
- 系统设计文档模板
- 阶段依赖检测正式启用
- `draft` 与 `confirmed` 更完整的确认流程

验收标准：用户能从需求分析继续生成 UI 设计和系统设计产出物。

### 14.3 v0.3 智能补全增强

目标：支持用户从任意阶段开始，并智能处理缺失依赖。

建议交付：

- `/sfk-dev` 基础开发协作流程
- `/sfk-test` 基础测试文档流程
- `/sfk-deploy` 基础部署文档流程
- `draft` 策略完整实现
- `sequential` 策略完整实现
- `skip` 策略历史记录
- 状态修复辅助命令

验收标准：用户直接进入开发阶段时，插件能检测缺失依赖并引导补全或确认跳过。

### 14.4 v1.0 完整插件发布

目标：达到可公开发布和长期使用的稳定版本。

建议交付：

- 完整六阶段工作流
- 完整模块依赖管理
- `/sfk-config` 完整配置能力
- `/sfk-export` 交付包导出能力
- `/sfk-code-review` 代码审查阶段
- 冲突检测与合并辅助
- README 用户文档
- 安装、升级、迁移说明
- 基础测试套件

发布标准：

1. 新用户可以根据 README 安装并完成 MVP 路径。
2. 所有核心命令都有明确错误处理。
3. 状态文件 schema 稳定并有迁移策略。
4. 至少覆盖一个完整示例项目流程。

---

## 15. 附录

### 15.1 完整命令列表

| 命令                        | v0.1 状态   | 说明                                 |
| --------------------------- | ----------- | ------------------------------------ |
| `/sfk`                      | 必须实现    | 唤醒插件并显示当前状态和下一步建议。 |
| `/sfk-init`                 | 必须实现    | 初始化项目工作流状态。               |
| `/sfk-status`               | 必须实现    | 查看项目和当前模块看板。             |
| `/sfk-module create <名称>` | 必须实现    | 创建模块。                           |
| `/sfk-module list`          | 必须实现    | 列出模块。                           |
| `/sfk-module switch <模块>` | 必须实现    | 切换当前模块。                       |
| `/sfk-module status`        | 必须实现    | 查看当前模块状态。                   |
| `/sfk-req`                  | 必须实现    | 执行需求分析流程。                   |
| `/sfk-config`               | 预留        | 查看或修改项目配置。                 |
| `/sfk-ui`                   | 预留        | UI 设计阶段。                        |
| `/sfk-design`               | 预留        | 系统设计阶段。                       |
| `/sfk-dev`                  | 预留        | 软件开发阶段。                       |
| `/sfk-test`                 | 预留        | 功能测试阶段。                       |
| `/sfk-deploy`               | 预留        | 部署上线阶段。                       |
| `/sfk-export`               | v0.8 已实现 | 导出单模块或全项目交付包，支持可选 zip。 |
| `/sfk-reset`                | 远期/高风险 | 重置项目工作流状态，必须二次确认。   |
| `/sfk-code-review`          | v0.7 已实现 | 代码审查阶段，记录审查结论、问题状态、修复回流和再审要求。 |

### 15.2 示例目录结构

```text
项目根目录/
├── .sfk/
│   ├── index.json
│   └── modules/
│       ├── user-auth/
│       │   └── state.json
│       └── payment-module/
│           └── state.json
└── docs/
    └── super-flow-kit/
        ├── user-auth/
        │   ├── 20260609143000-user-auth-需求分析.md
        │   ├── 20260610100000-user-auth-UI设计.md
        │   └── 20260611100000-user-auth-系统设计.md
        └── payment-module/
            └── 20260612100000-payment-module-需求分析.md
```

### 15.3 示例 index.json

```json
{
  "schemaVersion": "1.0.0",
  "project": {
    "name": "电商平台",
    "createdAt": "2026-06-09T00:00:00Z",
    "updatedAt": "2026-06-09T14:35:00Z",
    "root": "."
  },
  "currentModule": "user-auth",
  "modules": {
    "user-auth": {
      "moduleId": "user-auth",
      "displayName": "用户认证",
      "statePath": ".sfk/modules/user-auth/state.json",
      "docsPath": "docs/super-flow-kit/user-auth/",
      "status": "active",
      "owner": null,
      "currentPhase": "requirement",
      "updatedAt": "2026-06-09T14:35:00Z"
    }
  },
  "globalConfig": {
    "pluginName": "sfk",
    "userName": "小主",
    "defaultStrategy": "draft",
    "autoSave": true,
    "verbose": true
  }
}
```

### 15.4 示例 state.json

```json
{
  "schemaVersion": "1.0.0",
  "module": {
    "moduleId": "user-auth",
    "displayName": "用户认证",
    "createdAt": "2026-06-09T00:00:00Z",
    "updatedAt": "2026-06-09T14:35:00Z",
    "version": "0.1.0",
    "owner": null,
    "collaborators": []
  },
  "currentPhase": "requirement",
  "dependencies": [],
  "artifacts": {
    "requirement": {
      "status": "done",
      "quality": "confirmed",
      "files": [
        "docs/super-flow-kit/user-auth/20260609143000-user-auth-需求分析.md"
      ],
      "version": "1.0.0",
      "updatedAt": "2026-06-09T14:35:00Z",
      "confirmedAt": "2026-06-09T14:35:00Z",
      "owner": null
    },
    "ui_design": {
      "status": "pending",
      "quality": null,
      "files": [],
      "version": null,
      "updatedAt": null,
      "confirmedAt": null,
      "owner": null
    },
    "system_design": {
      "status": "pending",
      "quality": null,
      "files": [],
      "version": null,
      "updatedAt": null,
      "confirmedAt": null,
      "owner": null
    },
    "development": {
      "status": "pending",
      "quality": null,
      "files": [],
      "version": null,
      "updatedAt": null,
      "confirmedAt": null,
      "owner": null
    },
    "testing": {
      "status": "pending",
      "quality": null,
      "files": [],
      "version": null,
      "updatedAt": null,
      "confirmedAt": null,
      "owner": null
    },
    "deployment": {
      "status": "pending",
      "quality": null,
      "files": [],
      "version": null,
      "updatedAt": null,
      "confirmedAt": null,
      "owner": null
    }
  },
  "history": [
    {
      "action": "create_module",
      "timestamp": "2026-06-09T00:00:00Z",
      "user": null,
      "detail": "创建模块：用户认证"
    },
    {
      "action": "complete_requirement",
      "timestamp": "2026-06-09T14:35:00Z",
      "user": null,
      "detail": "用户确认需求分析文档",
      "files": [
        "docs/super-flow-kit/user-auth/20260609143000-user-auth-需求分析.md"
      ]
    }
  ]
}
```

### 15.5 示例交互流程

```text
用户：/sfk-init

AI：✅ 小主，super-flow-kit 初始化完成。
    下一步建议：/sfk-module create 用户认证
```

```text
用户：/sfk-module create 用户认证

AI：✅ 已创建模块：【用户认证】

    模块信息：
      - moduleId：user-auth
      - 产出物目录：docs/super-flow-kit/user-auth/
      - 状态文件：.sfk/modules/user-auth/state.json

    下一步建议：/sfk-req 开发用户登录功能
```

```text
用户：/sfk-req 开发用户登录功能

AI：小主，我先帮你把【用户登录功能】需求分析清楚。

    为了避免后面返工，我先确认一个关键点。

    1. 登录方式希望支持哪些？（可多选）
       A. 账号密码
       B. 手机验证码
       C. 第三方登录
       D. 多种方式都支持

    你可以直接回复选项，也可以用自己的话说明。
```

```text
用户：A，另外需要支持密码找回

AI：收到，我理解为：登录方式优先支持账号密码，并且需要支持密码找回。

    接下来确认下一个问题：

    2. 是否需要记住登录状态？（单选）
       A. 需要
       B. 不需要
       C. 先记录为待确认
```

```text
用户：A

AI：收到，我理解为：需要记住登录状态。

    我先总结一下刚才确认的信息：

    1. 登录方式：账号密码。
    2. 账号能力：需要支持密码找回。
    3. 登录状态：需要记住登录状态。

    基于这些信息，我建议下面几个需求范围方案：

    1️⃣ 标准登录 MVP（推荐）
       包含账号密码登录、密码找回、记住登录状态。
       适合先快速完成可用版本。

    2️⃣ 安全增强版
       在标准登录基础上，增加密码错误次数限制和账号临时锁定。
       适合对安全要求更高的项目。

    3️⃣ 可扩展登录版
       在标准登录基础上，预留手机号验证码和第三方登录扩展点。
       适合后续登录方式可能增加的项目。


    请选择一个方案，或者告诉我你想怎么组合。
```

```text
用户：1

AI：📝 【需求分析】草稿已生成 - 模块：用户认证（user-auth）

    📄 产出物已保存至：
      docs/super-flow-kit/user-auth/20260609143000-user-auth-需求分析.md

    请确认：这份需求分析文档是否可以作为后续设计和开发依据？

      1️⃣ 确认，标记为已完成
      2️⃣ 继续修改
      3️⃣ 暂存为草稿
```

```text
用户：确认

AI：✅ 【需求分析】已完成 - 模块：用户认证（user-auth）

    📌 状态已更新：
      requirement.status = done
      requirement.quality = confirmed

    下一步建议：/sfk-status
```

```text
用户：/sfk-status

AI：📊 super-flow-kit 工作流看板

    当前模块：用户认证（user-auth）

    📋 当前模块阶段：
      ✅ 需求分析    confirmed  docs/super-flow-kit/user-auth/20260609143000-user-auth-需求分析.md
      ⬜ UI 设计      pending
      ⬜ 系统设计    pending
      ⬜ 软件开发    pending
      ⬜ 功能测试    pending
      ⬜ 部署上线    pending
```
