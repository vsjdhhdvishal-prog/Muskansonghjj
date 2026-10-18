from pyrogram import filters
from bot import app  # Aapke bot ke instance ke anusaar import change ho sakta hai

@app.on_message(filters.command(["broadcast", "gcast"]))
async def broadcast_message(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Kripya broadcast karne ke liye message dein.")
    
    query = message.text.split(None, 1)[1]
    # Yahan aap apna broadcast/promotion ka logic likh sakte hain
    await message.reply_text("Broadcast code yahan execute hoga.")
  
