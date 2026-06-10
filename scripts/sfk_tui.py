#!/usr/bin/env python3
"""Reusable terminal selection helpers for super-flow-kit.

This module is intentionally state-free: it only reads keyboard input and prints
machine-readable selection results. Project state remains owned by sfk.py.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from typing import Any


@dataclass
class Option:
    key: str
    label: str


def emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False))


def parse_options(values: list[str]) -> list[Option]:
    options: list[Option] = []
    seen: set[str] = set()
    for value in values:
        if "=" not in value:
            raise ValueError(f"选项必须使用 key=label 格式：{value}")
        key, label = value.split("=", 1)
        key = key.strip()
        label = label.strip()
        if not key:
            raise ValueError(f"选项 key 不能为空：{value}")
        if key in seen:
            raise ValueError(f"选项 key 重复：{key}")
        seen.add(key)
        options.append(Option(key=key, label=label or key))
    if not options:
        raise ValueError("至少需要提供一个 --option。")
    return options


def is_interactive() -> bool:
    return sys.stdin.isatty() and sys.stderr.isatty()


def enable_windows_ansi() -> None:
    if os.name != "nt":
        return
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)
    except Exception:
        return


def read_key() -> str:
    if os.name == "nt":
        import msvcrt

        ch = msvcrt.getwch()
        if ch in ("\x00", "\xe0"):
            nxt = msvcrt.getwch()
            if nxt == "H":
                return "up"
            if nxt == "P":
                return "down"
            return "unknown"
        if ch in ("\r", "\n"):
            return "enter"
        if ch == " ":
            return "space"
        if ch == "\x1b":
            return "escape"
        if ch.lower() == "q":
            return "cancel"
        if ch.lower() == "j":
            return "down"
        if ch.lower() == "k":
            return "up"
        return ch

    import termios
    import tty

    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == "\x1b":
            seq = sys.stdin.read(2)
            if seq == "[A":
                return "up"
            if seq == "[B":
                return "down"
            return "escape"
        if ch in ("\r", "\n"):
            return "enter"
        if ch == " ":
            return "space"
        if ch.lower() == "q":
            return "cancel"
        if ch.lower() == "j":
            return "down"
        if ch.lower() == "k":
            return "up"
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def clear_lines(count: int) -> None:
    if count <= 0:
        return
    for _ in range(count):
        sys.stderr.write("\x1b[2K\r")
        sys.stderr.write("\x1b[1A")
    sys.stderr.write("\x1b[2K\r")


def render(title: str, description: str | None, mode: str, options: list[Option], cursor: int, selected: set[str], first: bool) -> int:
    lines: list[str] = []
    lines.append(title)
    if description:
        lines.append(description)
    hint = "↑/↓ 或 j/k 移动，Enter 确认，q/Esc 取消"
    if mode == "multi":
        hint = "↑/↓ 或 j/k 移动，Space 选择/取消，Enter 确认，q/Esc 取消"
    lines.append(hint)
    lines.append("")
    for index, option in enumerate(options):
        pointer = "❯" if index == cursor else " "
        if mode == "multi":
            mark = "[x]" if option.key in selected else "[ ]"
            lines.append(f"{pointer} {mark} {option.label}")
        else:
            mark = "●" if option.key in selected else "○"
            lines.append(f"{pointer} {mark} {option.label}")
    if not first:
        clear_lines(len(lines))
    sys.stderr.write("\n".join(lines) + "\n")
    sys.stderr.flush()
    return len(lines)


def run_loop(title: str, description: str | None, mode: str, options: list[Option], defaults: list[str]) -> dict[str, Any]:
    keys = [option.key for option in options]
    selected = {key for key in defaults if key in keys}
    if mode == "single":
        selected = {next(iter(selected), keys[0])}
    cursor = keys.index(next(iter(selected))) if selected else 0
    first = True

    sys.stderr.write("\x1b[?25l")
    sys.stderr.flush()
    try:
        while True:
            render(title, description, mode, options, cursor, selected, first)
            first = False
            key = read_key()
            if key == "up":
                cursor = (cursor - 1) % len(options)
            elif key == "down":
                cursor = (cursor + 1) % len(options)
            elif key == "space" and mode == "multi":
                current = keys[cursor]
                if current in selected:
                    selected.remove(current)
                else:
                    selected.add(current)
            elif key == "enter":
                if mode == "single":
                    selected = {keys[cursor]}
                return {
                    "status": "confirmed",
                    "mode": mode,
                    "selected": [key for key in keys if key in selected],
                }
            elif key in {"escape", "cancel"}:
                return {"status": "cancelled", "mode": mode, "selected": []}
    finally:
        sys.stderr.write("\x1b[?25h")
        sys.stderr.flush()


def run_select(args: Any) -> int:
    try:
        options = parse_options(args.option)
        defaults = args.default or []
        if not is_interactive():
            emit({
                "status": "non_interactive",
                "mode": args.mode,
                "selected": [],
                "options": [{"key": item.key, "label": item.label} for item in options],
            })
            return 0
        enable_windows_ansi()
        result = run_loop(args.title, args.description, args.mode, options, defaults)
        emit(result)
        return 0
    except ValueError as exc:
        emit({"status": "error", "message": str(exc)})
        return 1
