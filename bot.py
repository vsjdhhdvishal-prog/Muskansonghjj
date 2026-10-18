import os
import time
import asyncio
from aiohttp import web
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

app = Client(
    "SimpleBot",
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
        return await message.reply_text("Kripya promotion message dein! Jaise:\n`/promotion Hello everyone`")
    
    query = message.text.split(None, 1)[1]
    status_msg = await message.reply_text("⏳ Promotion shuru ho raha hai...")
    
    sent = 0
    failed = 0
    
    async for dialog in client.get_dialogs():
        chat_id = dialog.chat.id
        if chat_id != message.chat.id:
            try:
                await client.send_message(chat_id, query)
                sent += 1
                await asyncio.sleep(0.4)
            except Exception:
                failed += 1

    await status_msg.edit_text(f"✅ **Promotion Complete!**\n\n- Successful: `{sent}` chats\n- Failed: `{failed}` chats")

# Render ke port error ko khatam karne ke liye dummy web server
async def handle(request):
    return web.Response(text="Bot is running smoothly!")

async def web_server():
    web_app = web.Application()
    web_app.add_routes([web.get("/", handle)])
    runner = web.AppRunner(web_app)
    await runner.setup()
    port = int(os.getenv("PORT", "8080"))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    await web_server()
    await app.start()
    print("Bot & Web Server Successfully Started!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
    
