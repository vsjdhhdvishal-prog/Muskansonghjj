# =====================================================================
# FILE: config.py
# =====================================================================

import os
import sys
import logging
from typing import Final, Dict, List

BOT_VERSION: Final[str] = "30.0.0-CleanEnterprise"
DEFAULT_PORT: Final[int] = 10000
DATABASE_FILENAME: Final[str] = "enterprise_bot_database.sqlite"

BOT_TOKEN: Final[str] = os.environ.get("BOT_TOKEN", "")

try:
    OWNER_ID: Final[int] = int(os.environ.get("OWNER_ID", "123456789"))
except ValueError:
    OWNER_ID = 123456789

logging.basicConfig(
    format="%(asctime)s | LEVEL: %(levelname)-8s | MODULE: %(name)s | LINE: %(lineno)d - %(message)s",
    level=logging.INFO
)
LOGGER = logging.getLogger("CleanEnterpriseBot")

# Group tag/mention replies ke liye knowledge base
GROUP_KNOWLEDGE_BASE: Final[Dict[str, List[str]]] = {
    "interview_location": [
        "Main Indore se hoon! Madhya Pradesh ka sabse pyaara aur cleanest shehar. ✨",
        "Home town Indore hai mera, wahin rehti hoon."
    ],
    "interview_study": [
        "Meri 12th standard ki padhai poori ho chuki hai, aur abhi main school regular jaati hoon. 📚",
        "Main 12th me hu aur roz school jati hu!"
    ],
    "attitude": [
        "Hum wahi hain jo kal the, bas ab logo ko faltu bhav dena band kar diya hai. 😎",
        "Attitude humare khoon me hai!"
    ],
    "flirt": [
        "Aapki baatein sunke lagta hai ki aapko impress karne ke liye mujhe special class leni padegi. 😉",
        "Itni pyaari baatein karoge toh dil aa jayega kisi pe! ❤️"
    ],
    "default_pool": [
        "Aapne yaad kiya aur hum hazir hain! Bataiye kya kaam hai? 😊",
        "Sahi hai! Aise hi baatein karte raho."
    ]
}

def validate_system_config() -> bool:
    if not BOT_TOKEN:
        LOGGER.critical("CRITICAL ERROR: BOT_TOKEN environment variable is missing!")
        return False
    LOGGER.info(f"Configuration successfully validated for Owner ID: {OWNER_ID}")
    return True
    
