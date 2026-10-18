from pyrogram import filters

@app.on_message(filters.command(["broadcast", "gcast"]) & filters.user(OWNER_ID))
async def simple_broadcast(client, message):
    # Check karein ki message ke sath text diya hai ya nahi
    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text("Kripya broadcast karne ke liye kuch text likhein ya kisi message ko reply karein!")
    
    # Agar kisi message ko reply kiya hai toh use lo, nahi toh text lo
    broadcast_msg = message.reply_to_message if message.reply_to_message else message
    
    sent = 0
    failed = 0
    
    # Aapke bot ke pas jitne bhi chats/users ki list hai (yahan apni database list dalein)
    # Example ke taur par, agar aapke paas chat IDs ki list hai:
    # chats = [123456789, 987654321] 
    
    await message.reply_text("Broadcast shuru ho gaya hai...")
    
    # for chat_id in chats:
    #     try:
    #         await broadcast_msg.copy(chat_id)
    #         sent += 1
    #     except Exception:
    #         failed += 1
            
    await message.reply_text(f"Broadcast poora ho gaya!\nSafar: {sent}\nFailed: {failed}")
    
