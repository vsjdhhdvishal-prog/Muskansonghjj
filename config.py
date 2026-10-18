# =====================================================================
# FILE 1 OF 5: config.py
# Purpose: Configuration, Logging, and Security Parameters
# Lines: ~300
# =====================================================================

import os
import sys
import logging
from typing import Final, Dict, Any, List

# ---------------------------------------------------------------------
# 1. System Constants & Environment Variables
# ---------------------------------------------------------------------
BOT_VERSION: Final[str] = "3.5.0-Enterprise"
DEFAULT_PORT: Final[int] = 10000
DATABASE_FILENAME: Final[str] = "enterprise_bot_database.sqlite"

# Retrieve Telegram Bot Token from Environment Variables
BOT_TOKEN: Final[str] = os.environ.get("BOT_TOKEN", "")

# Retrieve Owner ID (Replace with your actual Telegram User ID)
try:
    OWNER_ID: Final[int] = int(os.environ.get("OWNER_ID", "123456789"))
except ValueError:
    OWNER_ID = 123456789

# ---------------------------------------------------------------------
# 2. Advanced Logging System Configuration
# ---------------------------------------------------------------------
LOG_FORMAT: Final[str] = (
    "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
)
LOG_FILE: Final[str] = "bot_runtime_activity.log"

def setup_enterprise_logging() -> logging.Logger:
    """Initializes professional multi-channel logging for enterprise tracking."""
    logger = logging.getLogger("EnterpriseBot")
    logger.setLevel(logging.DEBUG)

    # Prevent duplicate handlers if re-initialized
    if logger.hasHandlers():
        logger.handlers.clear()

    # Console Handler (Stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File Handler for permanent record
    try:
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(LOG_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as exc:
        print(f"Warning: Could not initialize file logger: {exc}")

    logger.info("Enterprise logging system successfully initialized.")
    return logger

LOGGER = setup_enterprise_logging()

# ---------------------------------------------------------------------
# 3. Interview Persona & Knowledge Base Dictionary
# ---------------------------------------------------------------------
INTERVIEW_KNOWLEDGE_BASE: Final[Dict[str, List[str]]] = {
    "location": [
        "Main Indore se hoon! Madhya Pradesh ka sabse pyara shehar. ✨",
        "Hum Indore me rehte hain, cleanest city of India! 🏙️"
    ],
    "education": [
        "Meri 12th standard ki padhai poori ho chuki hai, aur abhi main school jaati hoon. 📚",
        "Main 12th pass out hoon aur regular school continue kar rahi hoon."
    ],
    "identity": [
        "Main ek advanced automated personal assistant bot hoon jo aapke sabhi sawaalon ke jawab de sakta hai.",
        "Aap mujhse kisi bhi tarah ka interview sawal pooch sakte hain!"
    ],
    "greetings": [
        "Hello! Aap kaise hain? Aaj main aapki kya sahayta kar sakti hoon? 😊",
        "Hi there! Ummeed hai aapka din accha chal raha hoga."
    ],
    "default": [
        "Aapke message ke liye bahut shukriya! Main is par vichar kar rahi hoon.",
        "Yeh ek interesting sawal hai! Kripya thoda aur vistaar se batayein.",
        "Main abhi busy hoon, lekin aapka message mujhe mil gaya hai!"
    ]
}

# ---------------------------------------------------------------------
# 4. System Validation Check
# ---------------------------------------------------------------------
def validate_system_config() -> bool:
    """Validates if essential credentials are provided before startup."""
    LOGGER.info("Validating enterprise configuration parameters...")
    if not BOT_TOKEN:
        LOGGER.critical("CRITICAL ERROR: BOT_TOKEN environment variable is missing!")
        return False
    LOGGER.info(f"Configuration validated successfully for Owner ID: {OWNER_ID}")
    return True

if __name__ == "__main__":
    LOGGER.info("Config module executed directly.")
  
