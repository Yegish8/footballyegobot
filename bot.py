import os
import requests
import time
import logging
from telegram import Bot, error

API_KEY = os.getenv("API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

#   Настройки
CHAT_ID = 5050917770               # Твой Telegram ID
TOTAL_THRESHOLD = 2.5             # Уведомление, если total <= этого значения
MINUTE_TRIGGER = 60               # Минут с начала матча, после которых начинаем следить
ONLY_NO_GOALS = False             # Если True — сработает только при счёте 0:0
CHECK_INTERVAL = 60               # Интервал проверки (в секундах)

def get_live_matches():
    url = "https://v3.football.api-sports.io/fixtures?live=all"
    headers = {
        "x-apisports-key": API_KEY
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get("response", [])
        else:
            logging.error(f"API error: {response.status_code}")
    except requests.RequestException as e:
        logging.error(f"Connection error: {e}")
    return []

def analyze_match(match):
    fixture = match["fixture"]
    league = match["league"]
    teams = match["teams"]
    goals = match["goals"]

    minute = fixture["status"]["elapsed"]
    if not minute or minute < MINUTE_TRIGGER:
        return None

    home = teams["home"]["name"]
    away = teams["away"]["name"]
    home_goals = goals["home"]
    away_goals = goals["away"]
    total_goals = (home_goals or 0) + (away_goals or 0)

    if ONLY_NO_GOALS and total_goals > 0:
        return None

    if total_goals <= TOTAL_THRESHOLD:
        return f"⚽ {home} vs {away}\n  {league['country']} | {league['name']}\n⏱ {minute} минута\nСчёт: {home_goals} - {away_goals}\n❗ Возможно скоро будет гол!"

    return None

def main():
    logging.basicConfig(level=logging.INFO)
    sent_matches = set()

    while True:
        matches = get_live_matches()
        for match in matches:
            match_id = match["fixture"]["id"]
            if match_id in sent_matches:
                continue

            alert = analyze_match(match)
            if alert:
                try:
                    bot.send_message(chat_id=CHAT_ID, text=alert)
                    sent_matches.add(match_id)
                    logging.info(f"  Отправлено: {alert}")
                except error.TelegramError as e:
                    logging.error(f"Telegram error: {e}")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
