#!/usr/bin/env python3
"""super-flow-kit v0.1 state utility.

This script intentionally uses only Python standard library so the plugin can run
without jq/npm dependencies in Claude Code environments.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

SCHEMA_VERSION = "1.0.0"
PHASES = [
    ("requirement", "需求分析"),
    ("ui_design", "UI 设计"),
    ("system_design", "系统设计"),
    ("development", "软件开发"),
    ("testing", "功能测试"),
    ("deployment", "部署上线"),
]
DEFAULT_CONFIG = {
    "pluginName": "sfk",
    "userName": "小主",
    "defaultStrategy": "draft",
    "autoSave": True,
    "verbose": True,
}
MODULE_ID_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
COMMON_SLUGS = {
    "用户认证": "user-auth",
    "用户登录": "user-login",
    "登录": "login",
    "支付模块": "payment-module",
    "支付": "payment",
    "订单模块": "order-module",
    "订单": "order",
}


class SfkError(Exception):
    pass


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def root() -> Path:
    return Path.cwd()


def rel(path: Path) -> str:
    try:
        value = path.resolve().relative_to(root().resolve()).as_posix()
    except ValueError:
        value = path.as_posix()
    return value


def normalize_artifact_file(value: str) -> str:
    raw = value.strip()
    if not raw:
        raise SfkError("产出物路径不能为空。")
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = root() / candidate
    project_root = root().resolve()
    resolved = candidate.resolve(strict=False)
    try:
        return resolved.relative_to(project_root).as_posix()
    except ValueError as exc:
        raise SfkError("产出物路径必须位于当前项目根目录内，请使用项目相对路径。") from exc


def index_path() -> Path:
    return root() / ".sfk" / "index.json"


def state_path(module_id: str) -> Path:
    return root() / ".sfk" / "modules" / module_id / "state.json"


def docs_dir(module_id: str) -> Path:
    return root() / "docs" / "super-flow-kit" / module_id


def current_owner(index: dict[str, Any]) -> str:
    try:
        result = subprocess.run(
            ["git", "config", "user.name"],
            cwd=root(),
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        git_name = result.stdout.strip()
        if result.returncode == 0 and git_name:
            return git_name
    except (OSError, subprocess.SubprocessError):
        pass
    return str(index.get("globalConfig", {}).get("userName") or DEFAULT_CONFIG["userName"])


def fill_latest_change_owner_in_lines(lines: list[str], owner: str) -> bool:
    for index in range(len(lines) - 1, -1, -1):
        line = lines[index]
        if not line.startswith("|") or "---" in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 3 or cells[0] in {"时间", "Time"}:
            continue
        if cells[-1] in {"待确认", "<负责人或待确认>", ""}:
            cells[-1] = owner
            lines[index] = "| " + " | ".join(cells) + " |"
            return True
        break
    return False


def fill_latest_change_owner(file_path: str, owner: str) -> bool:
    path = root() / file_path
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    changed = fill_latest_change_owner_in_lines(lines, owner)
    if changed:
        trailing_newline = "\n" if text.endswith("\n") else ""
        path.write_text("\n".join(lines) + trailing_newline, encoding="utf-8")
    return changed


def renumber_markdown_headings(lines: list[str]) -> tuple[list[str], bool]:
    counters: dict[int, int] = {}
    changed = False
    updated: list[str] = []
    heading_re = re.compile(r"^(#{2,6})\s+(\d+(?:\.\d+)*)([.、]?)\s+(.+)$")
    for line in lines:
        match = heading_re.match(line)
        if not match:
            updated.append(line)
            continue
        hashes, old_number, punctuation, title = match.groups()
        level = len(hashes)
        if level == 2:
            counters = {2: counters.get(2, 0) + 1}
            expected = str(counters[2])
        else:
            parent = counters.get(level - 1)
            if parent is None:
                updated.append(line)
                continue
            for key in list(counters):
                if key > level:
                    counters.pop(key, None)
            counters[level] = counters.get(level, 0) + 1
            parts = [str(counters[i]) for i in range(2, level + 1) if i in counters]
            expected = ".".join(parts)
        expected_text = f"{expected}." if level == 2 else expected
        current_text = old_number + punctuation
        if current_text != expected_text:
            line = f"{hashes} {expected_text} {title}"
            changed = True
        updated.append(line)
    return updated, changed


def replace_doc_info_value(lines: list[str], field: str, value: str) -> bool:
    changed = False
    pattern = re.compile(rf"^(\|\s*{re.escape(field)}\s*\|\s*)(.*?)(\s*\|)$")
    for index, line in enumerate(lines):
        match = pattern.match(line)
        if not match:
            continue
        new_line = f"{match.group(1)}{value}{match.group(3)}"
        if new_line != line:
            lines[index] = new_line
            changed = True
        break
    return changed


def check_artifact_document(file_path: str, phase: str, artifact: dict[str, Any], owner: str | None = None) -> list[str]:
    path = root() / file_path
    if not path.exists() or path.suffix.lower() != ".md":
        return []
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    fixes: list[str] = []

    lines, heading_changed = renumber_markdown_headings(lines)
    if heading_changed:
        fixes.append("修复 Markdown 标题编号")

    quality = artifact.get("quality")
    if quality in {"draft", "confirmed"} and replace_doc_info_value(lines, "质量状态", str(quality)):
        fixes.append("同步文档质量状态")

    if artifact.get("status") == "done" and artifact.get("quality") == "confirmed" and owner:
        if fill_latest_change_owner_in_lines(lines, owner):
            fixes.append("回填变更记录负责人")

    if fixes:
        trailing_newline = "\n" if text.endswith("\n") else ""
        path.write_text("\n".join(lines) + trailing_newline, encoding="utf-8")
    return fixes


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SfkError(f"状态文件不存在：{rel(path)}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SfkError(f"状态文件不是合法 JSON：{rel(path)}，{exc}") from exc


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def require_index() -> dict[str, Any]:
    data = read_json(index_path())
    if data.get("schemaVersion") != SCHEMA_VERSION:
        raise SfkError(f"不支持的 schemaVersion：{data.get('schemaVersion')}")
    data.setdefault("globalConfig", DEFAULT_CONFIG.copy())
    data.setdefault("modules", {})
    return data


def require_current_state(index: dict[str, Any] | None = None) -> tuple[dict[str, Any], dict[str, Any], str]:
    index = index or require_index()
    module_id = index.get("currentModule")
    if not module_id:
        raise SfkError("当前项目还没有当前模块，请先执行：/sfk-module create <名称>")
    modules = index.get("modules", {})
    if module_id not in modules:
        raise SfkError(f"currentModule 指向不存在的模块：{module_id}")
    state = read_json(state_path(module_id))
    if state.get("schemaVersion") != SCHEMA_VERSION:
        raise SfkError(f"模块状态 schemaVersion 不支持：{state.get('schemaVersion')}")
    return index, state, module_id


def validate_module_id(module_id: str) -> None:
    if not MODULE_ID_RE.fullmatch(module_id):
        raise SfkError("moduleId 只能包含小写字母、数字、连字符，且不能以连字符开头或结尾。")


def suggest_module_id(display_name: str) -> str:
    text = display_name.strip()
    if text in COMMON_SLUGS:
        return COMMON_SLUGS[text]
    candidate = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()
    if candidate and MODULE_ID_RE.fullmatch(candidate):
        return candidate
    raise SfkError(
        "脚本层无法可靠生成 moduleId。请通过 /sfk-module create <名称> 让 Claude 在交互中推荐，"
        "或使用 --id 显式指定，例如：--id user-management"
    )


def phase_template() -> dict[str, Any]:
    return {
        phase_id: {
            "status": "pending",
            "quality": None,
            "files": [],
            "version": None,
            "updatedAt": None,
            "confirmedAt": None,
            "owner": None,
        }
        for phase_id, _ in PHASES
    }


def new_state(module_id: str, display_name: str) -> dict[str, Any]:
    timestamp = now_iso()
    return {
        "schemaVersion": SCHEMA_VERSION,
        "module": {
            "moduleId": module_id,
            "displayName": display_name,
            "createdAt": timestamp,
            "updatedAt": timestamp,
            "version": "0.1.0",
            "owner": None,
            "collaborators": [],
        },
        "currentPhase": "requirement",
        "dependencies": [],
        "artifacts": phase_template(),
        "history": [
            {
                "action": "create_module",
                "timestamp": timestamp,
                "user": None,
                "detail": f"创建模块：{display_name}",
            }
        ],
    }


def command_init(args: argparse.Namespace) -> None:
    path = index_path()
    if path.exists():
        print("✅ 当前项目已初始化 super-flow-kit。")
        print(f"状态文件：{rel(path)}")
        print("下一步建议：/sfk-status")
        return

    timestamp = now_iso()
    (root() / ".sfk" / "modules").mkdir(parents=True, exist_ok=True)
    (root() / "docs" / "super-flow-kit").mkdir(parents=True, exist_ok=True)
    data = {
        "schemaVersion": SCHEMA_VERSION,
        "project": {
            "name": args.name or root().name or "当前项目",
            "createdAt": timestamp,
            "updatedAt": timestamp,
            "root": ".",
        },
        "currentModule": None,
        "modules": {},
        "globalConfig": DEFAULT_CONFIG.copy(),
    }
    write_json(path, data)
    print("✅ super-flow-kit 初始化完成。")
    print("已创建：")
    print("  - .sfk/index.json")
    print("  - .sfk/modules/")
    print("  - docs/super-flow-kit/")
    print("下一步建议：/sfk-module create 用户管理")
    print("提示：创建模块时会在交互中推荐 moduleId；无法可靠推荐时再补充 --id。")


def module_create(args: argparse.Namespace) -> None:
    index = require_index()
    display_name = " ".join(args.name).strip()
    if not display_name:
        raise SfkError("模块名称不能为空。")
    auto_suggested = args.id is None
    module_id = args.id or suggest_module_id(display_name)
    validate_module_id(module_id)
    modules = index.setdefault("modules", {})
    if module_id in modules:
        raise SfkError(f"moduleId 已存在：{module_id}")
    for existing in modules.values():
        if existing.get("displayName") == display_name:
            raise SfkError(f"displayName 已存在：{display_name}")

    docs_dir(module_id).mkdir(parents=True, exist_ok=True)
    state = new_state(module_id, display_name)
    write_json(state_path(module_id), state)

    timestamp = now_iso()
    modules[module_id] = {
        "moduleId": module_id,
        "displayName": display_name,
        "statePath": rel(state_path(module_id)),
        "docsPath": rel(docs_dir(module_id)) + "/",
        "status": "active",
        "owner": None,
        "currentPhase": "requirement",
        "updatedAt": timestamp,
    }
    index["currentModule"] = module_id
    index.setdefault("project", {})["updatedAt"] = timestamp
    write_json(index_path(), index)

    print(f"✅ 已创建模块：【{display_name}】")
    if auto_suggested:
        print(f"moduleId：{module_id}（脚本自动生成）")
    else:
        print(f"moduleId：{module_id}")
    print(f"状态文件：{rel(state_path(module_id))}")
    print(f"产出物目录：{rel(docs_dir(module_id))}/")
    print("下一步建议：/sfk-req <需求描述>")


def module_list(_: argparse.Namespace) -> None:
    index = require_index()
    modules = index.get("modules", {})
    current = index.get("currentModule")
    if not modules:
        print("当前还没有模块。")
        print("下一步建议：/sfk-module create 用户管理")
        print("提示：创建模块时会在交互中推荐 moduleId；无法可靠推荐时再补充 --id。")
        return
    print("📦 模块列表：")
    for module_id, item in modules.items():
        marker = "✅" if module_id == current else "⬜"
        print(f"  {marker} {item.get('displayName')}（{module_id}）- 当前阶段：{item.get('currentPhase', 'requirement')}")


def module_switch(args: argparse.Namespace) -> None:
    index = require_index()
    target = " ".join(args.target).strip()
    modules = index.get("modules", {})
    matches = [mid for mid, item in modules.items() if mid == target or item.get("displayName") == target]
    if not matches:
        raise SfkError(f"没有找到模块：{target}")
    if len(matches) > 1:
        raise SfkError(f"匹配到多个模块，请使用 moduleId：{', '.join(matches)}")
    module_id = matches[0]
    if not state_path(module_id).exists():
        raise SfkError(f"模块状态文件缺失：{rel(state_path(module_id))}")
    index["currentModule"] = module_id
    index.setdefault("project", {})["updatedAt"] = now_iso()
    write_json(index_path(), index)
    item = modules[module_id]
    print(f"✅ 已切换当前模块：{item.get('displayName')}（{module_id}）")
    print("下一步建议：/sfk-status")


def phase_summary(artifact: dict[str, Any]) -> str:
    status = artifact.get("status", "pending")
    quality = artifact.get("quality")
    files = artifact.get("files") or []
    file_text = files[-1] if files else ""
    quality_text = f" {quality}" if quality else ""
    return f"{status}{quality_text} {file_text}".rstrip()


def module_status(_: argparse.Namespace) -> None:
    index, state, module_id = require_current_state()
    module = state.get("module", {})
    print(f"📋 当前模块：{module.get('displayName')}（{module_id}）")
    print(f"当前阶段：{state.get('currentPhase', 'requirement')}")
    print("阶段状态：")
    artifacts = state.get("artifacts", {})
    for phase_id, phase_name in PHASES:
        print(f"  - {phase_name}：{phase_summary(artifacts.get(phase_id, {}))}")


def render_status(_: argparse.Namespace) -> None:
    index = require_index()
    cfg = index.get("globalConfig", DEFAULT_CONFIG)
    user_name = cfg.get("userName", "小主")
    plugin_name = cfg.get("pluginName", "sfk")
    print(f"嗨！{user_name}，{plugin_name} 在呢～")
    print("\n📊 super-flow-kit 工作流看板")
    print(f"项目：{index.get('project', {}).get('name', '当前项目')}")
    modules = index.get("modules", {})
    current = index.get("currentModule")
    if not modules:
        print("\n当前项目已初始化，但还没有模块。")
        print("下一步建议：/sfk-module create 用户管理")
        print("提示：创建模块时会在交互中推荐 moduleId；无法可靠推荐时再补充 --id。")
        return
    print(f"当前模块：{current}")
    print("\n📦 模块列表：")
    for module_id, item in modules.items():
        marker = "✅" if module_id == current else "⬜"
        print(f"  {marker} {item.get('displayName')}（{module_id}）")
    try:
        _, state, module_id = require_current_state(index)
    except SfkError as exc:
        print(f"\n⚠️ 当前模块状态异常：{exc}")
        return
    module = state.get("module", {})
    print(f"\n📋 当前模块详情：{module.get('displayName')}（{module_id}）")
    artifacts = state.get("artifacts", {})
    for phase_id, phase_name in PHASES:
        print(f"  - {phase_name}：{phase_summary(artifacts.get(phase_id, {}))}")
    print("\n💡 下一步建议：/sfk-req <需求描述> 或 /sfk-module status")


def config_show(_: argparse.Namespace) -> None:
    index = require_index()
    print("🔧 当前配置：")
    for key, value in index.get("globalConfig", DEFAULT_CONFIG).items():
        print(f"  - {key}: {value}")


def config_set(args: argparse.Namespace) -> None:
    index = require_index()
    key = args.key
    value = args.value
    if key not in {"pluginName", "userName"}:
        raise SfkError("v0.1 仅支持设置 pluginName 和 userName。")
    if not value.strip():
        raise SfkError("配置值不能为空。")
    index.setdefault("globalConfig", DEFAULT_CONFIG.copy())[key] = value.strip()
    index.setdefault("project", {})["updatedAt"] = now_iso()
    write_json(index_path(), index)
    print(f"✅ 已更新配置：{key} = {value.strip()}")


def artifact_current(args: argparse.Namespace) -> None:
    _, state, module_id = require_current_state()
    phase = args.phase
    if phase not in dict(PHASES):
        raise SfkError(f"未知阶段：{phase}")
    artifact = state.get("artifacts", {}).get(phase, {})
    files = artifact.get("files") or []
    current_file = files[-1] if files else None
    print(json.dumps({
        "moduleId": module_id,
        "phase": phase,
        "status": artifact.get("status", "pending"),
        "quality": artifact.get("quality"),
        "currentFile": current_file,
        "files": files,
        "updatedAt": artifact.get("updatedAt"),
        "confirmedAt": artifact.get("confirmedAt"),
    }, ensure_ascii=False, indent=2))


def artifact_update(args: argparse.Namespace, confirmed: bool) -> None:
    index, state, module_id = require_current_state()
    phase = args.phase
    if phase not in dict(PHASES):
        raise SfkError(f"未知阶段：{phase}")
    artifact = state.setdefault("artifacts", {}).setdefault(phase, {})
    timestamp = now_iso()
    if confirmed:
        files = artifact.get("files") or []
        if not files:
            raise SfkError("没有可确认的阶段产出物。请先保存草稿后再确认。")
        owner = current_owner(index)
        artifact["status"] = "done"
        artifact["quality"] = "confirmed"
        artifact["confirmedAt"] = timestamp
        artifact["owner"] = owner
        artifact["version"] = artifact.get("version") or "1.0.0"
        action = f"confirm_{phase}"
        detail = f"确认阶段产出物：{phase}"
    else:
        owner = None
        file_path = normalize_artifact_file(args.file)
        artifact["status"] = "in_progress"
        artifact["quality"] = "draft"
        files = artifact.setdefault("files", [])
        if file_path not in files:
            files.append(file_path)
        artifact["confirmedAt"] = None
        artifact["version"] = artifact.get("version") or "0.1.0"
        action = f"draft_{phase}"
        detail = f"保存阶段草稿：{phase}"
    artifact["updatedAt"] = timestamp
    artifact.setdefault("owner", None)
    check_fixes: list[str] = []
    for artifact_file in artifact.get("files", []):
        check_fixes.extend(check_artifact_document(artifact_file, phase, artifact, owner))
    state["currentPhase"] = phase
    state.setdefault("module", {})["updatedAt"] = timestamp
    state.setdefault("history", []).append({
        "action": action,
        "timestamp": timestamp,
        "user": owner,
        "detail": detail,
        "files": artifact.get("files", []),
    })
    write_json(state_path(module_id), state)
    index.setdefault("modules", {}).setdefault(module_id, {})["currentPhase"] = phase
    index["modules"][module_id]["updatedAt"] = timestamp
    index.setdefault("project", {})["updatedAt"] = timestamp
    write_json(index_path(), index)
    print("✅ 阶段状态已更新。")
    print(f"阶段：{phase}")
    print(f"status：{artifact.get('status')}")
    print(f"quality：{artifact.get('quality')}")
    if check_fixes:
        print("documentCheck：fixed")
        for fix in sorted(set(check_fixes)):
            print(f"  - {fix}")
    else:
        print("documentCheck：passed")
    if confirmed:
        print(f"owner：{artifact.get('owner')}")


def tui_select(args: argparse.Namespace) -> None:
    import sfk_tui

    code = sfk_tui.run_select(args)
    if code != 0:
        raise SfkError("TUI 选择命令执行失败。")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sfk", description="super-flow-kit v0.1 状态工具")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init")
    p_init.add_argument("name", nargs="?")
    p_init.set_defaults(func=command_init)

    p_status = sub.add_parser("status")
    p_status.set_defaults(func=render_status)

    p_module = sub.add_parser("module")
    module_sub = p_module.add_subparsers(dest="module_command", required=True)
    p_create = module_sub.add_parser("create")
    p_create.add_argument("name", nargs="+")
    p_create.add_argument("--id")
    p_create.set_defaults(func=module_create)
    p_list = module_sub.add_parser("list")
    p_list.set_defaults(func=module_list)
    p_switch = module_sub.add_parser("switch")
    p_switch.add_argument("target", nargs="+")
    p_switch.set_defaults(func=module_switch)
    p_mstatus = module_sub.add_parser("status")
    p_mstatus.set_defaults(func=module_status)

    p_config = sub.add_parser("config")
    config_sub = p_config.add_subparsers(dest="config_command")
    p_show = config_sub.add_parser("show")
    p_show.set_defaults(func=config_show)
    p_set = config_sub.add_parser("set")
    p_set.add_argument("key")
    p_set.add_argument("value")
    p_set.set_defaults(func=config_set)
    p_config.set_defaults(func=config_show)

    p_artifact = sub.add_parser("artifact")
    artifact_sub = p_artifact.add_subparsers(dest="artifact_command", required=True)
    p_current = artifact_sub.add_parser("current")
    p_current.add_argument("phase")
    p_current.set_defaults(func=artifact_current)
    p_draft = artifact_sub.add_parser("draft")
    p_draft.add_argument("phase")
    p_draft.add_argument("file")
    p_draft.set_defaults(func=lambda args: artifact_update(args, confirmed=False))
    p_confirm = artifact_sub.add_parser("confirm")
    p_confirm.add_argument("phase")
    p_confirm.set_defaults(func=lambda args: artifact_update(args, confirmed=True))

    p_tui = sub.add_parser("tui")
    tui_sub = p_tui.add_subparsers(dest="tui_command", required=True)
    p_select = tui_sub.add_parser("select")
    p_select.add_argument("--title", required=True)
    p_select.add_argument("--description")
    p_select.add_argument("--mode", choices=["single", "multi"], default="single")
    p_select.add_argument("--option", action="append", required=True, help="选项，格式为 key=label，可重复。")
    p_select.add_argument("--default", action="append", help="默认选中的选项 key，可重复。")
    p_select.set_defaults(func=tui_select)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
        return 0
    except SfkError as exc:
        print(f"⚠️ {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
