import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

app = Client("SimpleBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("ping"))
async def ping_cmd(client, message: Message):
    start = time.time()
    rep = await message.reply_text("🏓 Pinging...")
    delta = time.time() - start
    await rep.edit_text(f"🏓 Pong!\n⚡ `{delta * 1000:.3f} ms`")

@app.on_message(filters.command(["broadcast", "promotion"]) & filters.user(OWNER_ID))
async def broadcast_cmd(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Kripya message dein!")
    
    query = message.text.split(None, 1)[1]
    m = await message.reply_text("⏳ Broadcast shuru ho raha hai...")
    
    sent = 0
    # Yahan aap apne chats/users loop kar sakte hain
    await m.edit_text(f"✅ Broadcast command received: {query}")

print("Bot Starting...")
app.run()
