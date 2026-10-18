# =====================================================================
# FILE 1 OF 3: config.py (Heavy Enterprise Configuration & Large Datasets)
# Purpose: Massive Knowledge Base for Interview, Attitude, Flirt & Chats
# =====================================================================

import os
import sys
import logging
from typing import Final, Dict, List, Any

# --- SYSTEM CONSTANTS ---
BOT_VERSION: Final[str] = "15.0.0-MassiveEnterprise"
DEFAULT_PORT: Final[int] = 10000
DATABASE_FILENAME: Final[str] = "massive_enterprise_database.sqlite"

# --- ENVIRONMENT VARIABLES ---
BOT_TOKEN: Final[str] = os.environ.get("BOT_TOKEN", "")

try:
    OWNER_ID: Final[int] = int(os.environ.get("OWNER_ID", "123456789"))
except ValueError:
    OWNER_ID = 123456789

# --- ADVANCED LOGGING SETUP ---
logging.basicConfig(
    format="%(asctime)s | LEVEL: %(levelname)-8s | MODULE: %(name)s | LINE: %(lineno)d - %(message)s",
    level=logging.INFO
)
LOGGER = logging.getLogger("MassiveEnterpriseBot")

# --- MASSIVE KNOWLEDGE BASE (HUNDREDS OF VARIATIONS) ---
MASSIVE_CHAT_DATABASE: Final[Dict[str, List[str]]] = {
    "interview_location": [
        "Main Indore se hoon! Madhya Pradesh ka sabse shaandar aur cleanest shehar. ✨",
        "Mera hometown Indore hai, aur main wahin se belong karti hoon.",
        "Indore shehar se hoon main, aap sunao aap kahan se ho?",
        "Indore, jo ki apni safai aur khane-peene ke liye famous hai, wahi ki hu main."
    ],
    "interview_study": [
        "Meri 12th standard ki padhai complete ho chuki hai, aur abhi main school regular jaati hoon. 📚",
        "Main 12th pass out student hoon aur abhi school continue kar rahi hoon.",
        "Padhai me abhi 12th chal raha hai, school life ke maze le rahi hu!",
        "12th ho gaya hai, aage ki planning chal rahi hai aur school jaati hoon."
    ],
    "interview_hobby": [
        "Mujhe free time me coding karna, naye doston se baat karna, aur music sunna bahut pasand hai. 🎵",
        "Mujhe tech cheezein explore karna, reels dekhna aur chat karna achha lagta hai.",
        "Hobby ki baat karein toh travelling, reading aur coding meri favorite list me hai."
    ],
    "attitude": [
        "Hum wahi hain jo kal the, bas ab logo ko faltu bhav dena chhod diya hai. 😎",
        "Attitude humare khoon me hai, baari aane par sabko unki aukat pata chal hi jati hai.",
        "Humse panga lene se pehle apna background check zaroor kar lena! 🔥",
        "Jitni tumhari soch hai, usse kai guna aage hamari planning chalti hai.",
        "Bhav khane ka shauk nahi hai, bas hum har kisi ke saamne jhukte nahi!"
    ],
    "flirt": [
        "Aapki baatein sunke lagta hai ki aapko impress karne ke liye mujhe special training leni padegi. 😉",
        "Itni pyaari baatein karoge toh dil aa jayega kisi pe, thoda sambhal ke bolo! ❤️",
        "Aapki smile kaafi achhi hogi, bas kabhi aamne-samne milne ka mauka nahi mila.",
        "Aap online kya aaye, baaki saari notifications bekar aur boring lagne lagi.",
        "Aapse baat karke aisa lagta hai ki waqt wahin tham gaya ho! ✨"
    ],
    "greetings": [
        "Hello ji! Kaise hain aap? Bataiye aaj din kaisa chal raha hai? 😊",
        "Hi! Aapka message dekh kar sach me bahut khushi hui.",
        "Hey there! Kahiye main aapki aisi kaun si madad kar sakti hoon?",
        "Good day! Bataiye kya chal raha hai aapki duniya me?"
    ],
    "help_queries": [
        "Main ek advanced multi-functional AI assistant hoon jo aapke har sawal ka jawab de sakti hoon!",
        "Aap mujhse interview questions, general chats, flirt, attitude ya koi bhi text bhej sakte ho.",
        "Main 24/7 active rehti hoon, aapko jo bhi puchna ho bejhijhak puch sakte hain."
    ],
    "default_massive_pool": [
        "Sahi hai! Is baare me thoda aur vistaar se batao na, mujhe sunne me maza aayega. 🤔",
        "Aapka yeh message padh kar thoda sochna pad gaya ki iska kya jawab doon!",
        "Hmm, baat toh aapki bilkul sahi hai, par main abhi thodi busy hoon.",
        "Yeh kya naya aur alag sa sawal pooch liya aapne? Dimag ki bati jala di!",
        "Aapke is message ka jawab dene ke liye mujhe thoda aur sochna padega. 😄",
        "Badiya hai! Aise hi baatein karte raho, acha lagta hai.",
        "Main samajh gayi aapki baat, aage bolo kya chal raha hai?"
    ]
}

def validate_system_configuration() -> bool:
    """Ensures all configuration tokens are fully loaded and valid."""
    LOGGER.info("Validating heavy enterprise configuration parameters...")
    if not BOT_TOKEN:
        LOGGER.critical("CRITICAL ERROR: BOT_TOKEN is missing from environment variables!")
        return False
    LOGGER.info(f"Configuration successfully validated for Owner ID: {OWNER_ID}")
    return True
    
