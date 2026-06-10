from __future__ import annotations

import json
import os
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
                "custom=其他",
            )
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "non_interactive")
            self.assertEqual(payload["mode"], "single")
            self.assertEqual(payload["selected"], [])
            self.assertEqual(
                payload["options"],
                [
                    {"key": "mvp", "label": "MVP方案"},
                    {"key": "custom", "label": "其他"},
                ],
            )


if __name__ == "__main__":
    unittest.main()
