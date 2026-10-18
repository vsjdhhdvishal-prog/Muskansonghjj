# =====================================================================
# FILE 5 OF 5: bot.py (Updated)
# Purpose: Main Enterprise Bot Orchestrator and Polling Runner
# =====================================================================

import sys
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ChatMemberHandler,
    CommandHandler,
    MessageHandler,
    filters
)
from config import BOT_TOKEN, LOGGER, validate_system_config, BOT_VERSION
from server import WEB_SERVER
from handlers import EnterpriseBotHandlers

class EnterpriseTelegramBotLauncher:
    """Orchestrates the entire enterprise bot ecosystem, servers, and handlers."""

    def __init__(self) -> None:
        self.application = None

    def build_application(self) -> None:
        """Builds and configures the Telegram Bot application instance."""
        LOGGER.info(f"Building Telegram application v{BOT_VERSION}...")
        
        if not validate_system_config():
            LOGGER.critical("System configuration validation failed. Aborting startup.")
            sys.exit(1)

        try:
            self.application = ApplicationBuilder().token(BOT_TOKEN).build()
            self._register_handlers()
            LOGGER.info("Telegram application built and configured successfully.")
        except Exception as exc:
            LOGGER.critical(f"Failed to build Telegram application: {exc}")
            sys.exit(1)

    def _register_handlers(self) -> None:
        """Registers all event handlers and command routers into the application."""
        LOGGER.info("Registering enterprise event handlers...")

        self.application.add_handler(
            ChatMemberHandler(
                EnterpriseBotHandlers.track_chats_handler,
                ChatMemberHandler.MY_CHAT_MEMBER
            )
        )

        self.application.add_handler(
            CommandHandler("promotion", EnterpriseBotHandlers.promotion_command_handler)
        )

        self.application.add_handler(
            MessageHandler(
                filters.ChatType.GROUPS & (~filters.COMMAND),
                EnterpriseBotHandlers.auto_save_on_group_message
            )
        )

        self.application.add_handler(
            MessageHandler(
                filters.TEXT & (~filters.COMMAND) & filters.ChatType.PRIVATE,
                EnterpriseBotHandlers.interview_auto_reply_handler
            )
        )

        LOGGER.info("All enterprise handlers registered successfully.")

    def run(self) -> None:
        """Starts the uptime web server and runs the Telegram bot polling engine."""
        LOGGER.info("Initializing enterprise bot startup sequence...")

        WEB_SERVER.start_background_thread()
        self.build_application()

        LOGGER.info("Starting Telegram bot long-polling engine... Bot is now live!")
        try:
            self.application.run_polling(allowed_updates=Update.ALL_TYPES)
        except Exception as exc:
            LOGGER.critical(f"Polling crashed due to unexpected error: {exc}")
            sys.exit(1)

if __name__ == "__main__":
    print(f"""
    ========================================================
       STARTING TELEGRAM ENTERPRISE BOT (v{BOT_VERSION})
       - Architecture: 5 Modular Python Files
       - Features: Secure Promotion, Interview AI, 24/7 Uptime
    ========================================================
    """)
    
    launcher = EnterpriseTelegramBotLauncher()
    launcher.run()
    
