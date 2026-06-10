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
        "## 9. 需求范围\n\n"
        "- 用户可以登录。\n\n"
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
        "## 11. 数据模型\n\n"
        "模块状态记录阶段、产出物、版本和历史。\n\n"
        "## 12. API / 接口设计\n\n"
        "CLI 接口通过 artifact draft 和 artifact confirm 更新产出物状态。\n\n"
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

            state = self.module_state(project_dir)
            artifact = state["artifacts"]["requirement"]
            self.assertEqual(artifact["status"], "in_progress")
            self.assertEqual(artifact["quality"], "draft")
            self.assertEqual(artifact["files"][-1], REQ_DOC)
            self.assertNotIn("\\", artifact["files"][-1])
            self.assertFalse(Path(artifact["files"][-1]).is_absolute())

            text = doc_path.read_text(encoding="utf-8")
            self.assertIn("## 1. 文档信息", text)
            self.assertIn("## 2. 需求范围", text)
            self.assertIn("| 质量状态 | draft |", text)

            git_env = {
                "GIT_CONFIG_COUNT": "1",
                "GIT_CONFIG_KEY_0": "user.name",
                "GIT_CONFIG_VALUE_0": "Test Owner",
            }
            confirmed = run_sfk(project_dir, "artifact", "confirm", "requirement", env=git_env)
            self.assertIn("documentCheck", confirmed.stdout)
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
            self.assertNotIn("待确认", text)

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
            self.assertIn("/sfk-dev（后续阶段预留，尚未完整实现）", status.stdout)

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
            dev_doc = f"docs/super-flow-kit/{MODULE_ID}/dev.md"
            (project_dir / dev_doc).write_text("# Dev doc\n", encoding="utf-8")
            run_sfk(project_dir, "artifact", "draft", "development", dev_doc)

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
            dev_doc = f"docs/super-flow-kit/{MODULE_ID}/dev.md"
            (project_dir / dev_doc).write_text("# Dev doc\n", encoding="utf-8")
            run_sfk(project_dir, "artifact", "draft", "development", dev_doc)

            result = run_sfk(project_dir, "artifact", "impact", "system_design")
            payload = json.loads(result.stdout)
            development = next(item for item in payload["downstream"] if item["phase"] == "development")
            self.assertTrue(payload["shouldWarnBeforeChange"])
            self.assertTrue(development["needsReview"])
            self.assertIn("开发实现", development["reason"])
            self.assertIn("接口/数据模型", development["reason"])

    def test_command_docs_do_not_use_fixed_custom_options(self) -> None:
        command_paths = [
            REPO_ROOT / ".claude" / "commands" / "sfk-req.md",
            REPO_ROOT / ".claude" / "commands" / "sfk-ui.md",
            REPO_ROOT / ".claude" / "commands" / "sfk-design.md",
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


if __name__ == "__main__":
    unittest.main()
