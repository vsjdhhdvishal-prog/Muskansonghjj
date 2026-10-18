import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

app = Client(
    "TelegramBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@app.on_message(filters.command("ping"))
async def ping_cmd(client, message: Message):
    start = time.time()
    rep = await message.reply_text("🏓 Pinging...")
    delta = time.time() - start
    await rep.edit_text(f"🏓 Pong!\n⚡ `{delta * 1000:.3f} ms`")

@app.on_message(filters.command(["broadcast", "promotion"]) & filters.user(OWNER_ID))
async def promotion_cmd(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Kripya promotion message dein! Jaise: `/promotion Hello`")
    
    query = message.text.split(None, 1)[1]
    m = await message.reply_text("⏳ Promotion shuru ho raha hai...")
    
    sent = 0
    failed = 0
    async for dialog in client.get_dialogs():
        if dialog.chat.id != message.chat.id:
            try:
                await client.send_message(dialog.chat.id, query)
                sent += 1
            except Exception:
                failed += 1

    await m.edit_text(f"✅ **Promotion Complete!**\n- Sent: `{sent}`\n- Failed: `{failed}`")

if __name__ == "__main__":
    print("Bot is starting...")
    app.run()
    
