from __future__ import annotations

import logging

import httpx
from telegram import Update
from telegram.ext import ContextTypes

from src.bot.config import get_config
from src.commands import CommandHandler, parse_command

logger = logging.getLogger(__name__)


def _is_allowed(user_id: int) -> bool:
    config = get_config()
    if not config.allowed_user_ids:
        return True
    return user_id in config.allowed_user_ids


async def _check_access(update: Update) -> bool:
    user = update.effective_user
    if user and _is_allowed(user.id):
        return True
    await update.effective_message.reply_text("⛔ Bu botu kullanma yetkiniz yok.")
    return False


async def _api_get(path: str):
    config = get_config()
    async with httpx.AsyncClient(base_url=config.api_base_url) as client:
        resp = await client.get(path, timeout=15)
        resp.raise_for_status()
        return resp.json()


async def _api_post(path: str, json: dict | None = None):
    config = get_config()
    async with httpx.AsyncClient(base_url=config.api_base_url) as client:
        resp = await client.post(path, json=json, timeout=30)
        resp.raise_for_status()
        return resp.json()


async def _api_patch(path: str, json: dict | None = None):
    config = get_config()
    async with httpx.AsyncClient(base_url=config.api_base_url) as client:
        resp = await client.patch(path, json=json, timeout=15)
        resp.raise_for_status()
        return resp.json()


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _check_access(update):
        return
    try:
        agents = await _api_get("/api/v1/agents")
    except Exception:
        agents = []
    lines = [
        "🤖 *AgentManager Telegram Bot'a Hoşgeldiniz!*\n",
        "Mevcut komutlar:",
        "• `/start` — Bu mesaj",
        "• `/agents` — Kullanılabilir ajanları listele",
        "• `/status` — Ajan durum özeti",
        "• `/agent <isim>` — Aktif ajanı değiştir",
        "• `/tasks` — Görevleri listele",
        "• `/pause <isim>` — Ajanı duraklat",
        "• `/resume <isim>` — Ajanı devam ettir",
        "",
    ]
    if agents:
        lines.append("📋 *Kullanılabilir Ajanlar:*")
        for a in agents:
            lines.append(f"  • `{a['name']}` — {a['role']} ({a['status']})")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def handle_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _check_access(update):
        return
    try:
        agents = await _api_get("/api/v1/agents")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ajan listesi alınamadı: {e}")
        return
    if not agents:
        await update.message.reply_text("Hiç ajan bulunamadı.")
        return
    lines = ["📊 *Ajan Durum Özeti*\n"]
    for a in agents:
        status_icon = {"idle": "🟢", "busy": "🟡", "paused": "🔴", "error": "⛔"}.get(
            a.get("status", ""), "⚪"
        )
        lines.append(
            f"{status_icon} *{a['name']}*\n"
            f"   Role: `{a['role']}` | Model: `{a['provider']}/{a['model']}`\n"
            f"   Durum: `{a['status']}` | Aktif: `{a['is_active']}`"
        )
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def handle_agents(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _check_access(update):
        return
    try:
        agents = await _api_get("/api/v1/agents")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ajan listesi alınamadı: {e}")
        return
    if not agents:
        await update.message.reply_text("Hiç ajan bulunamadı.")
        return
    lines = ["📋 *Kullanılabilir Ajanlar*\n"]
    for a in agents:
        lines.append(
            f"• `{a['name']}` — {a['role']}\n"
            f"  ID: `{a['id']}` | Durum: `{a['status']}`"
        )
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def handle_agent(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _check_access(update):
        return
    args = context.args
    if not args:
        await update.message.reply_text(
            "Kullanım: `/agent <ajan_adı>`\nÖrnek: `/agent code-agent`",
            parse_mode="Markdown",
        )
        return
    name = " ".join(args)
    try:
        agents = await _api_get("/api/v1/agents")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ajan listesi alınamadı: {e}")
        return
    match = next((a for a in agents if a["name"] == name), None)
    if not match:
        available = ", ".join(f"`{a['name']}`" for a in agents)
        await update.message.reply_text(
            f"❌ `{name}` bulunamadı.\nMevcut ajanlar: {available}",
            parse_mode="Markdown",
        )
        return
    chat_id = str(update.effective_chat.id)
    try:
        await _api_post(f"/api/v1/session/{chat_id}/agent/{match['id']}")
        await update.message.reply_text(
            f"✅ Aktif ajan `{name}` olarak değiştirildi.",
            parse_mode="Markdown",
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ajan değiştirilemedi: {e}")


async def handle_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _check_access(update):
        return
    try:
        tasks = await _api_get("/api/v1/tasks")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Görev listesi alınamadı: {e}")
        return
    if not tasks:
        await update.message.reply_text("Hiç görev bulunamadı.")
        return
    lines = ["📌 *Görevler*\n"]
    for t in tasks[:10]:
        status_icon = {
            "pending": "⏳", "running": "🔄", "completed": "✅", "failed": "❌",
        }.get(t.get("status", ""), "⚪")
        goal = t["goal"][:80] + "..." if len(t["goal"]) > 80 else t["goal"]
        lines.append(f"{status_icon} `{t['id'][:8]}...` {goal}")
    if len(tasks) > 10:
        lines.append(f"\n*+{len(tasks) - 10} görev daha*")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def handle_pause(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _check_access(update):
        return
    args = context.args
    if not args:
        await update.message.reply_text(
            "Kullanım: `/pause <ajan_adı>`\nÖrnek: `/pause code-agent`",
            parse_mode="Markdown",
        )
        return
    name = " ".join(args)
    try:
        agents = await _api_get("/api/v1/agents")
        match = next((a for a in agents if a["name"] == name), None)
        if not match:
            available = ", ".join(f"`{a['name']}`" for a in agents)
            await update.message.reply_text(
                f"❌ `{name}` bulunamadı.\nMevcut ajanlar: {available}",
                parse_mode="Markdown",
            )
            return
        await _api_patch(f"/api/v1/agents/{match['id']}", {"status": "paused"})
        await update.message.reply_text(
            f"⏸️ Ajan `{name}` duraklatıldı.",
            parse_mode="Markdown",
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ajan duraklatılamadı: {e}")


async def handle_resume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _check_access(update):
        return
    args = context.args
    if not args:
        await update.message.reply_text(
            "Kullanım: `/resume <ajan_adı>`\nÖrnek: `/resume code-agent`",
            parse_mode="Markdown",
        )
        return
    name = " ".join(args)
    try:
        agents = await _api_get("/api/v1/agents")
        match = next((a for a in agents if a["name"] == name), None)
        if not match:
            available = ", ".join(f"`{a['name']}`" for a in agents)
            await update.message.reply_text(
                f"❌ `{name}` bulunamadı.\nMevcut ajanlar: {available}",
                parse_mode="Markdown",
            )
            return
        await _api_patch(f"/api/v1/agents/{match['id']}", {"status": "idle"})
        await update.message.reply_text(
            f"▶️ Ajan `{name}` devam ettiriliyor.",
            parse_mode="Markdown",
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ajan devam ettirilemedi: {e}")


async def handle_map(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _check_access(update):
        return
    path = " ".join(context.args) if context.args else "."
    try:
        result = await _api_post(
            "/api/v1/tools/repo-map",
            {"path": path, "depth": 3, "include_signatures": False},
        )
        map_text = result.get("map", "")
        if not map_text:
            await update.message.reply_text("⚠️ Repo haritası oluşturulamadı.")
            return
        text = f"📂 *Repo Haritası:* `{path}`\n```\n{map_text}\n```"
        if len(text) > 4000:
            text = text[:4000] + "\n... (devamı kesildi)"
        await update.message.reply_text(text, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Repo haritası alınamadı: {e}")


async def handle_free_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _check_access(update):
        return
    chat_id = str(update.effective_chat.id)
    message_text = update.message.text
    if not message_text:
        return

    cmd = parse_command(message_text)
    if cmd:
        try:
            session_data = await _api_get(f"/api/v1/session/{chat_id}")
            agent_id = session_data.get("active_agent_id", chat_id)
            result = await _api_post(
                "/api/v1/chat",
                {"agent_id": agent_id, "message": message_text},
            )
            await update.message.reply_text(
                result.get("response", ""), parse_mode="Markdown"
            )
        except Exception as e:
            await update.message.reply_text(f"⚠️ Komut hatası: {e}")
        return

    try:
        session = await _api_get(f"/api/v1/session/{chat_id}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Oturum alınamadı: {e}")
        return
    agent_id = session.get("active_agent_id")
    if not agent_id:
        await update.message.reply_text(
            "❌ Henüz aktif bir ajan seçilmedi.\n"
            "Kullanılabilir ajanları görmek için `/agents` yazın,\n"
            "seçmek için `/agent <isim>` yazın.",
            parse_mode="Markdown",
        )
        return
    await update.message.reply_chat_action("typing")
    try:
        result = await _api_post(
            "/api/v1/chat",
            {"agent_id": agent_id, "message": message_text},
        )
        response = result.get("response", "")
        used = result.get("used_model", "?")
        await update.message.reply_text(
            f"{response}\n\n— _{used}_", parse_mode="Markdown"
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ Yanıt alınamadı: {e}")
