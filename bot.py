import os
import requests
import time
import logging
from telegram import Bot

API_KEY = os.getenv("API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

def get_live_matches():
    url = "https://v3.football.api-sports.io/fixtures?live=all"
    headers = {
        "x-apisports-key": API_KEY
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("response", [])
    return []

def analyze_match(match):
    stats = match.get("statistics")
    if not stats:
        return None

    team1 = match["teams"]["home"]["name"]
    team2 = match["teams"]["away"]["name"]
    shots = stats

    home_shots = shots[0]["statistics"]
    away_shots = shots[1]["statistics"]

    total_shots = 0
    for stat in home_shots + away_shots:
        if stat["type"] == "Shots on Goal" and stat["value"]:
            total_shots += stat["value"]

    if total_shots >= 15:
        return f"{team1} vs {team2} - Возможен гол! Удары в створ: {total_shots}"
    
    return None

def main():
    sent_matches = set()
    while True:
        matches = get_live_matches()
        for match in matches:
            match_id = match["fixture"]["id"]
            if match_id in sent_matches:
                continue
            alert = analyze_match(match)
            if alert:
                bot.send_message(chat_id="@Footballyegobot", text=alert)
                sent_matches.add(match_id)
        time.sleep(60)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
