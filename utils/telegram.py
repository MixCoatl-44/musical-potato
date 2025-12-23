import os
import requests

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_message(text: str) -> None:
    """
    Send a simple text message to Telegram.
    Expects TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in environment.
    """
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram not configured (missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID).")
        print("Message that would have been sent:\n", text)
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    try:
        resp = requests.post(url, data=payload, timeout=10)
        if not resp.ok:
            print("Telegram error:", resp.status_code, resp.text)
    except Exception as e:
        print("Telegram exception:", e)
