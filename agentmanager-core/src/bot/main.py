from __future__ import annotations

import logging

from telegram import BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from src.bot.config import get_config
from src.bot.handlers import (
    handle_agent,
    handle_agents,
    handle_free_text,
    handle_map,
    handle_pause,
    handle_resume,
    handle_start,
    handle_status,
    handle_tasks,
)

logger = logging.getLogger(__name__)


def build_application() -> Application:
    config = get_config()

    async def _post_init(app: Application) -> None:
        commands = [
            BotCommand("start", "Hoşgeldin mesajı ve ajan listesi"),
            BotCommand("status", "Tüm ajanların durum özeti"),
            BotCommand("agents", "Kullanılabilir ajanları listele"),
            BotCommand("agent", "<isim> ile aktif ajanı değiştir"),
            BotCommand("tasks", "Bekleyen/tamamlanan görevler"),
            BotCommand("pause", "<isim> ile ajanı duraklat"),
            BotCommand("resume", "<isim> ile ajanı devam ettir"),
            BotCommand("map", "[yol] ile repo haritasını göster"),
        ]
        await app.bot.set_my_commands(commands)

    app = (
        Application.builder()
        .token(config.token)
        .post_init(_post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", handle_start))
    app.add_handler(CommandHandler("status", handle_status))
    app.add_handler(CommandHandler("agents", handle_agents))
    app.add_handler(CommandHandler("tasks", handle_tasks))
    app.add_handler(CommandHandler("agent", handle_agent))
    app.add_handler(CommandHandler("pause", handle_pause))
    app.add_handler(CommandHandler("resume", handle_resume))
    app.add_handler(CommandHandler("map", handle_map))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_free_text))

    return app


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    config = get_config()
    if not config.token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is not set")
        return

    app = build_application()
    logger.info("Starting AgentManager Telegram Bot (polling)...")
    app.run_polling()


if __name__ == "__main__":
    main()
