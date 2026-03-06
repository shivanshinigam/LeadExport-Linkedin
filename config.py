import os
import sys
from dotenv import load_dotenv

load_dotenv()

ANYMAIL_API_KEY = os.getenv("ANYMAIL_API_KEY", "")
ANYMAIL_BASE_URL = "https://api.anymailfinder.com/v5.1"

ENDPOINTS = {
    "person": f"{ANYMAIL_BASE_URL}/find-email/person",
    "decision_maker": f"{ANYMAIL_BASE_URL}/find-email/decision-maker",
    "company": f"{ANYMAIL_BASE_URL}/find-email/company",
    "linkedin_url": f"{ANYMAIL_BASE_URL}/find-email/linkedin-url",
}

REQUEST_TIMEOUT = 180
MAX_RETRIES = 2
RETRY_DELAY = 5


def validate_api_key():
    if not ANYMAIL_API_KEY or ANYMAIL_API_KEY == "your_api_key_here":
        print("\n╔══════════════════════════════════════════════════════════╗")
        print("║  ANYMAIL_API_KEY is not configured!                   ║")
        print("║                                                          ║")
        print("║  Steps to fix:                                           ║")
        print("║  1. Copy .env.example to .env                            ║")
        print("║  2. Get your API key from:                               ║")
        print("║     https://newapp.anymailfinder.com/settings/api        ║")
        print("║  3. Paste it in .env as ANYMAIL_API_KEY=your_key         ║")
        print("╚══════════════════════════════════════════════════════════╝\n")
        sys.exit(1)
