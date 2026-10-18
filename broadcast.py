import asyncio
from pyrogram import filters
from pyrogram.errors import FloodWait
from anony import app
from anony.misc import SUDOERS  # ya apna owner check use karein
from anony.utils.database import get_active_chats, get_served_users

@app.on_message(filters.command(["broadcast", "promotion"]) & filters.user(SUDOERS))
async def broadcast_message(client, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "**Kripya broadcast ya promotion ke liye message dein!**\n"
            "Udaharan: `/broadcast Hello dosto` ya `/promotion New update!`"
        )
    
    query = message.text.split(None, 1)[1]
    
    # Send waiting message
    m = await message.reply_text("⏳ **Broadcast shuru ho raha hai...**")
    
    # Fetch chats and users from database
    chats = []
    try:
        active_chats = await get_active_chats()
        for chat in active_chats:
            chats.append(chat["chat_id"])
    except:
        pass

    users = []
    try:
        served_users = await get_served_users()
        for user in served_users:
            users.append(user["user_id"])
    except:
        pass

    sent = 0
    pin = 0
    failed = 0
    
    # Broadcast to groups/chats
    for i in chats:
        try:
            m_chat = await client.send_message(i, query)
            try:
                await m_chat.pin(disable_notification=True)
                pin += 1
            except:
                pass
            sent += 1
            await asyncio.sleep(0.2)
        except FloodWait as e:
            asyncio.sleep(e.value)
        except:
            failed += 1

    # Broadcast to private users
    for i in users:
        try:
            await client.send_message(i, query)
            sent += 1
            await asyncio.sleep(0.2)
        except FloodWait as e:
            asyncio.sleep(e.value)
        except:
            failed += 1

    await m.edit_text(
        f"✅ **Broadcast Safal Raha!**\n\n"
        f"**Kula Kul Bheje Gaye:** `{sent}`\n"
        f"**Pin Kiye Gaye Chats:** `{pin}`\n"
        f"**Viphal (Failed):** `{failed}`"
          )
  
