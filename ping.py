import time
from pyrogram import filters
from pyrogram.types import Message
from anony import app
from anony.core.bot import app as bot_client

@app.on_message(filters.command(["ping"]))
async def ping_cb(client, message: Message):
    start = time.time()
    current_time = time.strftime("%H:%M:%S", time.gmtime(time.time()))
    
    rep = await message.reply_text("🏓 **Pinging...**")
    delta = time.time() - start
    
    await rep.edit_text(
        f"🏓 **Pong!**\n"
        f"⚡ `{delta * 1000:.3f} ms`\n\n"
        f"🤖 **Bot:** Online\n"
        f"⏰ **Time:** `{current_time}`"
    )
  
