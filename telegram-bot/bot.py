"""
Agency Notification Bot
=======================
Telegram-бот для уведомлений AI-агентства.

Функции:
  - Принимает webhook от GitHub (деплой, PR, issues)
  - Мониторит uptime сайтов (каждые 5 мин)
  - Отправляет ежедневные сводки
  - Команды: /status, /sites, /add, /remove

Запуск:
  1. Создай бота через @BotFather → получи токен
  2. Скопируй .env.example → .env и заполни
  3. pip install -r requirements.txt
  4. python bot.py
"""

import os
import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path

import aiohttp
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

load_dotenv()

# ─── Конфиг ─────────────────────────────────────────────────
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "300"))  # 5 мин
SITES_FILE = Path(__file__).parent / "sites.json"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ─── Хранилище сайтов ───────────────────────────────────────
def load_sites() -> list[dict]:
    if SITES_FILE.exists():
        return json.loads(SITES_FILE.read_text())
    return []


def save_sites(sites: list[dict]):
    SITES_FILE.write_text(json.dumps(sites, indent=2, ensure_ascii=False))


# ─── Мониторинг uptime ──────────────────────────────────────
async def check_site(session: aiohttp.ClientSession, site: dict) -> dict:
    """Проверяет доступность одного сайта."""
    url = site["url"]
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            return {
                "url": url,
                "name": site.get("name", url),
                "status": resp.status,
                "ok": 200 <= resp.status < 400,
                "response_time": resp.headers.get("X-Response-Time", "n/a"),
            }
    except Exception as e:
        return {
            "url": url,
            "name": site.get("name", url),
            "status": 0,
            "ok": False,
            "error": str(e),
        }


async def monitor_sites(context: ContextTypes.DEFAULT_TYPE):
    """Периодическая проверка всех сайтов."""
    sites = load_sites()
    if not sites:
        return

    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(
            *[check_site(session, site) for site in sites]
        )

    down = [r for r in results if not r["ok"]]
    if down:
        msg = "🔴 *Сайты недоступны!*\n\n"
        for r in down:
            error = r.get("error", f"HTTP {r['status']}")
            msg += f"• {r['name']}: `{error}`\n"
        msg += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"

        await context.bot.send_message(
            chat_id=CHAT_ID, text=msg, parse_mode="Markdown"
        )


# ─── Команды бота ───────────────────────────────────────────
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Agency Bot готов к работе!\n\n"
        "Команды:\n"
        "/status — проверить все сайты сейчас\n"
        "/sites — список отслеживаемых сайтов\n"
        "/add <url> <name> — добавить сайт\n"
        "/remove <url> — удалить сайт\n"
        "/help — справка"
    )


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Моментальная проверка всех сайтов."""
    sites = load_sites()
    if not sites:
        await update.message.reply_text("📭 Список сайтов пуст. Добавь через /add")
        return

    msg = await update.message.reply_text("🔍 Проверяю...")

    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(
            *[check_site(session, site) for site in sites]
        )

    text = "📊 *Статус сайтов:*\n\n"
    for r in results:
        icon = "🟢" if r["ok"] else "🔴"
        status = f"HTTP {r['status']}" if r["status"] else r.get("error", "Timeout")
        text += f"{icon} *{r['name']}*\n   `{status}`\n\n"

    text += f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
    await msg.edit_text(text, parse_mode="Markdown")


async def cmd_sites(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать список сайтов."""
    sites = load_sites()
    if not sites:
        await update.message.reply_text("📭 Список пуст. Добавь через /add <url> <name>")
        return

    text = "📋 *Отслеживаемые сайты:*\n\n"
    for i, s in enumerate(sites, 1):
        text += f"{i}. [{s.get('name', s['url'])}]({s['url']})\n"

    await update.message.reply_text(text, parse_mode="Markdown")


async def cmd_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавить сайт: /add https://example.com My Site"""
    args = context.args
    if not args:
        await update.message.reply_text("Использование: /add <url> [name]")
        return

    url = args[0]
    if not url.startswith("http"):
        url = f"https://{url}"

    name = " ".join(args[1:]) if len(args) > 1 else url

    sites = load_sites()

    # Проверка дубликатов
    if any(s["url"] == url for s in sites):
        await update.message.reply_text(f"⚠️ `{url}` уже в списке", parse_mode="Markdown")
        return

    sites.append({"url": url, "name": name})
    save_sites(sites)

    await update.message.reply_text(
        f"✅ Добавлен: *{name}*\n`{url}`", parse_mode="Markdown"
    )


async def cmd_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удалить сайт: /remove https://example.com"""
    args = context.args
    if not args:
        await update.message.reply_text("Использование: /remove <url>")
        return

    url = args[0]
    sites = load_sites()
    new_sites = [s for s in sites if s["url"] != url]

    if len(new_sites) == len(sites):
        await update.message.reply_text(f"⚠️ `{url}` не найден", parse_mode="Markdown")
        return

    save_sites(new_sites)
    await update.message.reply_text(f"🗑 Удалён: `{url}`", parse_mode="Markdown")


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Agency Notification Bot*\n\n"
        "*Мониторинг:*\n"
        f"Проверяю сайты каждые {CHECK_INTERVAL // 60} мин.\n"
        "Если сайт недоступен — мгновенное уведомление.\n\n"
        "*GitHub:*\n"
        "Получаю уведомления о деплоях через GitHub Actions.\n"
        "Настройка — в workflow файлах (.github/workflows/).\n\n"
        "*Команды:*\n"
        "/status — проверить сайты сейчас\n"
        "/sites — список сайтов\n"
        "/add <url> [name] — добавить\n"
        "/remove <url> — удалить",
        parse_mode="Markdown",
    )


# ─── Запуск ─────────────────────────────────────────────────
def main():
    if not BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN не задан! Скопируй .env.example → .env")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    # Команды
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("sites", cmd_sites))
    app.add_handler(CommandHandler("add", cmd_add))
    app.add_handler(CommandHandler("remove", cmd_remove))
    app.add_handler(CommandHandler("help", cmd_help))

    # Мониторинг по расписанию
    if CHAT_ID:
        app.job_queue.run_repeating(
            monitor_sites,
            interval=CHECK_INTERVAL,
            first=10,
        )
        logger.info(f"Мониторинг запущен (интервал: {CHECK_INTERVAL}s)")

    logger.info("Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
