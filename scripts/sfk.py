#!/usr/bin/env python3
"""super-flow-kit v0.1 state utility.

This script intentionally uses only Python standard library so the plugin can run
without jq/npm dependencies in Claude Code environments.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
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
    ("code_review", "代码审查"),
    ("testing", "功能测试"),
    ("deployment", "部署上线"),
]
PHASE_NAMES = dict(PHASES)
PHASE_COMMANDS = {
    "requirement": "/sfk-req",
    "ui_design": "/sfk-ui",
    "system_design": "/sfk-design",
    "development": "/sfk-dev",
    "code_review": "/sfk-code-review",
    "testing": "/sfk-test",
    "deployment": "/sfk-deploy",
}
PHASE_DEPENDENCIES = {
    "requirement": {"hard": [], "soft": []},
    "ui_design": {"hard": [], "soft": ["requirement"]},
    "system_design": {"hard": ["requirement"], "soft": []},
    "development": {"hard": ["requirement", "system_design"], "soft": ["ui_design"]},
    "code_review": {"hard": ["requirement", "system_design", "development"], "soft": ["ui_design"]},
    "testing": {"hard": ["requirement"], "soft": ["development", "system_design", "code_review"]},
    "deployment": {"hard": [], "soft": ["testing", "system_design"]},
}
DEFAULT_CONFIG = {
    "pluginName": "sfk",
    "userName": "小主",
    "defaultStrategy": "draft",
    "autoSave": True,
    "verbose": True,
}
RESET_CONFIRM_PHRASE = "确认重置"
RESET_SCOPES = {"current-module", "project"}
MODULE_ID_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$")
SKIP_DISCOVERY_DIRS = {
    ".git",
    ".sfk",
    "node_modules",
    "dist",
    "build",
    "coverage",
    ".venv",
    "venv",
    "__pycache__",
}
MANIFEST_NAMES = {
    "package.json",
    "pyproject.toml",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "tsconfig.json",
    "angular.json",
}
UI_EXTENSIONS = {".tsx", ".jsx", ".vue", ".svelte", ".html", ".css", ".scss", ".less"}
CODE_EXTENSIONS = {".py", ".js", ".ts", ".tsx", ".jsx", ".vue", ".svelte", ".go", ".rs", ".java", ".kt", ".cs", ".php", ".rb"}
UI_DIR_PARTS = {"app", "pages", "components", "layouts", "views", "routes", "styles", "assets", "public", "ui", "design"}
REQUIREMENT_REQUIRED_SECTIONS = [
    "文档信息",
    "项目/业务/代码上下文",
    "背景与目标",
    "用户画像与使用场景",
    "功能范围",
    "用户故事",
    "验收标准",
    "非功能需求",
    "下游影响分析",
    "风险与待确认问题",
    "变更记录",
]
REQUIREMENT_TEMPLATE_FIELDS = {
    "displayName",
    "moduleId",
    "version",
    "quality",
    "createdAt",
    "updatedAt",
    "owner",
}
REQUIREMENT_BRACKET_PLACEHOLDER_RE = re.compile(
    r"\[(?:全新项目|已有业务文档|已有代码|已有需求文档|列出|说明|从既有|"
    r"用户角色|完成某件事|获得某种价值|前置条件|用户行为|预期结果|"
    r"性能、安全、兼容性、可用性、可维护性等要求|UI 设计|系统设计|软件开发|功能测试|部署上线|"
    r"待确认问题|影响|建议)[^\]]*\]"
)
SYSTEM_DESIGN_REQUIRED_SECTIONS = [
    "文档信息",
    "设计目标与范围",
    "需求依据",
    "UI / 交互依据",
    "项目技术现状与约束",
    "技术选型",
    "系统架构",
    "模块划分",
    "数据库设计",
    "API / 接口设计",
    "权限与安全",
    "错误处理与可观测性",
    "性能与扩展性",
    "部署与运行约束",
    "风险与备选方案",
    "假设与待确认问题",
    "下游影响分析",
    "变更记录",
]
SYSTEM_DESIGN_TEMPLATE_FIELDS = {
    "displayName",
    "moduleId",
    "version",
    "quality",
    "createdAt",
    "updatedAt",
    "owner",
}
SYSTEM_DESIGN_BRACKET_PLACEHOLDER_RE = re.compile(
    r"\[(?:说明|引用|列出|全新项目|已有业务文档|已有代码|已有 UI 代码|"
    r"语言/框架/存储/队列/缓存/测试/部署|选型|理由|备选|待确认|"
    r"模块名称|职责|输入|输出|依赖|备注|实体名称|字段|创建/更新/删除/归档|存储或来源|约束|"
    r"实体名称|关键属性|表名|主键字段|字段名|字段类型|默认值|约束或业务含义|"
    r"一对多/唯一索引/普通索引/外键/复合约束|数据对象|创建时机|更新规则|删除或归档策略|迁移、回填或兼容策略|"
    r"接口名称|调用方|提供方|入参|出参|错误|权限|GET/POST/事件/RPC|路径或主题|权限要求|"
    r"字段、类型、必填性|字段、类型、状态|错误码或状态|反馈文案|重试/修正/联系支持|"
    r"认证方式|角色/权限/数据范围|审计记录|幂等键/去重规则|限流或防重策略|外部系统/事件|入站/出站|协议和数据格式|重试/补偿|版本或兼容性说明|"
    r"风险|影响|条件|缓解|问题|建议|是/否|动作)[^\]]*\]"
)
DEVELOPMENT_REQUIRED_SECTIONS = [
    "文档信息",
    "开发目标与范围",
    "需求依据",
    "系统设计依据",
    "API 设计依据",
    "数据库设计依据",
    "UI / 交互依据",
    "项目代码现状与约束",
    "实现任务拆解",
    "关键文件与改动计划",
    "接口 / 数据 / 状态变更",
    "错误处理、安全与可观测性",
    "测试与验证计划",
    "开发顺序与回滚策略",
    "实现前确认",
    "风险与待确认问题",
    "下游影响分析",
    "变更记录",
]
DEVELOPMENT_TEMPLATE_FIELDS = {
    "displayName",
    "moduleId",
    "version",
    "quality",
    "createdAt",
    "updatedAt",
    "owner",
}
DEVELOPMENT_BRACKET_PLACEHOLDER_RE = re.compile(
    r"\[(?:说明|引用|列出|全新项目|已有代码|已有 UI 代码|已有业务文档|"
    r"接口名称|新增/修改/复用/不涉及|请求、响应或事件载荷|错误码、鉴权、权限|备注|"
    r"表或数据对象|字段、索引、唯一约束|迁移、回填、兼容或不涉及|"
    r"任务名称|目标|步骤|依赖|完成标准|路径|新增/修改/删除/不涉及|说明计划改动|风险|"
    r"变更项|接口/数据/状态/配置|影响范围|兼容或迁移策略|"
    r"单元测试/集成测试/手工验证/静态检查|覆盖范围|通过标准|序号|开发动作|前置条件|回滚或恢复方式|"
    r"待确认问题|影响|建议|是/否|原因|动作)[^\]]*\]"
)
TESTING_REQUIRED_SECTIONS = [
    "文档信息",
    "测试目标与范围",
    "需求依据",
    "系统设计依据",
    "开发依据",
    "项目测试上下文与约束",
    "测试策略",
    "测试范围与覆盖矩阵",
    "测试用例",
    "测试数据与环境",
    "自动化与手工执行计划",
    "执行记录",
    "缺陷与风险",
    "回归测试范围",
    "验收结论",
    "部署前测试建议",
    "下游影响分析",
    "变更记录",
]
TESTING_TEMPLATE_FIELDS = {
    "displayName",
    "moduleId",
    "version",
    "quality",
    "createdAt",
    "updatedAt",
    "owner",
}
TESTING_BRACKET_PLACEHOLDER_RE = re.compile(
    r"\[(?:说明|引用|列出|全新项目|已有业务文档|已有代码|已有 UI 代码|"
    r"测试目标|测试范围|不测试范围|需求编号|验收标准|覆盖方式|"
    r"系统设计文档|开发文档|缺失时说明假设|入口|配置|测试框架|CI|命令|环境|约束|"
    r"单元测试|集成测试|端到端测试|手工验证|回归测试|静态检查|安全检查|性能检查|"
    r"功能点|测试类型|用例编号|前置条件|步骤|预期结果|优先级|测试数据|账号|环境变量|"
    r"执行命令|手工步骤|执行状态|结果|证据|执行人|缺陷|风险|影响|建议|"
    r"通过/不通过/未执行|部署准入|上线验证|回滚|是/否|动作)[^\]]*\]"
)
CODE_REVIEW_REQUIRED_SECTIONS = [
    "文档信息",
    "审查目标与范围",
    "审查依据",
    "实现审批状态",
    "代码变更范围",
    "审查方法与证据",
    "审查清单",
    "问题列表",
    "问题处理策略",
    "审查结论",
    "修复回流与再审要求",
    "下游影响分析",
    "变更记录",
]
CODE_REVIEW_TEMPLATE_FIELDS = {
    "displayName",
    "moduleId",
    "version",
    "quality",
    "createdAt",
    "updatedAt",
    "owner",
}
CODE_REVIEW_OUTCOMES = {"pass", "pass_with_risks", "changes_required", "blocked"}
CODE_REVIEW_ISSUE_STATUSES = {"Open", "Fixed", "Verified", "Deferred", "Accepted", "Rejected"}
CODE_REVIEW_BRACKET_PLACEHOLDER_RE = re.compile(
    r"\[(?:说明|引用|列出|全新项目|已有业务文档|已有代码|已有 UI 代码|"
    r"审查目标|审查范围|不审查范围|需求文档路径|系统设计文档路径|开发文档路径|关键结论|"
    r"是/否|证据|implementationApproval 证据|路径|新增/修改/删除/配置/测试|审查重点|风险|"
    r"已执行/未执行/不适用|文件、片段或说明|通过/有风险/不通过/不适用|"
    r"CR-001|Blocker/Critical/Major/Minor/Info|问题描述|影响|建议处理|"
    r"pass/pass_with_risks/changes_required/blocked|条件|原因|动作|负责人|待确认问题|建议)[^\]]*\]"
)
DEPLOYMENT_REQUIRED_SECTIONS = [
    "文档信息",
    "部署目标与范围",
    "上线依据与准入条件",
    "全模块测试准入检查",
    "架构与运行环境依据",
    "环境与配置管理",
    "构建与制品管理",
    "数据库 / 数据迁移计划",
    "部署流程",
    "健康检查与上线验证",
    "监控、日志与告警",
    "回滚与恢复方案",
    "安全、权限与合规",
    "运维交接与值守计划",
    "风险与待确认问题",
    "上线后跟踪与后续动作",
    "变更记录",
]
DEPLOYMENT_TEMPLATE_FIELDS = {
    "displayName",
    "moduleId",
    "version",
    "quality",
    "createdAt",
    "updatedAt",
    "owner",
}
DEPLOYMENT_BRACKET_PLACEHOLDER_RE = re.compile(
    r"\[(?:说明|引用|列出|全新项目|已有业务文档|已有代码|已有 UI 代码|"
    r"部署目标|上线范围|不包含范围|测试状态|测试产出物|风险|建议动作|"
    r"架构文档|运行环境|平台|区域|域名|网络|配置项|环境变量|密钥来源|不要填写密钥值|"
    r"构建命令|制品|镜像|版本号|数据迁移|回填|兼容策略|部署步骤|负责人|审批|"
    r"健康检查|上线验证|监控|日志|告警|回滚|恢复|RTO|RPO|权限|合规|值守|通知|"
    r"待确认问题|影响|建议|是/否|动作|通过/不通过/未确认)[^\]]*\]"
)
QUALITY_CHECK_PHASES = {"requirement", "system_design", "development", "code_review", "testing", "deployment"}


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


def normalize_heading_title(title: str) -> str:
    return re.sub(r"^\d+(?:\.\d+)*(?:[.、])?\s*", "", title.strip())


def markdown_h2_titles(text: str) -> list[str]:
    titles: list[str] = []
    for line in text.splitlines():
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            titles.append(normalize_heading_title(match.group(1)))
    return titles


def detect_requirement_placeholders(text: str) -> list[str]:
    placeholders: list[str] = []
    seen: set[str] = set()
    for line_number, line in enumerate(text.splitlines(), start=1):
        for match in re.finditer(r"\{([A-Za-z][A-Za-z0-9_]*)\}", line):
            if match.group(1) not in REQUIREMENT_TEMPLATE_FIELDS:
                continue
            item = f"第 {line_number} 行：{match.group(0)}"
            if item not in seen:
                placeholders.append(item)
                seen.add(item)
        for match in REQUIREMENT_BRACKET_PLACEHOLDER_RE.finditer(line):
            item = f"第 {line_number} 行：{match.group(0)}"
            if item not in seen:
                placeholders.append(item)
                seen.add(item)
    return placeholders


def validate_requirement_document(file_path: str, confirmed: bool) -> dict[str, list[str]]:
    path = root() / file_path
    errors: list[str] = []
    warnings: list[str] = []
    if not path.exists() or not path.is_file():
        errors.append(f"需求分析文档不存在：{file_path}")
        return {"errors": errors, "warnings": warnings}
    if path.stat().st_size <= 0:
        errors.append(f"需求分析文档为空：{file_path}")
        return {"errors": errors, "warnings": warnings}
    if path.suffix.lower() != ".md":
        errors.append(f"需求分析文档必须是 Markdown 文件：{file_path}")
        return {"errors": errors, "warnings": warnings}

    text = path.read_text(encoding="utf-8")
    titles = set(markdown_h2_titles(text))
    missing_sections = [section for section in REQUIREMENT_REQUIRED_SECTIONS if section not in titles]
    if missing_sections:
        errors.append("需求分析文档缺少必备章节：" + "、".join(missing_sections))

    placeholders = detect_requirement_placeholders(text)
    if placeholders:
        message = "需求分析文档仍包含模板占位符：" + "；".join(placeholders[:10])
        if len(placeholders) > 10:
            message += f"；另有 {len(placeholders) - 10} 处"
        if confirmed:
            errors.append(message)
        else:
            warnings.append(message)
    return {"errors": errors, "warnings": warnings}


def detect_system_design_placeholders(text: str) -> list[str]:
    placeholders: list[str] = []
    seen: set[str] = set()
    for line_number, line in enumerate(text.splitlines(), start=1):
        for match in re.finditer(r"\{([A-Za-z][A-Za-z0-9_]*)\}", line):
            if match.group(1) not in SYSTEM_DESIGN_TEMPLATE_FIELDS:
                continue
            item = f"第 {line_number} 行：{match.group(0)}"
            if item not in seen:
                placeholders.append(item)
                seen.add(item)
        for match in SYSTEM_DESIGN_BRACKET_PLACEHOLDER_RE.finditer(line):
            item = f"第 {line_number} 行：{match.group(0)}"
            if item not in seen:
                placeholders.append(item)
                seen.add(item)
    return placeholders


def validate_system_design_document(file_path: str, confirmed: bool) -> dict[str, list[str]]:
    path = root() / file_path
    errors: list[str] = []
    warnings: list[str] = []
    if not path.exists() or not path.is_file():
        errors.append(f"系统设计文档不存在：{file_path}")
        return {"errors": errors, "warnings": warnings}
    if path.stat().st_size <= 0:
        errors.append(f"系统设计文档为空：{file_path}")
        return {"errors": errors, "warnings": warnings}
    if path.suffix.lower() != ".md":
        errors.append(f"系统设计文档必须是 Markdown 文件：{file_path}")
        return {"errors": errors, "warnings": warnings}

    text = path.read_text(encoding="utf-8")
    titles = set(markdown_h2_titles(text))
    missing_sections = [section for section in SYSTEM_DESIGN_REQUIRED_SECTIONS if section not in titles]
    if missing_sections:
        errors.append("系统设计文档缺少必备章节：" + "、".join(missing_sections))

    placeholders = detect_system_design_placeholders(text)
    if placeholders:
        message = "系统设计文档仍包含模板占位符：" + "；".join(placeholders[:10])
        if len(placeholders) > 10:
            message += f"；另有 {len(placeholders) - 10} 处"
        if confirmed:
            errors.append(message)
        else:
            warnings.append(message)
    return {"errors": errors, "warnings": warnings}


def detect_development_placeholders(text: str) -> list[str]:
    placeholders: list[str] = []
    seen: set[str] = set()
    for line_number, line in enumerate(text.splitlines(), start=1):
        for match in re.finditer(r"\{([A-Za-z][A-Za-z0-9_]*)\}", line):
            if match.group(1) not in DEVELOPMENT_TEMPLATE_FIELDS:
                continue
            item = f"第 {line_number} 行：{match.group(0)}"
            if item not in seen:
                placeholders.append(item)
                seen.add(item)
        for match in DEVELOPMENT_BRACKET_PLACEHOLDER_RE.finditer(line):
            item = f"第 {line_number} 行：{match.group(0)}"
            if item not in seen:
                placeholders.append(item)
                seen.add(item)
    return placeholders


def validate_development_document(file_path: str, confirmed: bool) -> dict[str, list[str]]:
    path = root() / file_path
    errors: list[str] = []
    warnings: list[str] = []
    if not path.exists() or not path.is_file():
        errors.append(f"开发文档不存在：{file_path}")
        return {"errors": errors, "warnings": warnings}
    if path.stat().st_size <= 0:
        errors.append(f"开发文档为空：{file_path}")
        return {"errors": errors, "warnings": warnings}
    if path.suffix.lower() != ".md":
        errors.append(f"开发文档必须是 Markdown 文件：{file_path}")
        return {"errors": errors, "warnings": warnings}

    text = path.read_text(encoding="utf-8")
    titles = set(markdown_h2_titles(text))
    missing_sections = [section for section in DEVELOPMENT_REQUIRED_SECTIONS if section not in titles]
    if missing_sections:
        errors.append("开发文档缺少必备章节：" + "、".join(missing_sections))

    placeholders = detect_development_placeholders(text)
    if placeholders:
        message = "开发文档仍包含模板占位符：" + "；".join(placeholders[:10])
        if len(placeholders) > 10:
            message += f"；另有 {len(placeholders) - 10} 处"
        if confirmed:
            errors.append(message)
        else:
            warnings.append(message)
    return {"errors": errors, "warnings": warnings}


def detect_testing_placeholders(text: str) -> list[str]:
    placeholders: list[str] = []
    seen: set[str] = set()
    for line_number, line in enumerate(text.splitlines(), start=1):
        for match in re.finditer(r"\{([A-Za-z][A-Za-z0-9_]*)\}", line):
            if match.group(1) not in TESTING_TEMPLATE_FIELDS:
                continue
            item = f"第 {line_number} 行：{match.group(0)}"
            if item not in seen:
                placeholders.append(item)
                seen.add(item)
        for match in TESTING_BRACKET_PLACEHOLDER_RE.finditer(line):
            item = f"第 {line_number} 行：{match.group(0)}"
            if item not in seen:
                placeholders.append(item)
                seen.add(item)
    return placeholders


def validate_testing_document(file_path: str, confirmed: bool) -> dict[str, list[str]]:
    path = root() / file_path
    errors: list[str] = []
    warnings: list[str] = []
    if not path.exists() or not path.is_file():
        errors.append(f"测试文档不存在：{file_path}")
        return {"errors": errors, "warnings": warnings}
    if path.stat().st_size <= 0:
        errors.append(f"测试文档为空：{file_path}")
        return {"errors": errors, "warnings": warnings}
    if path.suffix.lower() != ".md":
        errors.append(f"测试文档必须是 Markdown 文件：{file_path}")
        return {"errors": errors, "warnings": warnings}

    text = path.read_text(encoding="utf-8")
    titles = set(markdown_h2_titles(text))
    missing_sections = [section for section in TESTING_REQUIRED_SECTIONS if section not in titles]
    if missing_sections:
        errors.append("测试文档缺少必备章节：" + "、".join(missing_sections))

    placeholders = detect_testing_placeholders(text)
    if placeholders:
        message = "测试文档仍包含模板占位符：" + "；".join(placeholders[:10])
        if len(placeholders) > 10:
            message += f"；另有 {len(placeholders) - 10} 处"
        if confirmed:
            errors.append(message)
        else:
            warnings.append(message)
    return {"errors": errors, "warnings": warnings}


def detect_code_review_placeholders(text: str) -> list[str]:
    placeholders: list[str] = []
    seen: set[str] = set()
    for line_number, line in enumerate(text.splitlines(), start=1):
        for match in re.finditer(r"\{([A-Za-z][A-Za-z0-9_]*)\}", line):
            if match.group(1) not in CODE_REVIEW_TEMPLATE_FIELDS:
                continue
            item = f"第 {line_number} 行：{match.group(0)}"
            if item not in seen:
                placeholders.append(item)
                seen.add(item)
        for match in CODE_REVIEW_BRACKET_PLACEHOLDER_RE.finditer(line):
            item = f"第 {line_number} 行：{match.group(0)}"
            if item not in seen:
                placeholders.append(item)
                seen.add(item)
    return placeholders


def extract_code_review_outcome(text: str) -> str | None:
    for line in text.splitlines():
        if not line.startswith("|") or "审查结果" not in line or "---" in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2 or cells[0] != "审查结果":
            continue
        return cells[1]
    return None


def extract_code_review_issue_statuses(text: str) -> list[tuple[int, str]]:
    statuses: list[tuple[int, str]] = []
    in_issues = False
    status_index: int | None = None
    for line_number, line in enumerate(text.splitlines(), start=1):
        title_match = re.match(r"^##\s+(.+?)\s*$", line)
        if title_match:
            title = normalize_heading_title(title_match.group(1))
            in_issues = title == "问题列表"
            status_index = None
            continue
        if not in_issues or not line.startswith("|"):
            continue
        if "---" in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells:
            continue
        if "状态" in cells:
            status_index = cells.index("状态")
            continue
        if status_index is None or len(cells) <= status_index:
            continue
        status = cells[status_index]
        if status and status not in {"状态", "-"}:
            statuses.append((line_number, status))
    return statuses


def validate_code_review_document(file_path: str, confirmed: bool) -> dict[str, list[str]]:
    path = root() / file_path
    errors: list[str] = []
    warnings: list[str] = []
    if not path.exists() or not path.is_file():
        errors.append(f"代码审查文档不存在：{file_path}")
        return {"errors": errors, "warnings": warnings}
    if path.stat().st_size <= 0:
        errors.append(f"代码审查文档为空：{file_path}")
        return {"errors": errors, "warnings": warnings}
    if path.suffix.lower() != ".md":
        errors.append(f"代码审查文档必须是 Markdown 文件：{file_path}")
        return {"errors": errors, "warnings": warnings}

    text = path.read_text(encoding="utf-8")
    titles = set(markdown_h2_titles(text))
    missing_sections = [section for section in CODE_REVIEW_REQUIRED_SECTIONS if section not in titles]
    if missing_sections:
        errors.append("代码审查文档缺少必备章节：" + "、".join(missing_sections))

    placeholders = detect_code_review_placeholders(text)
    if placeholders:
        message = "代码审查文档仍包含模板占位符：" + "；".join(placeholders[:10])
        if len(placeholders) > 10:
            message += f"；另有 {len(placeholders) - 10} 处"
        if confirmed:
            errors.append(message)
        else:
            warnings.append(message)

    outcome = extract_code_review_outcome(text)
    if confirmed:
        if not outcome:
            errors.append("代码审查文档必须在“审查结论”中通过表格行填写审查结果。")
        elif outcome not in CODE_REVIEW_OUTCOMES:
            errors.append("代码审查文档审查结果不合法：" + outcome + "；允许值：" + "、".join(sorted(CODE_REVIEW_OUTCOMES)))
        invalid_statuses = [
            f"第 {line_number} 行：{status}"
            for line_number, status in extract_code_review_issue_statuses(text)
            if status not in CODE_REVIEW_ISSUE_STATUSES
        ]
        if invalid_statuses:
            errors.append("代码审查文档问题状态不合法：" + "；".join(invalid_statuses[:10]) + "；允许值：" + "、".join(sorted(CODE_REVIEW_ISSUE_STATUSES)))
    return {"errors": errors, "warnings": warnings}


def detect_deployment_placeholders(text: str) -> list[str]:
    placeholders: list[str] = []
    seen: set[str] = set()
    for line_number, line in enumerate(text.splitlines(), start=1):
        for match in re.finditer(r"\{([A-Za-z][A-Za-z0-9_]*)\}", line):
            if match.group(1) not in DEPLOYMENT_TEMPLATE_FIELDS:
                continue
            item = f"第 {line_number} 行：{match.group(0)}"
            if item not in seen:
                placeholders.append(item)
                seen.add(item)
        for match in DEPLOYMENT_BRACKET_PLACEHOLDER_RE.finditer(line):
            item = f"第 {line_number} 行：{match.group(0)}"
            if item not in seen:
                placeholders.append(item)
                seen.add(item)
    return placeholders


def validate_deployment_document(file_path: str, confirmed: bool) -> dict[str, list[str]]:
    path = root() / file_path
    errors: list[str] = []
    warnings: list[str] = []
    if not path.exists() or not path.is_file():
        errors.append(f"部署文档不存在：{file_path}")
        return {"errors": errors, "warnings": warnings}
    if path.stat().st_size <= 0:
        errors.append(f"部署文档为空：{file_path}")
        return {"errors": errors, "warnings": warnings}
    if path.suffix.lower() != ".md":
        errors.append(f"部署文档必须是 Markdown 文件：{file_path}")
        return {"errors": errors, "warnings": warnings}

    text = path.read_text(encoding="utf-8")
    titles = set(markdown_h2_titles(text))
    missing_sections = [section for section in DEPLOYMENT_REQUIRED_SECTIONS if section not in titles]
    if missing_sections:
        errors.append("部署文档缺少必备章节：" + "、".join(missing_sections))

    placeholders = detect_deployment_placeholders(text)
    if placeholders:
        message = "部署文档仍包含模板占位符：" + "；".join(placeholders[:10])
        if len(placeholders) > 10:
            message += f"；另有 {len(placeholders) - 10} 处"
        if confirmed:
            errors.append(message)
        else:
            warnings.append(message)
    return {"errors": errors, "warnings": warnings}


def validate_artifact_quality_document(phase: str, file_path: str, confirmed: bool) -> dict[str, list[str]]:
    if phase == "requirement":
        return validate_requirement_document(file_path, confirmed)
    if phase == "system_design":
        return validate_system_design_document(file_path, confirmed)
    if phase == "development":
        return validate_development_document(file_path, confirmed)
    if phase == "code_review":
        return validate_code_review_document(file_path, confirmed)
    if phase == "testing":
        return validate_testing_document(file_path, confirmed)
    if phase == "deployment":
        return validate_deployment_document(file_path, confirmed)
    return {"errors": [], "warnings": []}


def artifact_quality_error_prefix(phase: str) -> str:
    return f"{PHASE_NAMES[phase]}文档质量检查未通过："


def enforce_hard_dependencies(state: dict[str, Any], phase: str) -> None:
    result = check_phase_dependencies(state, phase)
    if not result["hardMissing"]:
        return
    details = "；".join(f"{item['phaseName']}({item['phase']}): {item['reason']}" for item in result["hardMissing"])
    raise SfkError(f"{PHASE_NAMES[phase]} 硬依赖未满足，不能更新阶段产出物：{details}")


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


def validate_phase(phase_id: str) -> None:
    if phase_id not in PHASE_NAMES:
        raise SfkError(f"未知阶段：{phase_id}")


def artifact_files_health(files: list[str]) -> dict[str, Any]:
    normalized = [str(item).replace("\\", "/") for item in files if str(item).strip()]
    missing: list[str] = []
    empty: list[str] = []
    usable: list[str] = []
    for file_path in normalized:
        path = root() / file_path
        if not path.exists() or not path.is_file():
            missing.append(file_path)
            continue
        if path.stat().st_size <= 0:
            empty.append(file_path)
            continue
        usable.append(file_path)
    return {
        "hasFiles": bool(normalized),
        "hasUsableFile": bool(usable),
        "files": normalized,
        "usable": usable,
        "missing": missing,
        "empty": empty,
    }


def dependency_status(state: dict[str, Any], phase_id: str) -> dict[str, Any]:
    validate_phase(phase_id)
    artifact = state.get("artifacts", {}).get(phase_id, {})
    status = artifact.get("status", "pending")
    quality = artifact.get("quality")
    files = artifact.get("files") or []
    health = artifact_files_health(files)
    reason = "satisfied"
    satisfied = True
    if not files:
        reason = "missing"
        satisfied = False
    elif status == "in_progress" or quality == "draft":
        reason = "draft"
        satisfied = False
    elif status != "done":
        reason = "missing"
        satisfied = False
    elif quality != "confirmed":
        reason = "not_confirmed"
        satisfied = False
    elif not health["hasUsableFile"]:
        reason = "file_missing" if health["missing"] else "file_empty"
        satisfied = False
    return {
        "phase": phase_id,
        "phaseName": PHASE_NAMES[phase_id],
        "status": status,
        "quality": quality,
        "reason": reason,
        "satisfied": satisfied,
        "files": health["files"],
        "missingFiles": health["missing"],
        "emptyFiles": health["empty"],
    }


def artifact_is_satisfied(artifact: dict[str, Any]) -> bool:
    return (
        artifact.get("status") == "done"
        and artifact.get("quality") == "confirmed"
        and artifact_files_health(artifact.get("files") or [])["hasUsableFile"]
    )


def check_phase_dependencies(state: dict[str, Any], target_phase: str) -> dict[str, Any]:
    validate_phase(target_phase)
    dependencies = PHASE_DEPENDENCIES.get(target_phase, {"hard": [], "soft": []})
    hard_missing = [
        item for item in (dependency_status(state, phase) for phase in dependencies.get("hard", []))
        if not item["satisfied"]
    ]
    soft_missing = [
        item for item in (dependency_status(state, phase) for phase in dependencies.get("soft", []))
        if not item["satisfied"]
    ]
    warnings: list[str] = []
    for item in hard_missing:
        warnings.append(f"{PHASE_NAMES[target_phase]} 需要先确认 {item['phaseName']} 产出物；当前状态：{item['reason']}。")
    for item in soft_missing:
        warnings.append(f"{PHASE_NAMES[target_phase]} 建议先确认 {item['phaseName']} 产出物；当前可继续，但需要记录假设。")
    return {
        "phase": target_phase,
        "phaseName": PHASE_NAMES[target_phase],
        "blocked": bool(hard_missing),
        "canContinue": not hard_missing,
        "hard": dependencies.get("hard", []),
        "soft": dependencies.get("soft", []),
        "hardMissing": hard_missing,
        "softMissing": soft_missing,
        "warnings": warnings,
    }


def should_skip_discovery_dir(dir_path: Path) -> bool:
    parts = set(dir_path.relative_to(root()).parts) if dir_path != root() else set()
    if parts & SKIP_DISCOVERY_DIRS:
        return True
    rel_parts = dir_path.relative_to(root()).parts if dir_path != root() else ()
    return len(rel_parts) >= 2 and rel_parts[0] == ".claude" and rel_parts[1] == "worktrees"


def iter_project_files(max_files: int = 5000) -> tuple[list[Path], bool]:
    files: list[Path] = []
    truncated = False
    for current_dir, dir_names, file_names in os.walk(root()):
        current_path = Path(current_dir)
        dir_names[:] = [name for name in dir_names if not should_skip_discovery_dir(current_path / name)]
        for file_name in file_names:
            path = current_path / file_name
            files.append(path)
            if len(files) >= max_files:
                return files, True
    return files, truncated


def is_business_doc(file_path: str) -> bool:
    lower = file_path.lower()
    name = Path(file_path).name.lower()
    if lower.startswith("docs/super-flow-kit/"):
        return False
    if name == "readme.md":
        return True
    if lower.startswith("docs/") and lower.endswith(".md"):
        return True
    return bool(re.match(r"^(product|requirements?|spec|prd).*\.md$", name))


def is_manifest(file_path: str) -> bool:
    name = Path(file_path).name
    lower = name.lower()
    return name in MANIFEST_NAMES or lower.startswith(("vite.config", "next.config", "nuxt.config", "svelte.config"))


def ui_framework_hints(file_path: str) -> list[str]:
    lower = file_path.lower()
    hints: list[str] = []
    patterns = {
        "Tailwind CSS": ["tailwind.config", "@tailwind"],
        "Next.js": ["next.config", "app/", "pages/"],
        "Vue": [".vue"],
        "Svelte": [".svelte", "svelte.config"],
        "CSS Modules": [".module.css", ".module.scss"],
        "SCSS": [".scss"],
    }
    for hint, values in patterns.items():
        if any(value in lower for value in values):
            hints.append(hint)
    return hints


def discover_project_context(phase: str) -> dict[str, Any]:
    validate_phase(phase)
    index, state, module_id = require_current_state()
    files, truncated = iter_project_files()
    manifests: list[str] = []
    business_docs: list[str] = []
    source_dirs: set[str] = set()
    code_files: list[str] = []
    sfk_artifacts: list[str] = []
    route_dirs: set[str] = set()
    component_dirs: set[str] = set()
    style_files: list[str] = []
    design_system_files: list[str] = []
    representative_files: list[str] = []
    framework_hints: set[str] = set()
    entrypoint_files: list[str] = []
    config_files: list[str] = []
    api_files: list[str] = []
    service_files: list[str] = []
    data_files: list[str] = []
    test_files: list[str] = []
    deploy_files: list[str] = []

    for path in files:
        file_path = rel(path)
        lower = file_path.lower()
        parts = file_path.split("/")
        lower_parts = [part.lower() for part in parts]
        name = path.name
        lower_name = name.lower()
        suffix = path.suffix.lower()
        stem = path.stem.lower()

        if lower.startswith("docs/super-flow-kit/"):
            sfk_artifacts.append(file_path)
            continue
        if is_manifest(file_path):
            manifests.append(file_path)
        if is_business_doc(file_path):
            business_docs.append(file_path)
        if parts and parts[0] in {"src", "app", "pages", "components", "tests", "test"}:
            source_dirs.add(parts[0])
        if suffix in CODE_EXTENSIONS:
            code_files.append(file_path)
        if any(part in {"app", "pages", "views", "routes"} for part in parts):
            route_dirs.add("/".join(parts[:2]) if len(parts) > 1 else parts[0])
        if any(part in {"components", "ui"} for part in parts):
            component_dirs.add("/".join(parts[:2]) if len(parts) > 1 else parts[0])
        if suffix in {".css", ".scss", ".less"}:
            style_files.append(file_path)
        if "tailwind.config" in lower or "theme" in lower or "tokens" in lower or "design-system" in lower or "globals.css" in lower:
            design_system_files.append(file_path)
        if suffix in UI_EXTENSIONS and (set(parts) & UI_DIR_PARTS):
            representative_files.append(file_path)
        for hint in ui_framework_hints(file_path):
            framework_hints.add(hint)

        if stem in {"main", "app", "server", "index"} and suffix in CODE_EXTENSIONS:
            entrypoint_files.append(file_path)
        if is_manifest(file_path) or ".config." in lower_name or lower_name.endswith("config.js") or lower_name.endswith("config.ts"):
            config_files.append(file_path)
        if any(part in {"api", "route", "routes", "router", "controller", "controllers", "endpoint", "endpoints"} for part in lower_parts):
            api_files.append(file_path)
        if any(part in {"service", "services", "domain", "usecase", "usecases", "application"} for part in lower_parts):
            service_files.append(file_path)
        if any(part in {"model", "models", "entity", "entities", "repository", "repositories", "schema", "schemas", "migration", "migrations", "prisma", "db", "database"} for part in lower_parts):
            data_files.append(file_path)
        if any(part in {"tests", "test"} for part in lower_parts) or ".test." in lower_name or ".spec." in lower_name:
            test_files.append(file_path)
        if (
            lower_name == "dockerfile"
            or lower_name.startswith("docker-compose")
            or lower.startswith(".github/workflows/")
            or any(part in {"k8s", "helm", "vercel", "netlify"} for part in lower_parts)
        ):
            deploy_files.append(file_path)

    has_ui_code = bool(route_dirs or component_dirs or style_files or design_system_files or representative_files)
    if has_ui_code:
        project_kind = "existing_ui_code"
    elif manifests or code_files:
        project_kind = "existing_code"
    elif business_docs:
        project_kind = "existing_business_docs"
    else:
        project_kind = "new_project"

    warnings: list[str] = []
    if truncated:
        warnings.append("scan_truncated")

    def limited(items: list[str] | set[str], limit: int = 50) -> list[str]:
        return sorted(items)[:limit]

    return {
        "moduleId": module_id,
        "phase": phase,
        "phaseName": PHASE_NAMES[phase],
        "projectKind": project_kind,
        "evidence": {
            "manifests": limited(manifests),
            "businessDocs": limited(business_docs),
            "sourceDirs": limited(source_dirs),
            "codeFiles": limited(code_files),
            "ui": {
                "hasUiCode": has_ui_code,
                "frameworkHints": sorted(framework_hints),
                "routeDirs": limited(route_dirs),
                "componentDirs": limited(component_dirs),
                "styleFiles": limited(style_files),
                "designSystemFiles": limited(design_system_files),
                "representativeFiles": limited(representative_files),
            },
            "architecture": {
                "entrypointFiles": limited(entrypoint_files),
                "configFiles": limited(config_files),
                "apiFiles": limited(api_files),
                "serviceFiles": limited(service_files),
                "dataFiles": limited(data_files),
                "testFiles": limited(test_files),
                "deployFiles": limited(deploy_files),
            },
            "sfkArtifacts": limited(sfk_artifacts),
        },
        "warnings": warnings,
    }


def artifact_summary(artifact: dict[str, Any]) -> dict[str, Any]:
    files = artifact.get("files") or []
    health = artifact_files_health(files)
    return {
        "status": artifact.get("status", "pending"),
        "quality": artifact.get("quality"),
        "currentFile": files[-1] if files else None,
        "files": health["files"],
        "missingFiles": health["missing"],
        "emptyFiles": health["empty"],
        "hasUsableFile": health["hasUsableFile"],
    }


def deployment_readiness_report(index: dict[str, Any]) -> dict[str, Any]:
    modules = index.get("modules", {})
    items: list[dict[str, Any]] = []
    ready_count = 0
    for module_id, module_info in modules.items():
        item = {
            "moduleId": module_id,
            "displayName": module_info.get("displayName") or module_id,
            "statePath": module_info.get("statePath") or rel(state_path(module_id)),
            "satisfied": False,
            "reason": "state_missing",
            "testingStatus": None,
            "quality": None,
            "currentFile": None,
            "files": [],
            "missingFiles": [],
            "emptyFiles": [],
        }
        try:
            state = read_json(state_path(module_id))
            status = dependency_status(state, "testing")
            item.update({
                "satisfied": status["satisfied"],
                "reason": status["reason"],
                "testingStatus": status["status"],
                "quality": status["quality"],
                "files": status["files"],
                "currentFile": status["files"][-1] if status["files"] else None,
                "missingFiles": status["missingFiles"],
                "emptyFiles": status["emptyFiles"],
            })
            if status["satisfied"]:
                ready_count += 1
        except SfkError as exc:
            item["reason"] = str(exc)
        items.append(item)
    not_ready = [item for item in items if not item["satisfied"]]
    return {
        "totalModules": len(items),
        "readyModules": ready_count,
        "notReadyModules": len(not_ready),
        "allModulesTestingConfirmed": bool(items) and not not_ready,
        "modules": items,
        "notReady": not_ready,
        "message": "所有模块均检测到已确认且可用的测试产出物。" if items and not not_ready else "存在模块未检测到已确认且可用的测试产出物，部署前需要提示用户确认风险。",
    }


def implementation_approval_status(state: dict[str, Any]) -> dict[str, Any]:
    development = state.get("artifacts", {}).get("development", {})
    approval = ensure_implementation_approval(development)
    summary = artifact_summary(development)
    confirmed_at = development.get("confirmedAt")
    current_file = summary["currentFile"]

    reason = "implementation_approval_pending"
    can_implement = False
    if not current_file:
        reason = "development_document_missing"
    elif development.get("status") != "done" or development.get("quality") != "confirmed":
        reason = "development_document_draft"
    elif summary["missingFiles"]:
        reason = "development_document_file_missing"
    elif summary["emptyFiles"]:
        reason = "development_document_file_empty"
    elif approval.get("status") != "approved":
        reason = "implementation_approval_pending"
    elif approval.get("approvedForFile") != current_file or approval.get("approvedForConfirmedAt") != confirmed_at:
        reason = "implementation_approval_stale"
    else:
        reason = "approved"
        can_implement = True

    return {
        "developmentArtifact": {
            "status": development.get("status", "pending"),
            "quality": development.get("quality"),
            "currentFile": current_file,
            "confirmedAt": confirmed_at,
            "hasUsableFile": summary["hasUsableFile"],
            "missingFiles": summary["missingFiles"],
            "emptyFiles": summary["emptyFiles"],
        },
        "implementationApproval": approval,
        "canImplement": can_implement,
        "reason": reason,
    }


def code_review_readiness_report(state: dict[str, Any]) -> dict[str, Any]:
    dependency_result = check_phase_dependencies(state, "code_review")
    approval_status = implementation_approval_status(state)
    blockers = [
        f"{item['phaseName']}({item['phase']}): {item['reason']}"
        for item in dependency_result["hardMissing"]
    ]
    if not approval_status["canImplement"]:
        blockers.append(f"源码实现二次确认未满足：{approval_status['reason']}")
    can_review = not blockers
    return {
        "phase": "code_review",
        "phaseName": PHASE_NAMES["code_review"],
        "canReview": can_review,
        "blocked": not can_review,
        "dependencies": dependency_result,
        "implementation": approval_status,
        "blockers": blockers,
        "message": "代码审查准入检查通过。" if can_review else "代码审查准入检查未通过，请先补齐硬依赖并完成源码实现二次确认。",
    }


def enforce_code_review_readiness(state: dict[str, Any]) -> None:
    result = code_review_readiness_report(state)
    if result["canReview"]:
        return
    details = "；".join(result["blockers"])
    raise SfkError(
        "代码审查准入未满足，不能更新代码审查产出物："
        + details
        + "。请先执行：python scripts/sfk.py implementation current development；"
        + "必要时执行：python scripts/sfk.py implementation approve development --summary \"<本次实现范围摘要>\"。"
    )


def exports_dir() -> Path:
    return root() / "docs" / "super-flow-kit" / "exports"


def export_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")


def safe_export_slug(value: str) -> str:
    candidate = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-._").lower()
    return candidate or "project"


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    if path.suffix:
        stem = path.with_suffix("")
        suffix = path.suffix
        for index in range(2, 1000):
            candidate = stem.parent / f"{stem.name}-{index}{suffix}"
            if not candidate.exists():
                return candidate
    else:
        for index in range(2, 1000):
            candidate = path.parent / f"{path.name}-{index}"
            if not candidate.exists():
                return candidate
    raise SfkError(f"无法生成不冲突的导出路径：{rel(path)}")


def package_rel(path: Path, base: Path) -> str:
    return path.relative_to(base).as_posix()


def module_state_for_export(index: dict[str, Any], module_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    validate_module_id(module_id)
    modules = index.get("modules", {})
    if module_id not in modules:
        raise SfkError(f"模块不存在，无法导出：{module_id}")
    return modules[module_id], read_json(state_path(module_id))


def is_exportable_artifact_path(module_id: str, file_path: str) -> tuple[bool, str | None]:
    if not file_path:
        return False, "empty_path"
    raw = str(file_path).replace("\\", "/")
    if Path(raw).is_absolute():
        return False, "absolute_path"
    if ".." in Path(raw).parts:
        return False, "parent_reference"
    if not raw.startswith(f"docs/super-flow-kit/{module_id}/"):
        return False, "outside_module_docs"
    if raw.startswith("docs/super-flow-kit/exports/"):
        return False, "inside_exports"
    if Path(raw).suffix.lower() != ".md":
        return False, "not_markdown"
    lower_name = Path(raw).name.lower()
    if any(marker in lower_name for marker in (".env", "secret", "credential", "private-key", "id_rsa")):
        return False, "sensitive_filename"
    resolved = (root() / raw).resolve(strict=False)
    try:
        resolved.relative_to(root().resolve())
    except ValueError:
        return False, "outside_project_root"
    return True, None


def detect_secret_markers(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    markers: list[str] = []
    if re.search(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", text):
        markers.append("private_key_block")
    if re.search(r"\bAKIA[0-9A-Z]{16}\b", text):
        markers.append("aws_access_key_id")
    secret_re = re.compile(r"(?im)^\s*(?:api[_-]?key|password|token|secret)\s*[:=]\s*['\"]?([^'\"\s#]+)")
    for match in secret_re.finditer(text):
        value = match.group(1).strip()
        if value and not re.fullmatch(r"(?:xxx+|\*+|<[^>]+>|\[[^\]]+\]|待确认|placeholder|example|demo)", value, flags=re.I):
            markers.append("inline_secret")
            break
    return markers


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def phase_export_filename(phase_id: str, source_path: str) -> str:
    suffix = Path(source_path).suffix or ".md"
    name = PHASE_NAMES[phase_id].replace(" ", "").replace("/", "")
    return f"{name}{suffix}"


def add_export_risk(model: dict[str, Any], phase: str | None, severity: str, message: str, action: str) -> None:
    risk = {"phase": phase, "severity": severity, "message": message, "action": action}
    model.setdefault("risks", []).append(risk)
    model.setdefault("checklist", []).append({"done": False, "item": action, "source": phase or "module"})


def module_export_model(index: dict[str, Any], module_id: str) -> dict[str, Any]:
    module_info, state = module_state_for_export(index, module_id)
    module = state.get("module", {})
    model: dict[str, Any] = {
        "moduleId": module_id,
        "displayName": module.get("displayName") or module_info.get("displayName") or module_id,
        "currentPhase": state.get("currentPhase", "requirement"),
        "statePath": rel(state_path(module_id)),
        "artifacts": [],
        "risks": [],
        "checklist": [],
        "implementation": implementation_approval_status(state),
    }
    artifacts = state.get("artifacts", {})
    for phase_id, phase_name in PHASES:
        artifact = artifacts.get(phase_id, {})
        summary = artifact_summary(artifact)
        current_file = summary["currentFile"]
        entry: dict[str, Any] = {
            "phase": phase_id,
            "phaseName": phase_name,
            "status": summary["status"],
            "quality": summary["quality"],
            "sourcePath": current_file,
            "packagePath": None,
            "copied": False,
            "sha256": None,
            "bytes": None,
            "riskReason": None,
        }
        if not current_file:
            entry["riskReason"] = "missing_artifact"
            add_export_risk(model, phase_id, "medium", f"{phase_name} 缺少当前产出物。", f"补齐或确认 {PHASE_COMMANDS[phase_id]} 产出物")
        elif summary["missingFiles"]:
            entry["riskReason"] = "file_missing"
            add_export_risk(model, phase_id, "high", f"{phase_name} 当前产出物文件缺失：{current_file}", "修复产出物文件引用或重新生成文档")
        elif summary["emptyFiles"]:
            entry["riskReason"] = "file_empty"
            add_export_risk(model, phase_id, "high", f"{phase_name} 当前产出物文件为空：{current_file}", "补充产出物内容后重新导出")
        elif summary["status"] != "done" or summary["quality"] != "confirmed":
            entry["riskReason"] = "not_confirmed"
            add_export_risk(model, phase_id, "medium", f"{phase_name} 尚未 confirmed：{summary['status']} / {summary['quality']}", f"继续使用 {PHASE_COMMANDS[phase_id]} 完成确认")
        ok, reason = is_exportable_artifact_path(module_id, current_file or "")
        if current_file and not ok:
            entry["riskReason"] = reason
            add_export_risk(model, phase_id, "high", f"{phase_name} 产出物不在允许导出目录，已跳过：{current_file}", "将产出物保存到模块 docs/super-flow-kit 目录后重新导出")
        model["artifacts"].append(entry)
    implementation = model["implementation"]
    if not implementation.get("canImplement"):
        add_export_risk(model, "development", "medium", f"源码实现授权未满足：{implementation.get('reason')}", "如需证明实现已获准，请回到 /sfk-dev 完成源码实现二次确认")
    return model


def project_export_model(index: dict[str, Any]) -> dict[str, Any]:
    modules = index.get("modules", {})
    if not modules:
        raise SfkError("当前项目没有可导出的模块。")
    module_models: list[dict[str, Any]] = []
    project_risks: list[dict[str, Any]] = []
    for module_id in modules:
        try:
            module_models.append(module_export_model(index, module_id))
        except SfkError as exc:
            project_risks.append({"moduleId": module_id, "phase": None, "severity": "high", "message": str(exc), "action": "修复模块状态文件后重新导出"})
    deployment_readiness = deployment_readiness_report(index)
    if not deployment_readiness.get("allModulesTestingConfirmed"):
        project_risks.append({"moduleId": None, "phase": "deployment", "severity": "medium", "message": deployment_readiness.get("message"), "action": "补齐各模块测试产出物后再进行正式部署交付"})
    return {"modules": module_models, "risks": project_risks, "deploymentReadiness": deployment_readiness}


def copy_module_artifacts(module_model: dict[str, Any], artifacts_dir: Path, package_prefix: str = "artifacts") -> None:
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    for entry in module_model.get("artifacts", []):
        source_path = entry.get("sourcePath")
        if not source_path or entry.get("riskReason") in {"file_missing", "file_empty"}:
            continue
        ok, reason = is_exportable_artifact_path(module_model["moduleId"], source_path)
        if not ok:
            entry["riskReason"] = reason
            continue
        source = root() / source_path
        markers = detect_secret_markers(source)
        if markers:
            raise SfkError(f"检测到疑似敏感信息，已阻止导出：{source_path} ({', '.join(markers)})。请先脱敏后再导出。")
        destination = unique_path(artifacts_dir / phase_export_filename(entry["phase"], source_path))
        shutil.copy2(source, destination)
        entry["copied"] = True
        entry["bytes"] = destination.stat().st_size
        entry["sha256"] = sha256_file(destination)
        entry["packagePath"] = f"{package_prefix}/{destination.name}"


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(cell) if cell is not None else "" for cell in row) + " |")
    return "\n".join(lines)


def render_module_export_readme(model: dict[str, Any]) -> str:
    rows = [[item["phaseName"], item["status"], item["quality"], item.get("sourcePath") or "", "是" if item.get("copied") else "否", item.get("riskReason") or ""] for item in model["artifacts"]]
    return (
        f"# 模块交付包：{model['displayName']}\n\n"
        f"- 模块 ID：{model['moduleId']}\n"
        f"- 当前阶段：{model['currentPhase']}\n"
        f"- 风险数量：{len(model.get('risks', []))}\n\n"
        "## 阶段状态总览\n\n"
        + markdown_table(["阶段", "状态", "质量", "源文件", "已复制", "风险"], rows)
        + "\n\n## 文件\n\n- `manifest.json`：机器可读导出清单。\n- `summary.md`：交付摘要。\n- `indices/artifacts.md`：产出物索引。\n- `risks/risk-register.md`：风险与待办。\n"
    )


def render_project_export_readme(model: dict[str, Any]) -> str:
    rows = [[item["moduleId"], item["displayName"], item["currentPhase"], len(item.get("risks", [])), f"modules/{item['moduleId']}/README.md"] for item in model["modules"]]
    return "# 项目交付包\n\n" + markdown_table(["模块 ID", "模块", "当前阶段", "风险数", "模块包"], rows) + "\n"


def render_export_summary(model: dict[str, Any], package_type: str) -> str:
    modules = model["modules"] if package_type == "project" else [model]
    completed = sum(1 for item in modules if not item.get("risks"))
    return (
        f"# 交付摘要\n\n"
        f"- 导出类型：{package_type}\n"
        f"- 模块数量：{len(modules)}\n"
        f"- 无风险模块数：{completed}\n"
        f"- 风险总数：{sum(len(item.get('risks', [])) for item in modules) + len(model.get('risks', [])) if package_type == 'project' else len(model.get('risks', []))}\n"
    )


def render_export_artifacts_index(modules: list[dict[str, Any]]) -> str:
    lines = ["# 产出物索引\n"]
    for module in modules:
        lines.append(f"## {module['displayName']}（{module['moduleId']}）\n")
        rows = [[item["phaseName"], item.get("sourcePath") or "", item.get("packagePath") or "", "是" if item.get("copied") else "否", item.get("riskReason") or ""] for item in module["artifacts"]]
        lines.append(markdown_table(["阶段", "源文件", "包内路径", "已复制", "风险"], rows))
        lines.append("")
    return "\n".join(lines)


def render_export_modules_index(modules: list[dict[str, Any]]) -> str:
    rows = [[item["moduleId"], item["displayName"], item["currentPhase"], len(item.get("risks", [])), f"modules/{item['moduleId']}/"] for item in modules]
    return "# 模块索引\n\n" + markdown_table(["模块 ID", "模块", "当前阶段", "风险数", "包内目录"], rows) + "\n"


def render_export_risk_register(modules: list[dict[str, Any]], project_risks: list[dict[str, Any]] | None = None) -> str:
    rows: list[list[Any]] = []
    for module in modules:
        for risk in module.get("risks", []):
            rows.append([module["moduleId"], risk.get("phase") or "", risk.get("severity"), risk.get("message"), risk.get("action")])
    for risk in project_risks or []:
        rows.append([risk.get("moduleId") or "项目", risk.get("phase") or "", risk.get("severity"), risk.get("message"), risk.get("action")])
    if not rows:
        rows.append(["-", "-", "-", "暂无导出风险", "-"])
    return "# 风险与待办汇总\n\n" + markdown_table(["模块", "阶段", "严重级别", "风险/待办", "建议动作"], rows) + "\n"


def render_export_checklist(modules: list[dict[str, Any]], project_risks: list[dict[str, Any]] | None = None) -> str:
    lines = ["# 交付检查清单\n"]
    for module in modules:
        if not module.get("checklist"):
            lines.append(f"- [x] {module['displayName']}：暂无导出发现的待办")
        for item in module.get("checklist", []):
            lines.append(f"- [ ] {module['displayName']}：{item.get('item')}")
    for risk in project_risks or []:
        lines.append(f"- [ ] 项目：{risk.get('action')}")
    return "\n".join(lines) + "\n"


def zip_export_dir(export_dir: Path) -> Path:
    zip_path = unique_path(export_dir.with_suffix(".zip"))
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for current_dir, _, file_names in os.walk(export_dir):
            for file_name in file_names:
                path = Path(current_dir) / file_name
                archive.write(path, path.relative_to(export_dir.parent).as_posix())
    return zip_path


def base_manifest(index: dict[str, Any], package_type: str, output_dir: Path, generated_at: str) -> dict[str, Any]:
    return {
        "schemaVersion": SCHEMA_VERSION,
        "exportVersion": "0.8",
        "packageType": package_type,
        "generatedAt": generated_at,
        "project": {"name": index.get("project", {}).get("name", root().name), "root": "."},
        "package": {"path": rel(output_dir), "zipPath": None},
        "modules": [],
    }


def write_json_file(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_module_export_package(index: dict[str, Any], module_id: str, with_zip: bool) -> dict[str, Any]:
    generated_at = now_iso()
    model = module_export_model(index, module_id)
    output_dir = unique_path(exports_dir() / f"{export_timestamp()}-module-{module_id}")
    output_dir.mkdir(parents=True, exist_ok=False)
    copy_module_artifacts(model, output_dir / "artifacts", "artifacts")
    (output_dir / "risks").mkdir(parents=True, exist_ok=True)
    (output_dir / "indices").mkdir(parents=True, exist_ok=True)
    (output_dir / "README.md").write_text(render_module_export_readme(model), encoding="utf-8")
    (output_dir / "summary.md").write_text(render_export_summary(model, "module"), encoding="utf-8")
    (output_dir / "indices" / "artifacts.md").write_text(render_export_artifacts_index([model]), encoding="utf-8")
    (output_dir / "risks" / "risk-register.md").write_text(render_export_risk_register([model]), encoding="utf-8")
    (output_dir / "checklist.md").write_text(render_export_checklist([model]), encoding="utf-8")
    manifest = base_manifest(index, "module", output_dir, generated_at)
    manifest["modules"] = [model]
    write_json_file(output_dir / "manifest.json", manifest)
    zip_path = zip_export_dir(output_dir) if with_zip else None
    if zip_path:
        manifest["package"]["zipPath"] = rel(zip_path)
        write_json_file(output_dir / "manifest.json", manifest)
    return {"outputDir": rel(output_dir), "zipPath": rel(zip_path) if zip_path else None, "manifest": rel(output_dir / "manifest.json"), "riskCount": len(model.get("risks", []))}


def write_project_export_package(index: dict[str, Any], with_zip: bool) -> dict[str, Any]:
    generated_at = now_iso()
    model = project_export_model(index)
    project_slug = safe_export_slug(index.get("project", {}).get("name") or root().name)
    output_dir = unique_path(exports_dir() / f"{export_timestamp()}-project-{project_slug}")
    output_dir.mkdir(parents=True, exist_ok=False)
    for module in model["modules"]:
        module_dir = output_dir / "modules" / module["moduleId"]
        module_dir.mkdir(parents=True, exist_ok=True)
        copy_module_artifacts(module, module_dir / "artifacts", f"modules/{module['moduleId']}/artifacts")
        (module_dir / "README.md").write_text(render_module_export_readme(module), encoding="utf-8")
    (output_dir / "risks").mkdir(parents=True, exist_ok=True)
    (output_dir / "indices").mkdir(parents=True, exist_ok=True)
    (output_dir / "README.md").write_text(render_project_export_readme(model), encoding="utf-8")
    (output_dir / "summary.md").write_text(render_export_summary(model, "project"), encoding="utf-8")
    (output_dir / "indices" / "modules.md").write_text(render_export_modules_index(model["modules"]), encoding="utf-8")
    (output_dir / "indices" / "artifacts.md").write_text(render_export_artifacts_index(model["modules"]), encoding="utf-8")
    (output_dir / "risks" / "risk-register.md").write_text(render_export_risk_register(model["modules"], model.get("risks", [])), encoding="utf-8")
    (output_dir / "checklist.md").write_text(render_export_checklist(model["modules"], model.get("risks", [])), encoding="utf-8")
    manifest = base_manifest(index, "project", output_dir, generated_at)
    manifest["modules"] = model["modules"]
    manifest["projectRisks"] = model.get("risks", [])
    manifest["deploymentReadiness"] = model.get("deploymentReadiness")
    write_json_file(output_dir / "manifest.json", manifest)
    zip_path = zip_export_dir(output_dir) if with_zip else None
    if zip_path:
        manifest["package"]["zipPath"] = rel(zip_path)
        write_json_file(output_dir / "manifest.json", manifest)
    return {"outputDir": rel(output_dir), "zipPath": rel(zip_path) if zip_path else None, "manifest": rel(output_dir / "manifest.json"), "riskCount": sum(len(module.get("risks", [])) for module in model["modules"]) + len(model.get("risks", []))}

def downstream_phases(phase: str) -> list[str]:
    validate_phase(phase)
    phase_ids = [phase_id for phase_id, _ in PHASES]
    index = phase_ids.index(phase)
    if phase == "ui_design":
        candidates = ["development", "code_review", "testing"]
        return [item for item in phase_ids[index + 1:] if item in candidates]
    return phase_ids[index + 1:]


def artifact_impact_report(state: dict[str, Any], phase: str) -> dict[str, Any]:
    validate_phase(phase)
    artifacts = state.get("artifacts", {})
    downstream: list[dict[str, Any]] = []
    for item in downstream_phases(phase):
        artifact = artifacts.get(item, {})
        summary = artifact_summary(artifact)
        has_state = summary["status"] != "pending" or bool(summary["files"])
        needs_review = has_state
        reason = "暂无已生成产出物。"
        if needs_review:
            if phase == "requirement":
                reason = "需求变更可能影响后续阶段的范围、页面、设计、实现、测试或部署。"
            elif phase == "ui_design":
                reason = "UI 设计变更可能影响前端实现、测试用例、交互验收和可访问性检查。"
            elif phase == "system_design":
                reason = "系统设计变更可能影响开发实现、API / 接口设计、数据库设计、测试覆盖、部署配置、监控和回滚策略。"
            elif phase == "development":
                reason = "开发文档变更可能影响代码审查结论、问题修复回流、测试覆盖、部署配置、数据迁移、监控和回滚策略。"
            elif phase == "code_review":
                reason = "代码审查结论或问题状态变更可能影响测试覆盖、缺陷验证、部署风险判断和上线准入说明。"
            elif phase == "testing":
                reason = "测试文档变更可能影响部署准入、发布风险判断、回归范围、上线验证和回滚策略。"
            else:
                reason = f"{PHASE_NAMES[phase]} 变更可能影响该阶段产出物。"
            if summary["missingFiles"]:
                reason += " 产出物文件缺失，需要先修复引用。"
            elif summary["emptyFiles"]:
                reason += " 产出物文件为空，需要复核内容。"
        downstream.append({
            "phase": item,
            "phaseName": PHASE_NAMES[item],
            **summary,
            "needsReview": needs_review,
            "reason": reason,
        })
    current = artifact_summary(artifacts.get(phase, {}))
    return {
        "phase": phase,
        "phaseName": PHASE_NAMES[phase],
        "currentArtifact": current,
        "downstream": downstream,
        "shouldWarnBeforeChange": any(item["needsReview"] for item in downstream),
    }


def validate_module_id(module_id: str) -> None:
    if not MODULE_ID_RE.fullmatch(module_id):
        raise SfkError("moduleId 只能包含小写字母、数字、连字符，且不能以连字符开头或结尾。")


def suggest_module_id(display_name: str) -> str:
    text = display_name.strip()
    candidate = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()
    if candidate and MODULE_ID_RE.fullmatch(candidate):
        return candidate
    raise SfkError(
        "脚本层无法根据模块名称可靠生成合法 moduleId。请使用 --id 显式指定，"
        "例如：--id user-management"
    )


def default_implementation_approval() -> dict[str, Any]:
    return {
        "required": True,
        "status": "pending",
        "approvedAt": None,
        "approvedBy": None,
        "approvedForFile": None,
        "approvedForConfirmedAt": None,
        "summary": None,
    }


def ensure_implementation_approval(artifact: dict[str, Any]) -> dict[str, Any]:
    approval = artifact.get("implementationApproval")
    if not isinstance(approval, dict):
        approval = default_implementation_approval()
        artifact["implementationApproval"] = approval
    default = default_implementation_approval()
    for key, value in default.items():
        approval.setdefault(key, value)
    return approval


def reset_implementation_approval(artifact: dict[str, Any]) -> None:
    artifact["implementationApproval"] = default_implementation_approval()


def phase_template() -> dict[str, Any]:
    artifacts = {
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
    artifacts["development"]["implementationApproval"] = default_implementation_approval()
    return artifacts


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
        raise SfkError(f"moduleId 已存在：{module_id}。请使用 --id 指定其他 moduleId。")
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


def phase_summary(artifact: dict[str, Any], phase: str | None = None) -> str:
    status = artifact.get("status", "pending")
    quality = artifact.get("quality")
    files = artifact.get("files") or []
    file_text = files[-1] if files else ""
    quality_text = f" {quality}" if quality else ""
    warning = ""
    if status == "done" and quality == "confirmed":
        health = artifact_files_health(files)
        if not health["hasUsableFile"]:
            warning = " ⚠️ 产出物文件缺失或为空"
    approval_text = ""
    if phase == "development":
        approval = ensure_implementation_approval(artifact)
        approval_text = f" 实现授权:{approval.get('status', 'pending')}"
    return f"{status}{quality_text} {file_text}{approval_text}{warning}".rstrip()


def next_step_suggestion(state: dict[str, Any]) -> str:
    artifacts = state.get("artifacts", {})
    requirement = artifacts.get("requirement", {})
    ui_design = artifacts.get("ui_design", {})
    system_design = artifacts.get("system_design", {})
    development = artifacts.get("development", {})
    code_review = artifacts.get("code_review", {})
    testing = artifacts.get("testing", {})
    deployment = artifacts.get("deployment", {})
    if artifact_is_satisfied(deployment):
        return "💡 下一步建议：核心交付流程已完成；请按已确认部署文档执行上线、监控和回滚预案。"
    if deployment.get("status") == "in_progress" or deployment.get("quality") == "draft":
        return "💡 下一步建议：继续使用 /sfk-deploy 完善并确认部署文档草稿。"
    if not artifact_is_satisfied(requirement):
        if requirement.get("status") == "in_progress" or requirement.get("quality") == "draft":
            return "💡 下一步建议：继续使用 /sfk-req 完善并确认需求草稿。"
        return "💡 下一步建议：/sfk-req <需求描述>"
    if artifact_is_satisfied(system_design):
        if artifact_is_satisfied(development):
            approval_status = implementation_approval_status(state)
            if approval_status["canImplement"]:
                if artifact_is_satisfied(code_review):
                    if artifact_is_satisfied(testing):
                        return "💡 下一步建议：测试文档已确认，可继续进入 /sfk-deploy；部署前会检查所有模块测试产出物是否已确认且可用。"
                    if testing.get("status") == "in_progress" or testing.get("quality") == "draft":
                        return "💡 下一步建议：继续使用 /sfk-test 完善并确认测试文档草稿。"
                    return "💡 下一步建议：代码审查文档已确认，可继续进入 /sfk-test，并将审查风险纳入测试覆盖。"
                if code_review.get("status") == "in_progress" or code_review.get("quality") == "draft":
                    return "💡 下一步建议：继续使用 /sfk-code-review 完善并确认代码审查文档草稿。"
                return "💡 下一步建议：源码实现已获授权，可按开发文档完成实现后进入 /sfk-code-review。"
            if approval_status["reason"] == "implementation_approval_stale":
                return "💡 下一步建议：开发文档已更新，请使用 /sfk-dev 重新进行源码实现二次确认。"
            return "💡 下一步建议：使用 /sfk-dev 进行源码实现二次确认；开发文档 confirmed 不代表已授权修改源码。"
        if development.get("status") == "in_progress" or development.get("quality") == "draft":
            return "💡 下一步建议：继续使用 /sfk-dev 完善并确认开发文档草稿。"
        return "💡 下一步建议：/sfk-dev"
    if system_design.get("status") == "in_progress" or system_design.get("quality") == "draft":
        return "💡 下一步建议：继续使用 /sfk-design 完善并确认系统设计草稿。"
    if not artifact_is_satisfied(ui_design):
        if ui_design.get("status") == "in_progress" or ui_design.get("quality") == "draft":
            return "💡 下一步建议：继续使用 /sfk-ui 完善并确认 UI 设计草稿；也可带假设进入 /sfk-design。"
        return "💡 下一步建议：/sfk-ui；如需先做技术架构，也可进入 /sfk-design。"
    return "💡 下一步建议：/sfk-design"


def print_dependency_warnings(state: dict[str, Any]) -> None:
    for phase_id, phase_name in PHASES:
        info = dependency_status(state, phase_id)
        if info["status"] == "done" and info["quality"] == "confirmed" and not info["satisfied"]:
            print(f"  ⚠️ {phase_name} 已标记 confirmed，但产出物不可用：{info['reason']}")


def module_status(_: argparse.Namespace) -> None:
    index, state, module_id = require_current_state()
    module = state.get("module", {})
    print(f"📋 当前模块：{module.get('displayName')}（{module_id}）")
    print(f"当前阶段：{state.get('currentPhase', 'requirement')}")
    print("阶段状态：")
    artifacts = state.get("artifacts", {})
    for phase_id, phase_name in PHASES:
        print(f"  - {phase_name}：{phase_summary(artifacts.get(phase_id, {}), phase_id)}")
    print_dependency_warnings(state)


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
        print(f"  - {phase_name}：{phase_summary(artifacts.get(phase_id, {}), phase_id)}")
    print_dependency_warnings(state)
    print(f"\n{next_step_suggestion(state)}")


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
    validate_phase(phase)
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
    validate_phase(phase)
    enforce_hard_dependencies(state, phase)
    if phase == "code_review":
        enforce_code_review_readiness(state)
    artifact = state.setdefault("artifacts", {}).setdefault(phase, {})
    timestamp = now_iso()
    quality_warnings: list[str] = []
    if confirmed:
        files = artifact.get("files") or []
        if not files:
            raise SfkError("没有可确认的阶段产出物。请先保存草稿后再确认。")
        quality_result = validate_artifact_quality_document(phase, files[-1], confirmed=True)
        if quality_result["errors"]:
            raise SfkError(artifact_quality_error_prefix(phase) + "；".join(quality_result["errors"]))
        quality_warnings = quality_result["warnings"]
        owner = current_owner(index)
        artifact["status"] = "done"
        artifact["quality"] = "confirmed"
        artifact["confirmedAt"] = timestamp
        artifact["owner"] = owner
        artifact["version"] = artifact.get("version") or "1.0.0"
        if phase == "development":
            ensure_implementation_approval(artifact)
        action = f"confirm_{phase}"
        detail = f"确认阶段产出物：{phase}"
    else:
        owner = None
        file_path = normalize_artifact_file(args.file)
        quality_result = validate_artifact_quality_document(phase, file_path, confirmed=False)
        if quality_result["errors"]:
            raise SfkError(artifact_quality_error_prefix(phase) + "；".join(quality_result["errors"]))
        quality_warnings = quality_result["warnings"]
        artifact["status"] = "in_progress"
        artifact["quality"] = "draft"
        files = artifact.setdefault("files", [])
        if file_path not in files:
            files.append(file_path)
        artifact["confirmedAt"] = None
        artifact["version"] = artifact.get("version") or "0.1.0"
        if phase == "development":
            reset_implementation_approval(artifact)
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
    if phase in QUALITY_CHECK_PHASES:
        if quality_warnings:
            print("qualityCheck：warnings")
            for warning in quality_warnings:
                print(f"  - {warning}")
        else:
            print("qualityCheck：passed")
    if confirmed:
        print(f"owner：{artifact.get('owner')}")


def phase_check(args: argparse.Namespace) -> None:
    _, state, module_id = require_current_state()
    phase = args.phase
    result = check_phase_dependencies(state, phase)
    result["moduleId"] = module_id
    print(json.dumps(result, ensure_ascii=False, indent=2))


def context_discover(args: argparse.Namespace) -> None:
    result = discover_project_context(args.phase)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def artifact_impact(args: argparse.Namespace) -> None:
    _, state, module_id = require_current_state()
    result = artifact_impact_report(state, args.phase)
    result["moduleId"] = module_id
    print(json.dumps(result, ensure_ascii=False, indent=2))


def deployment_readiness(_: argparse.Namespace) -> None:
    index = require_index()
    result = deployment_readiness_report(index)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def code_review_readiness(_: argparse.Namespace) -> None:
    _, state, module_id = require_current_state()
    result = code_review_readiness_report(state)
    result["moduleId"] = module_id
    print(json.dumps(result, ensure_ascii=False, indent=2))


def implementation_current(args: argparse.Namespace) -> None:
    if args.phase != "development":
        raise SfkError("当前仅支持查看 development 阶段的源码实现授权状态。")
    _, state, module_id = require_current_state()
    result = implementation_approval_status(state)
    result["moduleId"] = module_id
    result["phase"] = "development"
    result["phaseName"] = PHASE_NAMES["development"]
    print(json.dumps(result, ensure_ascii=False, indent=2))


def implementation_approve(args: argparse.Namespace) -> None:
    if args.phase != "development":
        raise SfkError("当前仅支持批准 development 阶段的源码实现。")
    summary = args.summary.strip()
    if not summary:
        raise SfkError("源码实现授权摘要不能为空，请说明本次允许实现的范围。")
    index, state, module_id = require_current_state()
    development = state.setdefault("artifacts", {}).setdefault("development", {})
    status = implementation_approval_status(state)
    if status["reason"] in {
        "development_document_missing",
        "development_document_draft",
        "development_document_file_missing",
        "development_document_file_empty",
    }:
        raise SfkError(f"开发文档尚未满足源码实现授权条件：{status['reason']}")
    approval = ensure_implementation_approval(development)
    if status["canImplement"]:
        print("✅ 源码实现授权已存在。")
        print(f"approvedBy：{approval.get('approvedBy')}")
        print(f"approvedAt：{approval.get('approvedAt')}")
        print("提示：未覆盖既有授权。")
        return
    timestamp = now_iso()
    owner = current_owner(index)
    current_file = status["developmentArtifact"]["currentFile"]
    approval.update({
        "required": True,
        "status": "approved",
        "approvedAt": timestamp,
        "approvedBy": owner,
        "approvedForFile": current_file,
        "approvedForConfirmedAt": status["developmentArtifact"].get("confirmedAt"),
        "summary": summary,
    })
    state.setdefault("module", {})["updatedAt"] = timestamp
    state.setdefault("history", []).append({
        "action": "approve_development_implementation",
        "timestamp": timestamp,
        "user": owner,
        "detail": summary,
        "files": [current_file] if current_file else [],
    })
    write_json(state_path(module_id), state)
    index.setdefault("modules", {}).setdefault(module_id, {})["updatedAt"] = timestamp
    index.setdefault("project", {})["updatedAt"] = timestamp
    write_json(index_path(), index)
    print("✅ 源码实现二次确认已记录。")
    print("提示：现在可以按已确认开发文档开始修改源码；这不代表源码已经实现完成。")
    print(f"approvedBy：{owner}")
    print(f"approvedForFile：{current_file}")


def validate_reset_scope(scope: str) -> str:
    if scope not in RESET_SCOPES:
        raise SfkError(f"未知 reset scope：{scope}")
    return scope


def validate_reset_confirmation(confirm: str) -> None:
    if confirm != RESET_CONFIRM_PHRASE:
        raise SfkError(f"确认语不匹配。高风险重置必须输入完全一致的确认语：{RESET_CONFIRM_PHRASE}")


def reset_target_module_ids(index: dict[str, Any], scope: str) -> list[str]:
    scope = validate_reset_scope(scope)
    modules = index.get("modules", {})
    if scope == "current-module":
        module_id = index.get("currentModule")
        if not module_id:
            raise SfkError("当前项目还没有当前模块，无需重置。请先执行：/sfk-module create <名称>")
        if module_id not in modules:
            raise SfkError(f"currentModule 指向不存在的模块：{module_id}")
        validate_module_id(module_id)
        return [module_id]
    if not modules:
        raise SfkError("当前项目还没有模块，无需执行项目级重置。")
    module_ids = list(modules.keys())
    for module_id in module_ids:
        validate_module_id(module_id)
    return module_ids


def load_reset_targets(index: dict[str, Any], scope: str) -> list[tuple[str, dict[str, Any], dict[str, Any]]]:
    targets: list[tuple[str, dict[str, Any], dict[str, Any]]] = []
    for module_id in reset_target_module_ids(index, scope):
        module_info = index.get("modules", {}).get(module_id, {})
        state = read_json(state_path(module_id))
        if state.get("schemaVersion") != SCHEMA_VERSION:
            raise SfkError(f"模块状态 schemaVersion 不支持：{state.get('schemaVersion')}")
        targets.append((module_id, module_info, state))
    return targets


def reset_module_impact(module_id: str, module_info: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    artifacts = state.get("artifacts", {})
    artifacts_to_reset: list[dict[str, Any]] = []
    referenced_files: list[str] = []
    for phase, phase_name in PHASES:
        artifact = artifacts.get(phase, {})
        summary = artifact_summary(artifact)
        files = summary["files"]
        referenced_files.extend(files)
        artifacts_to_reset.append({
            "phase": phase,
            "phaseName": phase_name,
            "status": summary["status"],
            "quality": summary["quality"],
            "currentFile": summary["currentFile"],
            "files": files,
            "missingFiles": summary["missingFiles"],
            "emptyFiles": summary["emptyFiles"],
            "hasUsableFile": summary["hasUsableFile"],
        })
    preserved_files = list(dict.fromkeys(referenced_files))
    return {
        "moduleId": module_id,
        "displayName": module_info.get("displayName") or state.get("module", {}).get("displayName") or module_id,
        "statePath": rel(state_path(module_id)),
        "docsPath": rel(docs_dir(module_id)) + "/",
        "currentPhase": state.get("currentPhase", "requirement"),
        "referencedArtifactFilesPreserved": preserved_files,
        "artifactsToReset": artifacts_to_reset,
    }


def reset_impact_report(index: dict[str, Any], scope: str) -> dict[str, Any]:
    scope = validate_reset_scope(scope)
    targets = load_reset_targets(index, scope)
    modules = [reset_module_impact(module_id, module_info, state) for module_id, module_info, state in targets]
    will_modify = [rel(index_path())]
    will_modify.extend(item["statePath"] for item in modules)
    return {
        "operation": "reset",
        "mode": "impact",
        "highRisk": True,
        "scope": scope,
        "confirmationPhrase": RESET_CONFIRM_PHRASE,
        "docsPreservedByDefault": True,
        "willModify": list(dict.fromkeys(will_modify)),
        "willDelete": [],
        "willNotModify": [
            "docs/super-flow-kit/",
            "business source files",
        ],
        "backupRecommendation": [
            ".sfk/",
            "docs/super-flow-kit/",
        ],
        "modules": modules,
        "message": f"第一次调用仅展示影响范围；如确认重置，请单独回复：{RESET_CONFIRM_PHRASE}",
    }


def reset_state_for_module(state: dict[str, Any], index: dict[str, Any], timestamp: str, scope: str) -> None:
    state["currentPhase"] = "requirement"
    state["artifacts"] = phase_template()
    state.setdefault("module", {})["updatedAt"] = timestamp
    state.setdefault("history", []).append({
        "action": "reset_workflow_state",
        "timestamp": timestamp,
        "user": current_owner(index),
        "detail": f"重置 super-flow-kit 工作流状态，scope={scope}；产出物文档保留。",
        "files": [],
    })


def sync_index_after_reset(index: dict[str, Any], module_ids: list[str], timestamp: str) -> None:
    modules = index.setdefault("modules", {})
    for module_id in module_ids:
        module_info = modules.setdefault(module_id, {})
        module_info["currentPhase"] = "requirement"
        module_info["updatedAt"] = timestamp
    index.setdefault("project", {})["updatedAt"] = timestamp


def reset_impact(args: argparse.Namespace) -> None:
    index = require_index()
    report = reset_impact_report(index, args.scope)
    print(json.dumps(report, ensure_ascii=False, indent=2))


def reset_apply(args: argparse.Namespace) -> None:
    validate_reset_confirmation(args.confirm)
    index = require_index()
    scope = validate_reset_scope(args.scope)
    targets = load_reset_targets(index, scope)
    timestamp = now_iso()
    module_ids = [module_id for module_id, _, _ in targets]
    for _, _, state in targets:
        reset_state_for_module(state, index, timestamp, scope)
    for module_id, _, state in targets:
        write_json(state_path(module_id), state)
    sync_index_after_reset(index, module_ids, timestamp)
    write_json(index_path(), index)
    print("✅ super-flow-kit 状态已重置。")
    print(f"scope：{scope}")
    print(f"modules：{', '.join(module_ids)}")
    print("modified：")
    print(f"  - {rel(index_path())}")
    for module_id in module_ids:
        print(f"  - {rel(state_path(module_id))}")
    print("preserved：")
    print("  - docs/super-flow-kit/")
    print("  - business source files")
    print("提示：产出物文档未删除，但已不再作为当前工作流状态引用。")
    print("下一步建议：/sfk-status")


def export_module(args: argparse.Namespace) -> None:
    index = require_index()
    module_id = args.module_id
    if not module_id:
        _, _, module_id = require_current_state(index)
    result = write_module_export_package(index, module_id, args.zip)
    print("✅ 模块交付包已导出。")
    print(f"exportType：module")
    print(f"moduleId：{module_id}")
    print(f"outputDir：{result['outputDir']}")
    print(f"manifest：{result['manifest']}")
    if result.get("zipPath"):
        print(f"zipPath：{result['zipPath']}")
    print(f"riskCount：{result['riskCount']}")


def export_project(args: argparse.Namespace) -> None:
    index = require_index()
    result = write_project_export_package(index, args.zip)
    print("✅ 项目交付包已导出。")
    print("exportType：project")
    print(f"outputDir：{result['outputDir']}")
    print(f"manifest：{result['manifest']}")
    if result.get("zipPath"):
        print(f"zipPath：{result['zipPath']}")
    print(f"riskCount：{result['riskCount']}")


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
    p_impact = artifact_sub.add_parser("impact")
    p_impact.add_argument("phase")
    p_impact.set_defaults(func=artifact_impact)

    p_context = sub.add_parser("context")
    context_sub = p_context.add_subparsers(dest="context_command", required=True)
    p_discover = context_sub.add_parser("discover")
    p_discover.add_argument("--phase", required=True)
    p_discover.set_defaults(func=context_discover)

    p_phase = sub.add_parser("phase")
    phase_sub = p_phase.add_subparsers(dest="phase_command", required=True)
    p_phase_check = phase_sub.add_parser("check")
    p_phase_check.add_argument("phase")
    p_phase_check.set_defaults(func=phase_check)

    p_deployment = sub.add_parser("deployment")
    deployment_sub = p_deployment.add_subparsers(dest="deployment_command", required=True)
    p_deployment_readiness = deployment_sub.add_parser("readiness")
    p_deployment_readiness.set_defaults(func=deployment_readiness)

    p_code_review = sub.add_parser("code-review")
    code_review_sub = p_code_review.add_subparsers(dest="code_review_command", required=True)
    p_code_review_readiness = code_review_sub.add_parser("readiness")
    p_code_review_readiness.set_defaults(func=code_review_readiness)

    p_export = sub.add_parser("export")
    export_sub = p_export.add_subparsers(dest="export_command", required=True)
    p_export_module = export_sub.add_parser("module")
    p_export_module.add_argument("module_id", nargs="?")
    p_export_module.add_argument("--zip", action="store_true")
    p_export_module.set_defaults(func=export_module)
    p_export_project = export_sub.add_parser("project")
    p_export_project.add_argument("--zip", action="store_true")
    p_export_project.set_defaults(func=export_project)

    p_reset = sub.add_parser("reset")
    reset_sub = p_reset.add_subparsers(dest="reset_command", required=True)
    p_reset_impact = reset_sub.add_parser("impact")
    p_reset_impact.add_argument("--scope", choices=sorted(RESET_SCOPES), default="current-module")
    p_reset_impact.set_defaults(func=reset_impact)
    p_reset_apply = reset_sub.add_parser("apply")
    p_reset_apply.add_argument("--scope", choices=sorted(RESET_SCOPES), default="current-module")
    p_reset_apply.add_argument("--confirm", required=True)
    p_reset_apply.set_defaults(func=reset_apply)

    p_impl = sub.add_parser("implementation")
    impl_sub = p_impl.add_subparsers(dest="implementation_command", required=True)
    p_impl_current = impl_sub.add_parser("current")
    p_impl_current.add_argument("phase")
    p_impl_current.set_defaults(func=implementation_current)
    p_impl_approve = impl_sub.add_parser("approve")
    p_impl_approve.add_argument("phase")
    p_impl_approve.add_argument("--summary", required=True)
    p_impl_approve.set_defaults(func=implementation_approve)

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
