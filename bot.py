import os
import asyncio
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# ====== НАСТРОЙКИ ======
BOT_TOKEN = os.getenv("8392132981:AAHpxCwk2GbqQvEb3c9mBWX6YrLSqccEGMs")
CHAT_ID = os.getenv("1895264689")
FORTNITE_URL = "https://fortnitedb.com/pve/alerts"
# =======================

bot = Bot(token=8392132981:AAHpxCwk2GbqQvEb3c9mBWX6YrLSqccEGMs)
dp = Dispatcher(bot)

def get_alerts():
    """Парсит алерты Fortnite PvE с сайта FortniteDB"""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(FORTNITE_URL, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "lxml")

        alerts = []
        cards = soup.select(".pve-alert-card, .card, .mission")
        for c in cards:
            title = (c.select_one(".mission-name") or c.select_one("h3"))
            reward = (c.select_one(".reward-name") or c.select_one(".reward"))
            region = (c.select_one(".region-name") or c.select_one(".region"))
            title = title.text.strip() if title else "—"
            reward = reward.text.strip() if reward else "—"
            region = region.text.strip() if region else "—"
            alerts.append(f"🗺 {region}\n🎯 {title}\n💎 {reward}\n")
        if not alerts:
            return "⚠️ Не удалось найти данные, возможно сайт обновляется."
        return "📢 Ежедневные алерты Fortnite PvE:\n\n" + "\n".join(alerts[:20])
    except Exception as e:
        return f"Ошибка: {e}"

async def send_alerts():
    text = await asyncio.get_event_loop().run_in_executor(None, get_alerts)
    await bot.send_message(CHAT_ID, text)

async def scheduler():
    """Запускает отправку каждый день в 3:00 по Москве (00:00 UTC)"""
    while True:
        now = datetime.utcnow()
        if now.hour == 0 and now.minute == 0:
            await send_alerts()
            await asyncio.sleep(3600)
        await asyncio.sleep(60)

@dp.message_handler(commands=["start"])
async def start_cmd(msg: types.Message):
    await msg.answer("✅ Бот активен! Я буду присылать Fortnite PvE алерты каждый день в 3:00 по МСК.")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(scheduler())
    executor.start_polling(dp, skip_updates=True)
