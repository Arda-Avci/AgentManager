from __future__ import annotations

import re


_COMMANDS: dict[str, str] = {
    "add": "/add <dosya> — Context'e dosya ekle",
    "drop": "/drop <dosya> — Dosyayi context'ten cikar",
    "undo": "/undo — Son islemi geri al",
    "diff": "/diff — Son degisiklikleri goster",
    "run": "/run <komut> — Shell komutu calistir (allowlist)",
    "help": "/help — Bu mesaji goster",
}


def parse_command(text: str) -> dict | None:
    if not text or not text.startswith("/"):
        return None
    text = text.lstrip()
    m = re.match(r"^/(\w+)(?:\s+(.*))?$", text)
    if not m:
        return None
    name = m.group(1).lower()
    args = (m.group(2) or "").strip()
    if name not in _COMMANDS:
        return None
    return {"name": name, "args": args}


def get_help_text() -> str:
    lines = [
        "*Kullanilabilir komutlar:*\n",
    ]
    for desc in _COMMANDS.values():
        lines.append(f"  `{desc}`")
    return "\n".join(lines)
