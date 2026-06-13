from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SFK_SCRIPT = REPO_ROOT / "scripts" / "sfk.py"
MODULE_ID = "user-management"
MODULE_NAME = "用户管理"
REQ_DOC = f"docs/super-flow-kit/{MODULE_ID}/20260610120000-{MODULE_ID}-需求分析.md"
UI_DOC = f"docs/super-flow-kit/{MODULE_ID}/20260610123000-{MODULE_ID}-UI设计.md"
SYS_DOC = f"docs/super-flow-kit/{MODULE_ID}/20260610130000-{MODULE_ID}-系统设计.md"
DEV_DOC = f"docs/super-flow-kit/{MODULE_ID}/20260610133000-{MODULE_ID}-开发文档.md"
TEST_DOC = f"docs/super-flow-kit/{MODULE_ID}/20260610140000-{MODULE_ID}-测试文档.md"
DEPLOY_DOC = f"docs/super-flow-kit/{MODULE_ID}/20260610150000-{MODULE_ID}-部署文档.md"


def run_sfk(project_dir: Path, *args: str, check: bool = True, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    merged_env.setdefault("PYTHONIOENCODING", "utf-8")
    if env:
        merged_env.update(env)
    result = subprocess.run(
        [sys.executable, str(SFK_SCRIPT), *args],
        cwd=project_dir,
        text=True,
        encoding="utf-8",
        capture_output=True,
        env=merged_env,
        check=False,
    )
    if check and result.returncode != 0:
        raise AssertionError(
            f"sfk command failed: {' '.join(args)}\n"
            f"returncode: {result.returncode}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return result


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_requirement_doc(project_dir: Path, rel_path: str = REQ_DOC) -> Path:
    path = project_dir / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# 用户管理需求分析\n\n"
        "## 3. 文档信息\n\n"
        "| 字段 | 值 |\n"
        "| --- | --- |\n"
        "| 模块 | 用户管理 |\n"
        "| 质量状态 | pending |\n\n"
        "## 9. 项目/业务/代码上下文\n\n"
        "当前模块用于管理用户登录和账号信息。\n\n"
        "## 4. 背景与目标\n\n"
        "为用户提供稳定的登录入口，并为后续权限能力奠定基础。\n\n"
        "## 6. 用户画像与使用场景\n\n"
        "普通用户在访问受保护功能前需要完成登录。\n\n"
        "## 5. 功能范围\n\n"
        "### 5.1 本期包含\n\n"
        "- 用户可以使用账号和密码登录。\n\n"
        "### 5.2 本期不包含\n\n"
        "- 本期不包含第三方 OAuth 登录。\n\n"
        "## 8. 用户故事\n\n"
        "- 作为普通用户，我希望使用账号密码登录，以便访问个人功能。\n\n"
        "## 7. 验收标准\n\n"
        "- Given 用户输入有效账号密码，When 提交登录，Then 系统显示登录成功。\n\n"
        "## 10. 非功能需求\n\n"
        "登录反馈需要清晰，错误信息不能泄露敏感细节。\n\n"
        "## 11. 下游影响分析\n\n"
        "| 受影响阶段 | 影响说明 | 同步建议 |\n"
        "| ---------- | -------- | -------- |\n"
        "| UI 设计 | 需要设计登录表单和错误状态 | 执行 /sfk-ui |\n\n"
        "## 12. 风险与待确认问题\n\n"
        "| 问题 | 影响 | 建议处理方式 |\n"
        "| ---- | ---- | ------------ |\n"
        "| 密码策略待确认 | 影响校验规则 | 与用户确认后进入系统设计 |\n\n"
        "## 2. 变更记录\n\n"
        "| 时间 | 变更 | 负责人 |\n"
        "| --- | --- | --- |\n"
        "| 2026-06-10 | 创建需求草稿 | 待确认 |\n",
        encoding="utf-8",
    )
    return path


def write_ui_doc(project_dir: Path, rel_path: str = UI_DOC) -> Path:
    path = project_dir / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# 用户管理 UI 设计\n\n"
        "## 4. 文档信息\n\n"
        "| 字段 | 值 |\n"
        "| --- | --- |\n"
        "| 模块 | 用户管理 |\n"
        "| 质量状态 | pending |\n\n"
        "## 8. 页面清单\n\n"
        "- 登录页\n\n"
        "## 1. 变更记录\n\n"
        "| 时间 | 变更 | 负责人 |\n"
        "| --- | --- | --- |\n"
        "| 2026-06-10 | 创建 UI 草稿 | 待确认 |\n",
        encoding="utf-8",
    )
    return path


def write_system_design_doc(project_dir: Path, rel_path: str = SYS_DOC) -> Path:
    path = project_dir / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# 用户管理系统设计\n\n"
        "## 5. 文档信息\n\n"
        "| 字段 | 值 |\n"
        "| --- | --- |\n"
        "| 模块 | 用户管理 |\n"
        "| 质量状态 | pending |\n\n"
        "## 9. 设计目标与范围\n\n"
        "支持用户登录能力的服务端架构设计。\n\n"
        "## 3. 需求依据\n\n"
        "依据已确认的用户管理需求分析文档。\n\n"
        "## 4. UI / 交互依据\n\n"
        "登录页提交账号密码并展示成功或失败反馈。\n\n"
        "## 6. 项目技术现状与约束\n\n"
        "当前项目使用 Python 标准库维护插件状态。\n\n"
        "## 7. 技术选型\n\n"
        "继续使用 Python 标准库实现状态管理。\n\n"
        "## 8. 系统架构\n\n"
        "登录请求经由命令入口进入状态工具。\n\n"
        "## 10. 模块划分\n\n"
        "状态工具负责 JSON 读写，命令文档负责交互流程。\n\n"
        "## 11. 数据库设计\n\n"
        "### 11.1 概念数据模型\n\n"
        "用户实体记录账号、登录凭据摘要和账号状态。\n\n"
        "### 11.2 表结构设计\n\n"
        "| 表 | 用途 | 主键 | 重要字段 | 关联表 |\n"
        "| --- | --- | --- | --- | --- |\n"
        "| users | 保存用户账号 | id | username、password_hash、status | 无 |\n\n"
        "### 11.3 字段说明\n\n"
        "username 唯一且必填，password_hash 只保存哈希摘要。\n\n"
        "### 11.4 关系、索引与唯一约束\n\n"
        "users.username 需要唯一索引，便于登录查询和冲突校验。\n\n"
        "### 11.5 数据生命周期与迁移策略\n\n"
        "用户创建后可更新状态，删除采用软删除或归档策略。\n\n"
        "## 12. API / 接口设计\n\n"
        "### 12.1 接口清单\n\n"
        "POST /api/login 由登录页调用认证服务，需要匿名访问权限。\n\n"
        "### 12.2 请求 / 响应结构\n\n"
        "请求包含 username 和 password，响应包含登录结果和用户摘要。\n\n"
        "### 12.3 错误码与异常响应\n\n"
        "INVALID_CREDENTIALS 表示账号或密码错误，用户可见反馈保持模糊。\n\n"
        "### 12.4 鉴权与权限控制\n\n"
        "登录接口匿名可访问，成功后签发会话凭证。\n\n"
        "### 12.5 分页、排序、过滤、幂等与限流\n\n"
        "登录接口不分页，需要限流和防暴力破解。\n\n"
        "### 12.6 外部集成 / 事件 / Webhook\n\n"
        "本期不涉及外部集成。\n\n"
        "## 13. 权限与安全\n\n"
        "产出物路径必须位于项目根目录内。\n\n"
        "## 14. 错误处理与可观测性\n\n"
        "脚本通过非零退出码和 stderr 返回错误。\n\n"
        "## 15. 性能与扩展性\n\n"
        "文件扫描限制数量，避免大型项目中过度遍历。\n\n"
        "## 16. 部署与运行约束\n\n"
        "运行环境需要 Python 标准库和 Bash 包装命令。\n\n"
        "## 17. 风险与备选方案\n\n"
        "命令文档执行偏差由脚本层质量门禁兜底。\n\n"
        "## 18. 假设与待确认问题\n\n"
        "暂无待确认问题。\n\n"
        "## 19. 下游影响分析\n\n"
        "系统设计确认后影响开发、测试和部署阶段。\n\n"
        "## 1. 变更记录\n\n"
        "| 时间 | 变更 | 负责人 |\n"
        "| --- | --- | --- |\n"
        "| 2026-06-10 | 创建系统设计草稿 | 待确认 |\n",
        encoding="utf-8",
    )
    return path


def write_development_doc(project_dir: Path, rel_path: str = DEV_DOC) -> Path:
    path = project_dir / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# 用户管理开发文档\n\n"
        "## 4. 文档信息\n\n"
        "| 字段 | 值 |\n"
        "| --- | --- |\n"
        "| 模块 | 用户管理 |\n"
        "| 质量状态 | pending |\n\n"
        "## 9. 开发目标与范围\n\n"
        "实现用户登录开发计划，不直接声明代码已经完成。\n\n"
        "## 3. 需求依据\n\n"
        "依据已确认的需求分析文档。\n\n"
        "## 5. 系统设计依据\n\n"
        "依据已确认的系统设计文档。\n\n"
        "## 6. API 设计依据\n\n"
        "POST /api/login 接收账号密码并返回登录结果。\n\n"
        "## 7. 数据库设计依据\n\n"
        "users 表保存账号、密码摘要和状态，username 唯一。\n\n"
        "## 8. UI / 交互依据\n\n"
        "登录页提交账号密码并展示错误反馈。\n\n"
        "## 10. 项目代码现状与约束\n\n"
        "现有代码需要延续状态工具和命令文档分层。\n\n"
        "## 11. 实现任务拆解\n\n"
        "先实现状态校验，再补充接口处理和验证计划。\n\n"
        "## 12. 关键文件与改动计划\n\n"
        "计划修改服务层、接口层和测试文件。\n\n"
        "## 13. 接口 / 数据 / 状态变更\n\n"
        "新增登录接口并读取 users 数据。\n\n"
        "## 14. 错误处理、安全与可观测性\n\n"
        "错误信息不泄露敏感细节，记录必要审计日志。\n\n"
        "## 15. 测试与验证计划\n\n"
        "覆盖成功登录、失败登录和限流场景。\n\n"
        "## 16. 开发顺序与回滚策略\n\n"
        "先增加测试，再实现接口；回滚时移除接口入口。\n\n"
        "## 17. 实现前确认\n\n"
        "开发文档确认不代表授权修改源码，源码实现需要二次确认。\n\n"
        "## 18. 风险与待确认问题\n\n"
        "密码策略仍需业务确认。\n\n"
        "## 19. 下游影响分析\n\n"
        "开发文档会影响测试覆盖和部署检查。\n\n"
        "## 1. 变更记录\n\n"
        "| 时间 | 变更 | 负责人 |\n"
        "| --- | --- | --- |\n"
        "| 2026-06-10 | 创建开发草稿 | 待确认 |\n",
        encoding="utf-8",
    )
    return path


def write_testing_doc(project_dir: Path, rel_path: str = TEST_DOC) -> Path:
    path = project_dir / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# 用户管理测试文档\n\n"
        "## 4. 文档信息\n\n"
        "| 字段 | 值 |\n"
        "| --- | --- |\n"
        "| 模块 | 用户管理 |\n"
        "| 质量状态 | pending |\n\n"
        "## 9. 测试目标与范围\n\n"
        "验证用户登录需求的核心路径、失败反馈和基础安全约束。\n\n"
        "## 3. 需求依据\n\n"
        "依据已确认的用户管理需求分析文档和登录验收标准。\n\n"
        "## 5. 系统设计依据\n\n"
        "依据系统设计中的登录接口、用户数据和限流约束；缺失时记录为风险。\n\n"
        "## 6. 开发依据\n\n"
        "依据开发文档中的登录接口开发计划和测试验证计划；缺失时按需求制定测试计划。\n\n"
        "## 7. 项目测试上下文与约束\n\n"
        "当前测试上下文以需求验收标准为主，测试命令和环境在执行前确认。\n\n"
        "## 8. 测试策略\n\n"
        "组合单元测试、集成测试和手工验证，覆盖成功登录、失败登录和错误反馈。\n\n"
        "## 10. 测试范围与覆盖矩阵\n\n"
        "登录成功、凭证错误、空输入和异常反馈均需要覆盖。\n\n"
        "## 11. 测试用例\n\n"
        "TC-LOGIN-001 验证有效账号密码登录成功；TC-LOGIN-002 验证错误密码提示。\n\n"
        "## 12. 测试数据与环境\n\n"
        "使用测试账号和隔离环境，避免污染真实用户数据。\n\n"
        "## 13. 自动化与手工执行计划\n\n"
        "优先运行已有自动化测试；缺少命令时执行手工验证并记录证据。\n\n"
        "## 14. 执行记录\n\n"
        "当前文档为测试计划，尚未声明所有测试已经执行通过。\n\n"
        "## 15. 缺陷与风险\n\n"
        "测试命令、账号数据和部署环境仍需在执行前确认。\n\n"
        "## 16. 回归测试范围\n\n"
        "后续登录接口、用户数据或错误反馈变更时，需要回归登录主流程。\n\n"
        "## 17. 验收结论\n\n"
        "当前测试计划覆盖需求验收标准；实际执行结果需在执行记录中补充。\n\n"
        "## 18. 部署前测试建议\n\n"
        "部署前至少完成登录成功、失败、限流和回归验证。\n\n"
        "## 19. 下游影响分析\n\n"
        "测试结论会影响部署准入、发布风险判断和回滚策略。\n\n"
        "## 1. 变更记录\n\n"
        "| 时间 | 变更 | 负责人 |\n"
        "| --- | --- | --- |\n"
        "| 2026-06-10 | 创建测试草稿 | 待确认 |\n",
        encoding="utf-8",
    )
    return path


def write_deployment_doc(project_dir: Path, rel_path: str = DEPLOY_DOC) -> Path:
    path = project_dir / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# 用户管理部署文档\n\n"
        "## 4. 文档信息\n\n"
        "| 字段 | 值 |\n"
        "| --- | --- |\n"
        "| 模块 | 用户管理 |\n"
        "| 质量状态 | pending |\n\n"
        "## 9. 部署目标与范围\n\n"
        "规划用户管理模块在测试确认后的部署上线步骤，不执行真实部署。\n\n"
        "## 3. 上线依据与准入条件\n\n"
        "依据已确认测试文档和上线窗口确认部署准入。\n\n"
        "## 5. 全模块测试准入检查\n\n"
        "所有模块需要检测到已确认且可用的测试产出物；风险需在上线前确认。\n\n"
        "## 6. 架构与运行环境依据\n\n"
        "依据系统设计和现有部署配置确定运行环境。\n\n"
        "## 7. 环境与配置管理\n\n"
        "只记录配置项名称和密钥来源，不记录密钥值。\n\n"
        "## 8. 构建与制品管理\n\n"
        "使用确认后的构建命令生成版本化制品。\n\n"
        "## 10. 数据库 / 数据迁移计划\n\n"
        "本次不涉及数据库迁移；如后续涉及需补充回滚策略。\n\n"
        "## 11. 部署流程\n\n"
        "按准备、发布、验证、观察四步推进部署。\n\n"
        "## 12. 健康检查与上线验证\n\n"
        "部署后执行健康检查和登录主流程 smoke 验证。\n\n"
        "## 13. 监控、日志与告警\n\n"
        "观察错误率、登录失败率、响应时间和关键日志。\n\n"
        "## 14. 回滚与恢复方案\n\n"
        "出现关键错误时回滚到上一稳定版本并验证登录流程。\n\n"
        "## 15. 安全、权限与合规\n\n"
        "部署权限需由授权人员执行，敏感配置通过密钥管理系统注入。\n\n"
        "## 16. 运维交接与值守计划\n\n"
        "上线窗口安排负责人值守并通知相关干系人。\n\n"
        "## 17. 风险与待确认问题\n\n"
        "若存在模块测试产出物未确认，需要在上线前确认风险接受或补测。\n\n"
        "## 18. 上线后跟踪与后续动作\n\n"
        "上线后跟踪登录成功率、错误日志和用户反馈。\n\n"
        "## 1. 变更记录\n\n"
        "| 时间 | 变更 | 负责人 |\n"
        "| --- | --- | --- |\n"
        "| 2026-06-10 | 创建部署草稿 | 待确认 |\n",
        encoding="utf-8",
    )
    return path


class SfkCliTests(unittest.TestCase):
    def make_project(self) -> tempfile.TemporaryDirectory[str]:
        return tempfile.TemporaryDirectory()

    def init_project(self, project_dir: Path) -> None:
        run_sfk(project_dir, "init")

    def create_module(self, project_dir: Path) -> None:
        run_sfk(project_dir, "module", "create", MODULE_NAME, "--id", MODULE_ID)

    def module_state(self, project_dir: Path) -> dict:
        return load_json(project_dir / ".sfk" / "modules" / MODULE_ID / "state.json")

    def test_mvp_state_lifecycle(self) -> None:
        with self.make_project() as tmp:
            project_dir = Path(tmp)

            run_sfk(project_dir, "init")
            run_sfk(project_dir, "status")
            run_sfk(project_dir, "module", "create", MODULE_NAME, "--id", MODULE_ID)
            run_sfk(project_dir, "module", "list")
            run_sfk(project_dir, "module", "status")
            run_sfk(project_dir, "config", "set", "pluginName", "flow")
            run_sfk(project_dir, "config", "set", "userName", "阿杰")
            run_sfk(project_dir, "config", "show")
            current = run_sfk(project_dir, "artifact", "current", "requirement")

            index_path = project_dir / ".sfk" / "index.json"
            state_path = project_dir / ".sfk" / "modules" / MODULE_ID / "state.json"
            self.assertTrue(index_path.exists())
            self.assertTrue(state_path.exists())

            index = load_json(index_path)
            self.assertEqual(index["currentModule"], MODULE_ID)
            self.assertEqual(index["modules"][MODULE_ID]["docsPath"], f"docs/super-flow-kit/{MODULE_ID}/")
            self.assertEqual(index["globalConfig"]["pluginName"], "flow")
            self.assertEqual(index["globalConfig"]["userName"], "阿杰")

            payload = json.loads(current.stdout)
            self.assertEqual(payload["moduleId"], MODULE_ID)
            self.assertEqual(payload["phase"], "requirement")
            self.assertEqual(payload["status"], "pending")
            self.assertIsNone(payload["currentFile"])
            self.assertEqual(payload["files"], [])

    def test_artifact_draft_confirm_updates_state_and_document(self) -> None:
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)
            doc_path = write_requirement_doc(project_dir)

            draft = run_sfk(project_dir, "artifact", "draft", "requirement", REQ_DOC)
            self.assertIn("documentCheck", draft.stdout)
            self.assertIn("qualityCheck：passed", draft.stdout)

            state = self.module_state(project_dir)
            artifact = state["artifacts"]["requirement"]
            self.assertEqual(artifact["status"], "in_progress")
            self.assertEqual(artifact["quality"], "draft")
            self.assertEqual(artifact["files"][-1], REQ_DOC)
            self.assertNotIn("\\", artifact["files"][-1])
            self.assertFalse(Path(artifact["files"][-1]).is_absolute())

            text = doc_path.read_text(encoding="utf-8")
            self.assertIn("## 1. 文档信息", text)
            self.assertIn("## 2. 项目/业务/代码上下文", text)
            self.assertIn("| 质量状态 | draft |", text)

            git_env = {
                "GIT_CONFIG_COUNT": "1",
                "GIT_CONFIG_KEY_0": "user.name",
                "GIT_CONFIG_VALUE_0": "Test Owner",
            }
            confirmed = run_sfk(project_dir, "artifact", "confirm", "requirement", env=git_env)
            self.assertIn("documentCheck", confirmed.stdout)
            self.assertIn("qualityCheck：passed", confirmed.stdout)
            self.assertIn("owner：Test Owner", confirmed.stdout)

            state = self.module_state(project_dir)
            artifact = state["artifacts"]["requirement"]
            self.assertEqual(artifact["status"], "done")
            self.assertEqual(artifact["quality"], "confirmed")
            self.assertTrue(artifact["confirmedAt"])
            self.assertEqual(artifact["owner"], "Test Owner")

            text = doc_path.read_text(encoding="utf-8")
            self.assertIn("| 质量状态 | confirmed |", text)
            self.assertIn("| 2026-06-10 | 创建需求草稿 | Test Owner |", text)
            self.assertIn("密码策略待确认", text)

    def test_requirement_artifact_requires_required_sections(self) -> None:
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)
            doc_path = project_dir / REQ_DOC
            doc_path.parent.mkdir(parents=True, exist_ok=True)
            doc_path.write_text(
                "# 用户管理需求分析\n\n"
                "## 文档信息\n\n"
                "| 质量状态 | pending |\n\n"
                "## 背景与目标\n\n"
                "只包含背景，缺少其他必备章节。\n",
                encoding="utf-8",
            )

            result = run_sfk(project_dir, "artifact", "draft", "requirement", REQ_DOC, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("需求分析文档质量检查未通过", result.stderr)
            self.assertIn("缺少必备章节", result.stderr)
            artifact = self.module_state(project_dir)["artifacts"]["requirement"]
            self.assertEqual(artifact["status"], "pending")
            self.assertEqual(artifact["files"], [])

    def test_requirement_placeholder_warnings_block_confirm(self) -> None:
        git_env = {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "user.name",
            "GIT_CONFIG_VALUE_0": "Test Owner",
        }
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)
            doc_path = write_requirement_doc(project_dir)
            text = doc_path.read_text(encoding="utf-8")
            doc_path.write_text(
                text.replace(
                    "为用户提供稳定的登录入口，并为后续权限能力奠定基础。",
                    "[说明为什么要做这个功能，以及期望达成什么业务或产品目标。]",
                ),
                encoding="utf-8",
            )

            draft = run_sfk(project_dir, "artifact", "draft", "requirement", REQ_DOC)
            self.assertIn("qualityCheck：warnings", draft.stdout)
            self.assertIn("模板占位符", draft.stdout)
            confirm = run_sfk(project_dir, "artifact", "confirm", "requirement", check=False)
            self.assertNotEqual(confirm.returncode, 0)
            self.assertIn("模板占位符", confirm.stderr)
            artifact = self.module_state(project_dir)["artifacts"]["requirement"]
            self.assertEqual(artifact["status"], "in_progress")
            self.assertEqual(artifact["quality"], "draft")

            doc_path.write_text(
                doc_path.read_text(encoding="utf-8").replace(
                    "[说明为什么要做这个功能，以及期望达成什么业务或产品目标。]",
                    "为用户提供稳定的登录入口，并为后续权限能力奠定基础。",
                ),
                encoding="utf-8",
            )
            confirmed = run_sfk(project_dir, "artifact", "confirm", "requirement", env=git_env)
            self.assertIn("qualityCheck：passed", confirmed.stdout)
            artifact = self.module_state(project_dir)["artifacts"]["requirement"]
            self.assertEqual(artifact["status"], "done")
            self.assertEqual(artifact["quality"], "confirmed")

    def test_requirement_artifact_rejects_missing_empty_and_non_markdown_files(self) -> None:
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)

            missing = run_sfk(project_dir, "artifact", "draft", "requirement", REQ_DOC, check=False)
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn("需求分析文档不存在", missing.stderr)

            empty_path = project_dir / REQ_DOC
            empty_path.parent.mkdir(parents=True, exist_ok=True)
            empty_path.write_text("", encoding="utf-8")
            empty = run_sfk(project_dir, "artifact", "draft", "requirement", REQ_DOC, check=False)
            self.assertNotEqual(empty.returncode, 0)
            self.assertIn("需求分析文档为空", empty.stderr)

            text_path = f"docs/super-flow-kit/{MODULE_ID}/req.txt"
            (project_dir / text_path).write_text("not markdown\n", encoding="utf-8")
            non_md = run_sfk(project_dir, "artifact", "draft", "requirement", text_path, check=False)
            self.assertNotEqual(non_md.returncode, 0)
            self.assertIn("必须是 Markdown", non_md.stderr)
            artifact = self.module_state(project_dir)["artifacts"]["requirement"]
            self.assertEqual(artifact["status"], "pending")
            self.assertEqual(artifact["files"], [])

    def test_init_is_idempotent_and_does_not_overwrite_existing_state(self) -> None:
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)

            second = run_sfk(project_dir, "init")
            self.assertIn("已初始化", second.stdout)

            index = load_json(project_dir / ".sfk" / "index.json")
            self.assertEqual(index["currentModule"], MODULE_ID)
            self.assertIn(MODULE_ID, index["modules"])

    def test_module_validation_rejects_duplicate_and_invalid_ids(self) -> None:
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)

            invalid = run_sfk(
                project_dir,
                "module",
                "create",
                MODULE_NAME,
                "--id",
                "UserManagement",
                check=False,
            )
            self.assertNotEqual(invalid.returncode, 0)
            self.assertIn("moduleId 只能包含", invalid.stderr)

            self.create_module(project_dir)
            duplicate = run_sfk(
                project_dir,
                "module",
                "create",
                "用户管理2",
                "--id",
                MODULE_ID,
                check=False,
            )
            self.assertNotEqual(duplicate.returncode, 0)
            self.assertIn("moduleId 已存在", duplicate.stderr)

    def test_artifact_rejects_paths_outside_project_root(self) -> None:
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)

            result = run_sfk(project_dir, "artifact", "draft", "requirement", "../outside.md", check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("产出物路径必须位于当前项目根目录内", result.stderr)

    def test_confirm_without_draft_fails(self) -> None:
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)

            result = run_sfk(project_dir, "artifact", "confirm", "requirement", check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("没有可确认的阶段产出物", result.stderr)

    def test_tui_select_non_interactive_returns_machine_readable_json(self) -> None:
        with self.make_project() as tmp:
            project_dir = Path(tmp)

            result = run_sfk(
                project_dir,
                "tui",
                "select",
                "--title",
                "选择方案",
                "--mode",
                "single",
                "--option",
                "mvp=MVP方案",
                "--option",
                "full=完整方案",
            )
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "non_interactive")
            self.assertEqual(payload["mode"], "single")
            self.assertEqual(payload["selected"], [])
            self.assertEqual(
                payload["options"],
                [
                    {"key": "mvp", "label": "MVP方案"},
                    {"key": "full", "label": "完整方案"},
                ],
            )

    def test_phase_check_allows_ui_with_soft_missing_requirement(self) -> None:
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)

            result = run_sfk(project_dir, "phase", "check", "ui_design")
            payload = json.loads(result.stdout)
            self.assertEqual(payload["moduleId"], MODULE_ID)
            self.assertEqual(payload["phase"], "ui_design")
            self.assertFalse(payload["blocked"])
            self.assertTrue(payload["canContinue"])
            self.assertEqual(payload["hardMissing"], [])
            self.assertEqual(payload["softMissing"][0]["phase"], "requirement")
            self.assertEqual(payload["softMissing"][0]["reason"], "missing")

    def test_phase_check_hard_dependencies_require_confirmed_non_empty_artifacts(self) -> None:
        git_env = {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "user.name",
            "GIT_CONFIG_VALUE_0": "Test Owner",
        }
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)

            result = run_sfk(project_dir, "phase", "check", "system_design")
            payload = json.loads(result.stdout)
            self.assertTrue(payload["blocked"])
            self.assertEqual(payload["hardMissing"][0]["phase"], "requirement")
            self.assertEqual(payload["hardMissing"][0]["reason"], "missing")

            write_requirement_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "requirement", REQ_DOC)
            result = run_sfk(project_dir, "phase", "check", "system_design")
            payload = json.loads(result.stdout)
            self.assertTrue(payload["blocked"])
            self.assertEqual(payload["hardMissing"][0]["reason"], "draft")

            run_sfk(project_dir, "artifact", "confirm", "requirement", env=git_env)
            result = run_sfk(project_dir, "phase", "check", "system_design")
            payload = json.loads(result.stdout)
            self.assertFalse(payload["blocked"])
            self.assertEqual(payload["hardMissing"], [])

            (project_dir / REQ_DOC).write_text("", encoding="utf-8")
            result = run_sfk(project_dir, "phase", "check", "system_design")
            payload = json.loads(result.stdout)
            self.assertTrue(payload["blocked"])
            self.assertEqual(payload["hardMissing"][0]["reason"], "file_empty")

            (project_dir / REQ_DOC).unlink()
            result = run_sfk(project_dir, "phase", "check", "system_design")
            payload = json.loads(result.stdout)
            self.assertTrue(payload["blocked"])
            self.assertEqual(payload["hardMissing"][0]["reason"], "file_missing")

    def test_ui_design_artifact_reuses_generic_draft_confirm_flow(self) -> None:
        git_env = {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "user.name",
            "GIT_CONFIG_VALUE_0": "Test Owner",
        }
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)
            doc_path = write_ui_doc(project_dir)

            run_sfk(project_dir, "artifact", "draft", "ui_design", UI_DOC)
            state = self.module_state(project_dir)
            artifact = state["artifacts"]["ui_design"]
            self.assertEqual(artifact["status"], "in_progress")
            self.assertEqual(artifact["quality"], "draft")
            self.assertEqual(artifact["files"][-1], UI_DOC)
            self.assertNotIn("\\", artifact["files"][-1])
            self.assertFalse(Path(artifact["files"][-1]).is_absolute())

            text = doc_path.read_text(encoding="utf-8")
            self.assertIn("## 1. 文档信息", text)
            self.assertIn("| 质量状态 | draft |", text)

            run_sfk(project_dir, "artifact", "confirm", "ui_design", env=git_env)
            state = self.module_state(project_dir)
            artifact = state["artifacts"]["ui_design"]
            self.assertEqual(artifact["status"], "done")
            self.assertEqual(artifact["quality"], "confirmed")
            self.assertEqual(artifact["owner"], "Test Owner")

            text = doc_path.read_text(encoding="utf-8")
            self.assertIn("| 质量状态 | confirmed |", text)
            self.assertIn("| 2026-06-10 | 创建 UI 草稿 | Test Owner |", text)

    def test_system_design_artifact_reuses_generic_draft_confirm_flow(self) -> None:
        git_env = {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "user.name",
            "GIT_CONFIG_VALUE_0": "Test Owner",
        }
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)
            write_requirement_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "requirement", REQ_DOC)
            run_sfk(project_dir, "artifact", "confirm", "requirement", env=git_env)
            doc_path = write_system_design_doc(project_dir)

            draft = run_sfk(project_dir, "artifact", "draft", "system_design", SYS_DOC)
            self.assertIn("qualityCheck：passed", draft.stdout)
            state = self.module_state(project_dir)
            artifact = state["artifacts"]["system_design"]
            self.assertEqual(artifact["status"], "in_progress")
            self.assertEqual(artifact["quality"], "draft")
            self.assertEqual(artifact["files"][-1], SYS_DOC)
            self.assertNotIn("\\", artifact["files"][-1])
            self.assertFalse(Path(artifact["files"][-1]).is_absolute())

            text = doc_path.read_text(encoding="utf-8")
            self.assertIn("## 1. 文档信息", text)
            self.assertIn("| 质量状态 | draft |", text)

            confirmed = run_sfk(project_dir, "artifact", "confirm", "system_design", env=git_env)
            self.assertIn("qualityCheck：passed", confirmed.stdout)
            state = self.module_state(project_dir)
            artifact = state["artifacts"]["system_design"]
            self.assertEqual(artifact["status"], "done")
            self.assertEqual(artifact["quality"], "confirmed")
            self.assertEqual(artifact["owner"], "Test Owner")

            text = doc_path.read_text(encoding="utf-8")
            self.assertIn("| 质量状态 | confirmed |", text)
            self.assertIn("| 2026-06-10 | 创建系统设计草稿 | Test Owner |", text)

    def test_system_design_artifact_enforces_hard_requirement_dependency(self) -> None:
        git_env = {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "user.name",
            "GIT_CONFIG_VALUE_0": "Test Owner",
        }
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)
            write_system_design_doc(project_dir)

            missing = run_sfk(project_dir, "artifact", "draft", "system_design", SYS_DOC, check=False)
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn("硬依赖未满足", missing.stderr)
            artifact = self.module_state(project_dir)["artifacts"]["system_design"]
            self.assertEqual(artifact["status"], "pending")
            self.assertEqual(artifact["files"], [])

            write_requirement_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "requirement", REQ_DOC)
            draft_requirement = run_sfk(project_dir, "artifact", "draft", "system_design", SYS_DOC, check=False)
            self.assertNotEqual(draft_requirement.returncode, 0)
            self.assertIn("draft", draft_requirement.stderr)
            artifact = self.module_state(project_dir)["artifacts"]["system_design"]
            self.assertEqual(artifact["status"], "pending")
            self.assertEqual(artifact["files"], [])

            run_sfk(project_dir, "artifact", "confirm", "requirement", env=git_env)
            success = run_sfk(project_dir, "artifact", "draft", "system_design", SYS_DOC)
            self.assertIn("qualityCheck：passed", success.stdout)

    def test_system_design_artifact_requires_required_sections(self) -> None:
        git_env = {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "user.name",
            "GIT_CONFIG_VALUE_0": "Test Owner",
        }
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)
            write_requirement_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "requirement", REQ_DOC)
            run_sfk(project_dir, "artifact", "confirm", "requirement", env=git_env)
            doc_path = project_dir / SYS_DOC
            doc_path.parent.mkdir(parents=True, exist_ok=True)
            doc_path.write_text(
                "# 用户管理系统设计\n\n"
                "## 文档信息\n\n"
                "| 质量状态 | pending |\n\n"
                "## 系统架构\n\n"
                "只有系统架构，缺少其他必备章节。\n",
                encoding="utf-8",
            )

            result = run_sfk(project_dir, "artifact", "draft", "system_design", SYS_DOC, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("缺少必备章节", result.stderr)
            self.assertIn("数据库设计", result.stderr)
            self.assertIn("API / 接口设计", result.stderr)
            artifact = self.module_state(project_dir)["artifacts"]["system_design"]
            self.assertEqual(artifact["status"], "pending")
            self.assertEqual(artifact["files"], [])

    def test_system_design_placeholder_warnings_block_confirm(self) -> None:
        git_env = {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "user.name",
            "GIT_CONFIG_VALUE_0": "Test Owner",
        }
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)
            write_requirement_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "requirement", REQ_DOC)
            run_sfk(project_dir, "artifact", "confirm", "requirement", env=git_env)
            doc_path = write_system_design_doc(project_dir)
            text = doc_path.read_text(encoding="utf-8")
            doc_path.write_text(text.replace("支持用户登录能力的服务端架构设计。", "[说明本次系统设计要解决的问题。]"), encoding="utf-8")

            draft = run_sfk(project_dir, "artifact", "draft", "system_design", SYS_DOC)
            self.assertIn("qualityCheck：warnings", draft.stdout)
            confirm = run_sfk(project_dir, "artifact", "confirm", "system_design", check=False)
            self.assertNotEqual(confirm.returncode, 0)
            self.assertIn("模板占位符", confirm.stderr)
            artifact = self.module_state(project_dir)["artifacts"]["system_design"]
            self.assertEqual(artifact["status"], "in_progress")
            self.assertEqual(artifact["quality"], "draft")

            doc_path.write_text(doc_path.read_text(encoding="utf-8").replace("[说明本次系统设计要解决的问题。]", "支持用户登录能力的服务端架构设计。"), encoding="utf-8")
            confirmed = run_sfk(project_dir, "artifact", "confirm", "system_design", env=git_env)
            self.assertIn("qualityCheck：passed", confirmed.stdout)

    def test_development_artifact_enforces_hard_requirement_and_system_design_dependencies(self) -> None:
        git_env = {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "user.name",
            "GIT_CONFIG_VALUE_0": "Test Owner",
        }
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)
            write_development_doc(project_dir)

            missing = run_sfk(project_dir, "artifact", "draft", "development", DEV_DOC, check=False)
            self.assertNotEqual(missing.returncode, 0)
            self.assertIn("硬依赖未满足", missing.stderr)
            artifact = self.module_state(project_dir)["artifacts"]["development"]
            self.assertEqual(artifact["status"], "pending")
            self.assertEqual(artifact["files"], [])

            write_requirement_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "requirement", REQ_DOC)
            run_sfk(project_dir, "artifact", "confirm", "requirement", env=git_env)
            missing_system = run_sfk(project_dir, "artifact", "draft", "development", DEV_DOC, check=False)
            self.assertNotEqual(missing_system.returncode, 0)
            self.assertIn("system_design", missing_system.stderr)

            write_system_design_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "system_design", SYS_DOC)
            run_sfk(project_dir, "artifact", "confirm", "system_design", env=git_env)
            phase = run_sfk(project_dir, "phase", "check", "development")
            payload = json.loads(phase.stdout)
            self.assertFalse(payload["blocked"])
            self.assertEqual(payload["hardMissing"], [])
            self.assertEqual(payload["softMissing"][0]["phase"], "ui_design")

            success = run_sfk(project_dir, "artifact", "draft", "development", DEV_DOC)
            self.assertIn("qualityCheck：passed", success.stdout)

    def test_development_artifact_reuses_generic_draft_confirm_flow(self) -> None:
        git_env = {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "user.name",
            "GIT_CONFIG_VALUE_0": "Test Owner",
        }
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)
            write_requirement_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "requirement", REQ_DOC)
            run_sfk(project_dir, "artifact", "confirm", "requirement", env=git_env)
            write_system_design_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "system_design", SYS_DOC)
            run_sfk(project_dir, "artifact", "confirm", "system_design", env=git_env)
            doc_path = write_development_doc(project_dir)

            draft = run_sfk(project_dir, "artifact", "draft", "development", DEV_DOC)
            self.assertIn("qualityCheck：passed", draft.stdout)
            state = self.module_state(project_dir)
            artifact = state["artifacts"]["development"]
            self.assertEqual(artifact["status"], "in_progress")
            self.assertEqual(artifact["quality"], "draft")
            self.assertEqual(artifact["files"][-1], DEV_DOC)
            self.assertNotIn("\\", artifact["files"][-1])
            self.assertFalse(Path(artifact["files"][-1]).is_absolute())

            text = doc_path.read_text(encoding="utf-8")
            self.assertIn("## 1. 文档信息", text)
            self.assertIn("| 质量状态 | draft |", text)

            confirmed = run_sfk(project_dir, "artifact", "confirm", "development", env=git_env)
            self.assertIn("qualityCheck：passed", confirmed.stdout)
            state = self.module_state(project_dir)
            artifact = state["artifacts"]["development"]
            self.assertEqual(artifact["status"], "done")
            self.assertEqual(artifact["quality"], "confirmed")
            self.assertEqual(artifact["owner"], "Test Owner")
            self.assertEqual(artifact["implementationApproval"]["status"], "pending")

            current = run_sfk(project_dir, "implementation", "current", "development")
            current_payload = json.loads(current.stdout)
            self.assertFalse(current_payload["canImplement"])
            self.assertEqual(current_payload["reason"], "implementation_approval_pending")

            text = doc_path.read_text(encoding="utf-8")
            self.assertIn("| 质量状态 | confirmed |", text)
            self.assertIn("| 2026-06-10 | 创建开发草稿 | Test Owner |", text)

    def test_implementation_approval_requires_confirmed_development_doc_and_is_auditable(self) -> None:
        git_env = {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "user.name",
            "GIT_CONFIG_VALUE_0": "Test Owner",
        }
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)

            current = run_sfk(project_dir, "implementation", "current", "development")
            payload = json.loads(current.stdout)
            self.assertFalse(payload["canImplement"])
            self.assertEqual(payload["reason"], "development_document_missing")

            empty_summary = run_sfk(project_dir, "implementation", "approve", "development", "--summary", "", check=False)
            self.assertNotEqual(empty_summary.returncode, 0)
            self.assertIn("授权摘要不能为空", empty_summary.stderr)

            write_requirement_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "requirement", REQ_DOC)
            run_sfk(project_dir, "artifact", "confirm", "requirement", env=git_env)
            write_system_design_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "system_design", SYS_DOC)
            run_sfk(project_dir, "artifact", "confirm", "system_design", env=git_env)
            write_development_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "development", DEV_DOC)

            draft_current = run_sfk(project_dir, "implementation", "current", "development")
            draft_payload = json.loads(draft_current.stdout)
            self.assertFalse(draft_payload["canImplement"])
            self.assertEqual(draft_payload["reason"], "development_document_draft")
            draft_approve = run_sfk(project_dir, "implementation", "approve", "development", "--summary", "实现登录接口", check=False)
            self.assertNotEqual(draft_approve.returncode, 0)
            self.assertIn("development_document_draft", draft_approve.stderr)

            run_sfk(project_dir, "artifact", "confirm", "development", env=git_env)
            approved = run_sfk(project_dir, "implementation", "approve", "development", "--summary", "按已确认开发文档实现登录接口", env=git_env)
            self.assertIn("源码实现二次确认已记录", approved.stdout)

            state = self.module_state(project_dir)
            artifact = state["artifacts"]["development"]
            approval = artifact["implementationApproval"]
            self.assertEqual(approval["status"], "approved")
            self.assertEqual(approval["approvedBy"], "Test Owner")
            self.assertEqual(approval["approvedForFile"], DEV_DOC)
            self.assertEqual(approval["approvedForConfirmedAt"], artifact["confirmedAt"])
            self.assertEqual(approval["summary"], "按已确认开发文档实现登录接口")
            self.assertTrue(approval["approvedAt"])
            self.assertEqual(state["history"][-1]["action"], "approve_development_implementation")

            current = run_sfk(project_dir, "implementation", "current", "development")
            payload = json.loads(current.stdout)
            self.assertTrue(payload["canImplement"])
            self.assertEqual(payload["reason"], "approved")

    def test_development_draft_resets_implementation_approval(self) -> None:
        git_env = {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "user.name",
            "GIT_CONFIG_VALUE_0": "Test Owner",
        }
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)
            write_requirement_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "requirement", REQ_DOC)
            run_sfk(project_dir, "artifact", "confirm", "requirement", env=git_env)
            write_system_design_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "system_design", SYS_DOC)
            run_sfk(project_dir, "artifact", "confirm", "system_design", env=git_env)
            write_development_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "development", DEV_DOC)
            run_sfk(project_dir, "artifact", "confirm", "development", env=git_env)
            run_sfk(project_dir, "implementation", "approve", "development", "--summary", "实现登录接口", env=git_env)
            self.assertEqual(self.module_state(project_dir)["artifacts"]["development"]["implementationApproval"]["status"], "approved")

            run_sfk(project_dir, "artifact", "draft", "development", DEV_DOC)
            artifact = self.module_state(project_dir)["artifacts"]["development"]
            self.assertEqual(artifact["implementationApproval"]["status"], "pending")
            current = run_sfk(project_dir, "implementation", "current", "development")
            payload = json.loads(current.stdout)
            self.assertFalse(payload["canImplement"])
            self.assertEqual(payload["reason"], "development_document_draft")

    def test_development_artifact_requires_required_sections(self) -> None:
        git_env = {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "user.name",
            "GIT_CONFIG_VALUE_0": "Test Owner",
        }
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)
            write_requirement_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "requirement", REQ_DOC)
            run_sfk(project_dir, "artifact", "confirm", "requirement", env=git_env)
            write_system_design_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "system_design", SYS_DOC)
            run_sfk(project_dir, "artifact", "confirm", "system_design", env=git_env)
            doc_path = project_dir / DEV_DOC
            doc_path.parent.mkdir(parents=True, exist_ok=True)
            doc_path.write_text(
                "# 用户管理开发文档\n\n"
                "## 文档信息\n\n"
                "| 质量状态 | pending |\n\n"
                "## 开发目标与范围\n\n"
                "只包含目标，缺少其他必备章节。\n",
                encoding="utf-8",
            )

            result = run_sfk(project_dir, "artifact", "draft", "development", DEV_DOC, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("开发文档质量检查未通过", result.stderr)
            self.assertIn("缺少必备章节", result.stderr)
            self.assertIn("API 设计依据", result.stderr)
            self.assertIn("数据库设计依据", result.stderr)

    def test_development_placeholder_warnings_block_confirm(self) -> None:
        git_env = {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "user.name",
            "GIT_CONFIG_VALUE_0": "Test Owner",
        }
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)
            write_requirement_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "requirement", REQ_DOC)
            run_sfk(project_dir, "artifact", "confirm", "requirement", env=git_env)
            write_system_design_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "system_design", SYS_DOC)
            run_sfk(project_dir, "artifact", "confirm", "system_design", env=git_env)
            doc_path = write_development_doc(project_dir)
            text = doc_path.read_text(encoding="utf-8")
            doc_path.write_text(text.replace("实现用户登录开发计划，不直接声明代码已经完成。", "[说明本次开发要完成的目标。]"), encoding="utf-8")

            draft = run_sfk(project_dir, "artifact", "draft", "development", DEV_DOC)
            self.assertIn("qualityCheck：warnings", draft.stdout)
            self.assertIn("模板占位符", draft.stdout)
            confirm = run_sfk(project_dir, "artifact", "confirm", "development", check=False)
            self.assertNotEqual(confirm.returncode, 0)
            self.assertIn("模板占位符", confirm.stderr)
            artifact = self.module_state(project_dir)["artifacts"]["development"]
            self.assertEqual(artifact["status"], "in_progress")
            self.assertEqual(artifact["quality"], "draft")

            doc_path.write_text(doc_path.read_text(encoding="utf-8").replace("[说明本次开发要完成的目标。]", "实现用户登录开发计划，不直接声明代码已经完成。"), encoding="utf-8")
            confirmed = run_sfk(project_dir, "artifact", "confirm", "development", env=git_env)
            self.assertIn("qualityCheck：passed", confirmed.stdout)

    def test_testing_artifact_enforces_hard_requirement_dependency(self) -> None:
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)
            write_testing_doc(project_dir)

            result = run_sfk(project_dir, "artifact", "draft", "testing", TEST_DOC, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("硬依赖未满足", result.stderr)
            self.assertIn("requirement", result.stderr)
            artifact = self.module_state(project_dir)["artifacts"]["testing"]
            self.assertEqual(artifact["status"], "pending")
            self.assertEqual(artifact["files"], [])

    def test_testing_phase_check_allows_missing_soft_dependencies(self) -> None:
        git_env = {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "user.name",
            "GIT_CONFIG_VALUE_0": "Test Owner",
        }
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)
            write_requirement_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "requirement", REQ_DOC)
            run_sfk(project_dir, "artifact", "confirm", "requirement", env=git_env)

            result = run_sfk(project_dir, "phase", "check", "testing")
            payload = json.loads(result.stdout)
            self.assertFalse(payload["blocked"])
            self.assertTrue(payload["canContinue"])
            self.assertEqual(payload["hardMissing"], [])
            self.assertEqual({item["phase"] for item in payload["softMissing"]}, {"development", "system_design"})

    def test_testing_artifact_reuses_generic_draft_confirm_flow(self) -> None:
        git_env = {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "user.name",
            "GIT_CONFIG_VALUE_0": "Test Owner",
        }
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)
            write_requirement_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "requirement", REQ_DOC)
            run_sfk(project_dir, "artifact", "confirm", "requirement", env=git_env)
            doc_path = write_testing_doc(project_dir)

            draft = run_sfk(project_dir, "artifact", "draft", "testing", TEST_DOC)
            self.assertIn("qualityCheck：passed", draft.stdout)
            state = self.module_state(project_dir)
            artifact = state["artifacts"]["testing"]
            self.assertEqual(artifact["status"], "in_progress")
            self.assertEqual(artifact["quality"], "draft")
            self.assertEqual(artifact["files"][-1], TEST_DOC)
            self.assertNotIn("\\", artifact["files"][-1])
            self.assertFalse(Path(artifact["files"][-1]).is_absolute())
            self.assertNotIn("implementationApproval", artifact)

            text = doc_path.read_text(encoding="utf-8")
            self.assertIn("## 1. 文档信息", text)
            self.assertIn("| 质量状态 | draft |", text)

            confirmed = run_sfk(project_dir, "artifact", "confirm", "testing", env=git_env)
            self.assertIn("qualityCheck：passed", confirmed.stdout)
            state = self.module_state(project_dir)
            artifact = state["artifacts"]["testing"]
            self.assertEqual(artifact["status"], "done")
            self.assertEqual(artifact["quality"], "confirmed")
            self.assertEqual(artifact["owner"], "Test Owner")
            self.assertNotIn("implementationApproval", artifact)
            self.assertEqual(state["artifacts"]["development"]["implementationApproval"]["status"], "pending")

            text = doc_path.read_text(encoding="utf-8")
            self.assertIn("| 质量状态 | confirmed |", text)
            self.assertIn("| 2026-06-10 | 创建测试草稿 | Test Owner |", text)

    def test_testing_artifact_requires_required_sections(self) -> None:
        git_env = {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "user.name",
            "GIT_CONFIG_VALUE_0": "Test Owner",
        }
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)
            write_requirement_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "requirement", REQ_DOC)
            run_sfk(project_dir, "artifact", "confirm", "requirement", env=git_env)
            doc_path = project_dir / TEST_DOC
            doc_path.parent.mkdir(parents=True, exist_ok=True)
            doc_path.write_text(
                "# 用户管理测试文档\n\n"
                "## 文档信息\n\n"
                "| 质量状态 | pending |\n\n"
                "## 测试目标与范围\n\n"
                "只包含目标，缺少其他必备章节。\n",
                encoding="utf-8",
            )

            result = run_sfk(project_dir, "artifact", "draft", "testing", TEST_DOC, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("测试文档质量检查未通过", result.stderr)
            self.assertIn("缺少必备章节", result.stderr)
            self.assertIn("验收结论", result.stderr)
            artifact = self.module_state(project_dir)["artifacts"]["testing"]
            self.assertEqual(artifact["status"], "pending")
            self.assertEqual(artifact["files"], [])

    def test_testing_placeholder_warnings_block_confirm(self) -> None:
        git_env = {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "user.name",
            "GIT_CONFIG_VALUE_0": "Test Owner",
        }
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)
            write_requirement_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "requirement", REQ_DOC)
            run_sfk(project_dir, "artifact", "confirm", "requirement", env=git_env)
            doc_path = write_testing_doc(project_dir)
            text = doc_path.read_text(encoding="utf-8")
            doc_path.write_text(text.replace("验证用户登录需求的核心路径、失败反馈和基础安全约束。", "[说明本次测试目标。]"), encoding="utf-8")

            draft = run_sfk(project_dir, "artifact", "draft", "testing", TEST_DOC)
            self.assertIn("qualityCheck：warnings", draft.stdout)
            self.assertIn("模板占位符", draft.stdout)
            confirm = run_sfk(project_dir, "artifact", "confirm", "testing", check=False)
            self.assertNotEqual(confirm.returncode, 0)
            self.assertIn("模板占位符", confirm.stderr)
            artifact = self.module_state(project_dir)["artifacts"]["testing"]
            self.assertEqual(artifact["status"], "in_progress")
            self.assertEqual(artifact["quality"], "draft")

            doc_path.write_text(doc_path.read_text(encoding="utf-8").replace("[说明本次测试目标。]", "验证用户登录需求的核心路径、失败反馈和基础安全约束。"), encoding="utf-8")
            confirmed = run_sfk(project_dir, "artifact", "confirm", "testing", env=git_env)
            self.assertIn("qualityCheck：passed", confirmed.stdout)

    def test_status_suggests_system_design_and_reserved_development_next_steps(self) -> None:
        git_env = {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "user.name",
            "GIT_CONFIG_VALUE_0": "Test Owner",
        }
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)

            write_requirement_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "requirement", REQ_DOC)
            run_sfk(project_dir, "artifact", "confirm", "requirement", env=git_env)
            status = run_sfk(project_dir, "status")
            self.assertIn("/sfk-ui", status.stdout)
            self.assertIn("/sfk-design", status.stdout)

            write_ui_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "ui_design", UI_DOC)
            run_sfk(project_dir, "artifact", "confirm", "ui_design", env=git_env)
            status = run_sfk(project_dir, "status")
            self.assertIn("/sfk-design", status.stdout)
            self.assertNotIn("后续阶段预留，尚未完整实现", status.stdout)

            write_system_design_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "system_design", SYS_DOC)
            status = run_sfk(project_dir, "status")
            self.assertIn("继续使用 /sfk-design", status.stdout)

            run_sfk(project_dir, "artifact", "confirm", "system_design", env=git_env)
            status = run_sfk(project_dir, "status")
            self.assertIn("/sfk-dev", status.stdout)
            self.assertNotIn("/sfk-dev（后续阶段预留，尚未完整实现）", status.stdout)

            write_development_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "development", DEV_DOC)
            status = run_sfk(project_dir, "status")
            self.assertIn("继续使用 /sfk-dev", status.stdout)

            run_sfk(project_dir, "artifact", "confirm", "development", env=git_env)
            status = run_sfk(project_dir, "status")
            self.assertIn("源码实现二次确认", status.stdout)
            self.assertIn("实现授权:pending", status.stdout)

            run_sfk(project_dir, "implementation", "approve", "development", "--summary", "实现用户管理开发计划", env=git_env)
            status = run_sfk(project_dir, "status")
            self.assertIn("/sfk-test", status.stdout)
            self.assertIn("实现授权:approved", status.stdout)
            self.assertNotIn("/sfk-test（后续阶段预留，尚未完整实现）", status.stdout)

            write_testing_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "testing", TEST_DOC)
            status = run_sfk(project_dir, "status")
            self.assertIn("继续使用 /sfk-test", status.stdout)

            run_sfk(project_dir, "artifact", "confirm", "testing", env=git_env)
            status = run_sfk(project_dir, "status")
            self.assertIn("/sfk-deploy", status.stdout)

            write_deployment_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "deployment", DEPLOY_DOC)
            status = run_sfk(project_dir, "status")
            self.assertIn("继续使用 /sfk-deploy", status.stdout)

            run_sfk(project_dir, "artifact", "confirm", "deployment", env=git_env)
            status = run_sfk(project_dir, "status")
            self.assertIn("核心交付流程已完成", status.stdout)

    def test_context_discover_identifies_new_project(self) -> None:
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)

            result = run_sfk(project_dir, "context", "discover", "--phase", "requirement")
            payload = json.loads(result.stdout)
            self.assertEqual(payload["projectKind"], "new_project")
            self.assertEqual(payload["phase"], "requirement")
            self.assertEqual(payload["moduleId"], MODULE_ID)
            for group in ("manifests", "businessDocs", "sourceDirs", "codeFiles", "sfkArtifacts"):
                for item in payload["evidence"][group]:
                    self.assertNotIn("\\", item)
                    self.assertFalse(Path(item).is_absolute())
            for group in payload["evidence"]["architecture"].values():
                self.assertEqual(group, [])

    def test_context_discover_identifies_business_docs_without_sfk_artifacts(self) -> None:
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)
            (project_dir / "README.md").write_text("# Existing product\n", encoding="utf-8")
            (project_dir / "docs").mkdir(exist_ok=True)
            (project_dir / "docs" / "product.md").write_text("# Product doc\n", encoding="utf-8")
            write_requirement_doc(project_dir)

            result = run_sfk(project_dir, "context", "discover", "--phase", "requirement")
            payload = json.loads(result.stdout)
            self.assertEqual(payload["projectKind"], "existing_business_docs")
            self.assertIn("README.md", payload["evidence"]["businessDocs"])
            self.assertIn("docs/product.md", payload["evidence"]["businessDocs"])
            self.assertNotIn(REQ_DOC, payload["evidence"]["businessDocs"])
            self.assertIn(REQ_DOC, payload["evidence"]["sfkArtifacts"])

    def test_context_discover_identifies_existing_ui_code_and_ignores_skipped_dirs(self) -> None:
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)
            (project_dir / "package.json").write_text('{"dependencies":{"react":"latest"}}\n', encoding="utf-8")
            (project_dir / "src" / "components").mkdir(parents=True)
            (project_dir / "src" / "components" / "Button.tsx").write_text("export function Button() { return <button /> }\n", encoding="utf-8")
            (project_dir / "src" / "pages").mkdir(parents=True)
            (project_dir / "src" / "pages" / "Login.tsx").write_text("export default function Login() { return null }\n", encoding="utf-8")
            (project_dir / "src" / "styles").mkdir(parents=True)
            (project_dir / "src" / "styles" / "globals.css").write_text("@tailwind base;\n", encoding="utf-8")
            (project_dir / "tailwind.config.js").write_text("module.exports = {}\n", encoding="utf-8")
            (project_dir / "node_modules" / "fake").mkdir(parents=True)
            (project_dir / "node_modules" / "fake" / "Ignored.tsx").write_text("export const Ignored = 1\n", encoding="utf-8")
            (project_dir / ".sfk" / "fake").mkdir(parents=True, exist_ok=True)
            (project_dir / ".sfk" / "fake" / "Ignored.tsx").write_text("export const Ignored = 1\n", encoding="utf-8")

            result = run_sfk(project_dir, "context", "discover", "--phase", "ui_design")
            payload = json.loads(result.stdout)
            self.assertEqual(payload["projectKind"], "existing_ui_code")
            self.assertTrue(payload["evidence"]["ui"]["hasUiCode"])
            self.assertIn("package.json", payload["evidence"]["manifests"])
            self.assertIn("src/components/Button.tsx", payload["evidence"]["ui"]["representativeFiles"])
            self.assertIn("src/styles/globals.css", payload["evidence"]["ui"]["styleFiles"])
            self.assertIn("tailwind.config.js", payload["evidence"]["ui"]["designSystemFiles"])
            flattened = json.dumps(payload, ensure_ascii=False)
            self.assertNotIn("node_modules/fake/Ignored.tsx", flattened)
            self.assertNotIn(".sfk/fake/Ignored.tsx", flattened)

    def test_context_discover_identifies_system_design_architecture_evidence(self) -> None:
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)
            (project_dir / "package.json").write_text('{"scripts":{"test":"vitest"}}\n', encoding="utf-8")
            (project_dir / "src" / "api").mkdir(parents=True)
            (project_dir / "src" / "api" / "routes.ts").write_text("export const routes = []\n", encoding="utf-8")
            (project_dir / "src" / "services").mkdir(parents=True)
            (project_dir / "src" / "services" / "auth.ts").write_text("export const auth = {}\n", encoding="utf-8")
            (project_dir / "src" / "server.ts").write_text("export function start() {}\n", encoding="utf-8")
            (project_dir / "prisma").mkdir(parents=True)
            (project_dir / "prisma" / "schema.prisma").write_text("model User { id String @id }\n", encoding="utf-8")
            (project_dir / "tests").mkdir(parents=True)
            (project_dir / "tests" / "auth.test.ts").write_text("test('auth', () => {})\n", encoding="utf-8")
            (project_dir / "Dockerfile").write_text("FROM python:3.12\n", encoding="utf-8")

            result = run_sfk(project_dir, "context", "discover", "--phase", "system_design")
            payload = json.loads(result.stdout)
            architecture = payload["evidence"]["architecture"]
            self.assertIn("src/server.ts", architecture["entrypointFiles"])
            self.assertIn("package.json", architecture["configFiles"])
            self.assertIn("src/api/routes.ts", architecture["apiFiles"])
            self.assertIn("src/services/auth.ts", architecture["serviceFiles"])
            self.assertIn("prisma/schema.prisma", architecture["dataFiles"])
            self.assertIn("tests/auth.test.ts", architecture["testFiles"])
            self.assertIn("Dockerfile", architecture["deployFiles"])

    def test_artifact_impact_reports_downstream_ui_review(self) -> None:
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)
            write_requirement_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "requirement", REQ_DOC)
            write_ui_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "ui_design", UI_DOC)

            result = run_sfk(project_dir, "artifact", "impact", "requirement")
            payload = json.loads(result.stdout)
            ui_impact = next(item for item in payload["downstream"] if item["phase"] == "ui_design")
            self.assertTrue(payload["shouldWarnBeforeChange"])
            self.assertTrue(ui_impact["needsReview"])
            self.assertEqual(ui_impact["currentFile"], UI_DOC)
            self.assertNotIn("\\", ui_impact["currentFile"])

    def test_artifact_impact_without_downstream_outputs_no_warning(self) -> None:
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)
            write_requirement_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "requirement", REQ_DOC)

            result = run_sfk(project_dir, "artifact", "impact", "requirement")
            payload = json.loads(result.stdout)
            self.assertFalse(payload["shouldWarnBeforeChange"])
            self.assertTrue(all(not item["needsReview"] for item in payload["downstream"]))

    def test_artifact_impact_reports_ui_downstream_review_and_rejects_unknown_phase(self) -> None:
        git_env = {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "user.name",
            "GIT_CONFIG_VALUE_0": "Test Owner",
        }
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)
            write_requirement_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "requirement", REQ_DOC)
            run_sfk(project_dir, "artifact", "confirm", "requirement", env=git_env)
            write_ui_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "ui_design", UI_DOC)
            write_system_design_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "system_design", SYS_DOC)
            run_sfk(project_dir, "artifact", "confirm", "system_design", env=git_env)
            write_development_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "development", DEV_DOC)

            result = run_sfk(project_dir, "artifact", "impact", "ui_design")
            payload = json.loads(result.stdout)
            development = next(item for item in payload["downstream"] if item["phase"] == "development")
            self.assertTrue(payload["shouldWarnBeforeChange"])
            self.assertTrue(development["needsReview"])

            unknown = run_sfk(project_dir, "artifact", "impact", "unknown", check=False)
            self.assertNotEqual(unknown.returncode, 0)
            self.assertIn("未知阶段", unknown.stderr)

    def test_artifact_impact_reports_system_design_downstream_review(self) -> None:
        git_env = {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "user.name",
            "GIT_CONFIG_VALUE_0": "Test Owner",
        }
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)
            write_requirement_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "requirement", REQ_DOC)
            run_sfk(project_dir, "artifact", "confirm", "requirement", env=git_env)
            write_system_design_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "system_design", SYS_DOC)
            run_sfk(project_dir, "artifact", "confirm", "system_design", env=git_env)
            write_development_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "development", DEV_DOC)

            result = run_sfk(project_dir, "artifact", "impact", "system_design")
            payload = json.loads(result.stdout)
            development = next(item for item in payload["downstream"] if item["phase"] == "development")
            self.assertTrue(payload["shouldWarnBeforeChange"])
            self.assertTrue(development["needsReview"])
            self.assertIn("开发实现", development["reason"])
            self.assertIn("API / 接口设计", development["reason"])
            self.assertIn("数据库设计", development["reason"])

    def test_artifact_impact_reports_development_downstream_review(self) -> None:
        git_env = {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "user.name",
            "GIT_CONFIG_VALUE_0": "Test Owner",
        }
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)
            write_requirement_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "requirement", REQ_DOC)
            run_sfk(project_dir, "artifact", "confirm", "requirement", env=git_env)
            write_system_design_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "system_design", SYS_DOC)
            run_sfk(project_dir, "artifact", "confirm", "system_design", env=git_env)
            write_development_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "development", DEV_DOC)
            write_testing_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "testing", TEST_DOC)

            result = run_sfk(project_dir, "artifact", "impact", "development")
            payload = json.loads(result.stdout)
            testing = next(item for item in payload["downstream"] if item["phase"] == "testing")
            self.assertTrue(payload["shouldWarnBeforeChange"])
            self.assertTrue(testing["needsReview"])
            self.assertIn("测试覆盖", testing["reason"])
            self.assertIn("部署配置", testing["reason"])
            self.assertIn("回滚", testing["reason"])

    def test_artifact_impact_reports_testing_downstream_deployment_review(self) -> None:
        git_env = {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "user.name",
            "GIT_CONFIG_VALUE_0": "Test Owner",
        }
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)
            write_requirement_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "requirement", REQ_DOC)
            run_sfk(project_dir, "artifact", "confirm", "requirement", env=git_env)
            write_testing_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "testing", TEST_DOC)
            run_sfk(project_dir, "artifact", "confirm", "testing", env=git_env)
            deploy_doc = f"docs/super-flow-kit/{MODULE_ID}/20260610143000-{MODULE_ID}-部署文档.md"
            write_deployment_doc(project_dir, deploy_doc)
            run_sfk(project_dir, "artifact", "draft", "deployment", deploy_doc)

            result = run_sfk(project_dir, "artifact", "impact", "testing")
            payload = json.loads(result.stdout)
            deployment = next(item for item in payload["downstream"] if item["phase"] == "deployment")
            self.assertTrue(payload["shouldWarnBeforeChange"])
            self.assertTrue(deployment["needsReview"])
            self.assertIn("部署准入", deployment["reason"])
            self.assertIn("回归范围", deployment["reason"])
            self.assertIn("回滚策略", deployment["reason"])
            self.assertEqual(self.module_state(project_dir)["artifacts"]["deployment"]["status"], "in_progress")

    def test_deployment_phase_check_treats_testing_as_soft_dependency(self) -> None:
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)

            result = run_sfk(project_dir, "phase", "check", "deployment")
            payload = json.loads(result.stdout)
            self.assertFalse(payload["blocked"])
            self.assertTrue(payload["canContinue"])
            self.assertEqual(payload["hardMissing"], [])
            self.assertEqual({item["phase"] for item in payload["softMissing"]}, {"testing", "system_design"})

    def test_deployment_readiness_reports_all_modules_testing_status(self) -> None:
        git_env = {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "user.name",
            "GIT_CONFIG_VALUE_0": "Test Owner",
        }
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)

            result = run_sfk(project_dir, "deployment", "readiness")
            payload = json.loads(result.stdout)
            self.assertEqual(payload["totalModules"], 1)
            self.assertFalse(payload["allModulesTestingConfirmed"])
            self.assertEqual(payload["notReady"][0]["moduleId"], MODULE_ID)
            self.assertEqual(payload["notReady"][0]["reason"], "missing")

            write_requirement_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "requirement", REQ_DOC)
            run_sfk(project_dir, "artifact", "confirm", "requirement", env=git_env)
            write_testing_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "testing", TEST_DOC)
            draft = json.loads(run_sfk(project_dir, "deployment", "readiness").stdout)
            self.assertFalse(draft["allModulesTestingConfirmed"])
            self.assertEqual(draft["notReady"][0]["reason"], "draft")

            run_sfk(project_dir, "artifact", "confirm", "testing", env=git_env)
            ready = json.loads(run_sfk(project_dir, "deployment", "readiness").stdout)
            self.assertTrue(ready["allModulesTestingConfirmed"])
            self.assertEqual(ready["readyModules"], 1)
            self.assertEqual(ready["notReadyModules"], 0)

            (project_dir / TEST_DOC).write_text("", encoding="utf-8")
            empty = json.loads(run_sfk(project_dir, "deployment", "readiness").stdout)
            self.assertFalse(empty["allModulesTestingConfirmed"])
            self.assertEqual(empty["notReady"][0]["reason"], "file_empty")

    def test_deployment_readiness_reports_multi_module_gaps(self) -> None:
        git_env = {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "user.name",
            "GIT_CONFIG_VALUE_0": "Test Owner",
        }
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)
            write_requirement_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "requirement", REQ_DOC)
            run_sfk(project_dir, "artifact", "confirm", "requirement", env=git_env)
            write_testing_doc(project_dir)
            run_sfk(project_dir, "artifact", "draft", "testing", TEST_DOC)
            run_sfk(project_dir, "artifact", "confirm", "testing", env=git_env)

            run_sfk(project_dir, "module", "create", "订单管理", "--id", "order-management")
            result = run_sfk(project_dir, "deployment", "readiness")
            payload = json.loads(result.stdout)
            self.assertEqual(payload["totalModules"], 2)
            self.assertFalse(payload["allModulesTestingConfirmed"])
            self.assertEqual(payload["readyModules"], 1)
            self.assertEqual(payload["notReadyModules"], 1)
            self.assertEqual(payload["notReady"][0]["moduleId"], "order-management")

    def test_deployment_artifact_reuses_generic_draft_confirm_flow(self) -> None:
        git_env = {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "user.name",
            "GIT_CONFIG_VALUE_0": "Test Owner",
        }
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)
            doc_path = write_deployment_doc(project_dir)

            draft = run_sfk(project_dir, "artifact", "draft", "deployment", DEPLOY_DOC)
            self.assertIn("qualityCheck：passed", draft.stdout)
            state = self.module_state(project_dir)
            artifact = state["artifacts"]["deployment"]
            self.assertEqual(artifact["status"], "in_progress")
            self.assertEqual(artifact["quality"], "draft")
            self.assertEqual(artifact["files"][-1], DEPLOY_DOC)
            self.assertNotIn("\\", artifact["files"][-1])
            self.assertFalse(Path(artifact["files"][-1]).is_absolute())

            text = doc_path.read_text(encoding="utf-8")
            self.assertIn("## 1. 文档信息", text)
            self.assertIn("| 质量状态 | draft |", text)

            confirmed = run_sfk(project_dir, "artifact", "confirm", "deployment", env=git_env)
            self.assertIn("qualityCheck：passed", confirmed.stdout)
            state = self.module_state(project_dir)
            artifact = state["artifacts"]["deployment"]
            self.assertEqual(artifact["status"], "done")
            self.assertEqual(artifact["quality"], "confirmed")
            self.assertEqual(artifact["owner"], "Test Owner")
            self.assertNotIn("implementationApproval", artifact)

            text = doc_path.read_text(encoding="utf-8")
            self.assertIn("| 质量状态 | confirmed |", text)
            self.assertIn("| 2026-06-10 | 创建部署草稿 | Test Owner |", text)

    def test_deployment_artifact_requires_required_sections(self) -> None:
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)
            doc_path = project_dir / DEPLOY_DOC
            doc_path.parent.mkdir(parents=True, exist_ok=True)
            doc_path.write_text(
                "# 用户管理部署文档\n\n"
                "## 文档信息\n\n"
                "| 质量状态 | pending |\n\n"
                "## 部署目标与范围\n\n"
                "只包含部署目标，缺少其他必备章节。\n",
                encoding="utf-8",
            )

            result = run_sfk(project_dir, "artifact", "draft", "deployment", DEPLOY_DOC, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("部署上线文档质量检查未通过", result.stderr)
            self.assertIn("缺少必备章节", result.stderr)
            self.assertIn("全模块测试准入检查", result.stderr)
            artifact = self.module_state(project_dir)["artifacts"]["deployment"]
            self.assertEqual(artifact["status"], "pending")
            self.assertEqual(artifact["files"], [])

    def test_deployment_placeholder_warnings_block_confirm(self) -> None:
        git_env = {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "user.name",
            "GIT_CONFIG_VALUE_0": "Test Owner",
        }
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)
            doc_path = write_deployment_doc(project_dir)
            text = doc_path.read_text(encoding="utf-8")
            doc_path.write_text(text.replace("规划用户管理模块在测试确认后的部署上线步骤，不执行真实部署。", "[说明部署目标。]"), encoding="utf-8")

            draft = run_sfk(project_dir, "artifact", "draft", "deployment", DEPLOY_DOC)
            self.assertIn("qualityCheck：warnings", draft.stdout)
            self.assertIn("模板占位符", draft.stdout)
            confirm = run_sfk(project_dir, "artifact", "confirm", "deployment", check=False)
            self.assertNotEqual(confirm.returncode, 0)
            self.assertIn("模板占位符", confirm.stderr)
            artifact = self.module_state(project_dir)["artifacts"]["deployment"]
            self.assertEqual(artifact["status"], "in_progress")
            self.assertEqual(artifact["quality"], "draft")

            doc_path.write_text(doc_path.read_text(encoding="utf-8").replace("[说明部署目标。]", "规划用户管理模块在测试确认后的部署上线步骤，不执行真实部署。"), encoding="utf-8")
            confirmed = run_sfk(project_dir, "artifact", "confirm", "deployment", env=git_env)
            self.assertIn("qualityCheck：passed", confirmed.stdout)

    def test_context_discover_deployment_reports_deploy_files(self) -> None:
        with self.make_project() as tmp:
            project_dir = Path(tmp)
            self.init_project(project_dir)
            self.create_module(project_dir)
            (project_dir / "Dockerfile").write_text("FROM python:3.12\n", encoding="utf-8")
            workflow_dir = project_dir / ".github" / "workflows"
            workflow_dir.mkdir(parents=True)
            (workflow_dir / "deploy.yml").write_text("name: deploy\n", encoding="utf-8")

            result = run_sfk(project_dir, "context", "discover", "--phase", "deployment")
            payload = json.loads(result.stdout)
            self.assertEqual(payload["phase"], "deployment")
            deploy_files = payload["evidence"]["architecture"]["deployFiles"]
            self.assertIn("Dockerfile", deploy_files)
            self.assertIn(".github/workflows/deploy.yml", deploy_files)

    def test_command_docs_do_not_use_fixed_custom_options(self) -> None:
        command_paths = [
            REPO_ROOT / ".claude" / "commands" / "sfk-req.md",
            REPO_ROOT / ".claude" / "commands" / "sfk-ui.md",
            REPO_ROOT / ".claude" / "commands" / "sfk-design.md",
            REPO_ROOT / ".claude" / "commands" / "sfk-dev.md",
            REPO_ROOT / ".claude" / "commands" / "sfk-test.md",
            REPO_ROOT / ".claude" / "commands" / "sfk-deploy.md",
        ]
        forbidden_line_patterns = [
            re.compile(r"^\s*-\s*(自定义|其他)(\s|$)"),
            re.compile(r"--option\s+custom"),
            re.compile(r"custom=其他"),
        ]
        for path in command_paths:
            for line in path.read_text(encoding="utf-8").splitlines():
                for pattern in forbidden_line_patterns:
                    self.assertIsNone(pattern.search(line), f"{path}: {line}")
        dev_doc = (REPO_ROOT / ".claude" / "commands" / "sfk-dev.md").read_text(encoding="utf-8")
        self.assertIn("implementation approve development", dev_doc)
        self.assertIn("Gate C", dev_doc)
        self.assertIn("Gate B 只确认开发文档", dev_doc)


if __name__ == "__main__":
    unittest.main()
