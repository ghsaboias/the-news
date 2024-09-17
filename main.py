from openai import OpenAI
from crawl4ai import WebCrawler
import requests
import os
from groq import Groq
import time
# from twilio.rest import Client
from brave import Brave
from datetime import datetime

# twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
llm_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
brave = Brave(api_key=os.getenv("BRAVE_API_KEY"))
telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
crawler = WebCrawler()

crawler.warmup()

REGION_TOPICS = {
    "middle east": [
        "Saudi Arabia", "United Arab Emirates", "Israel", "Iran",
        "Iraq", "Jordan", "Lebanon", "Syria", "Turkey", "Yemen",
        "Oman", "Kuwait", "Bahrain", "Qatar"
    ],
    "europe": [
        "Germany", "France", "United Kingdom", "Italy", "Spain",
        "Poland", "Netherlands", "Sweden", "Norway", "Switzerland",
        "Belgium", "Austria", "Denmark", "Finland", "Ireland"
    ],
}


def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage"
    payload = {
        "chat_id": telegram_chat_id,
        "text": message
    }
    try:
        print(f"Sending message to Telegram: {message}")
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

# def send_whatsapp_message(message: str):
#     try:
#         twilio_client.messages.create(
#             from_='whatsapp:+14155238886',
#             body=message,
#             to='whatsapp:+5511992745950'
#         )
#     except Exception as e:
#         print(f"Error sending WhatsApp message: {e}")

def ask_llm(results):
    response = llm_client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
            {"role": "system", "content": """
            You are a precise and efficient news summarizer. Given a list of news results, create a concise summary.

            Guidelines:
            - Focus on hard data, facts, and objective information.
            - Maintain neutrality; avoid bias, opinions, or editorializing.
            - Be concise and direct; omit unnecessary details or repetition.
            - Do not include stock recommendations unless directly related to major news.
            - Avoid generalized disclaimers or evasive language.
            - Do not include double asterisks or single asterisks in the summary.
            - Include most important URLs in the summary.
            - Do NOT include "Here's a summary of the news" or similar introductory phrases.
            """},
            {"role": "user", "content": f"Results:\n{results}\n\n."},
        ],
        max_tokens=8000
    )
    return response.choices[0].message.content

def search_brave_news(topic):
    results = []
    try:
        params = {
            "q": topic,
            "count": 3,
            "country": "all",
            "search_lang": "en",
            "spellcheck": 1,
            "extra_snippets": True,
            "freshness": "pd"
        }
        headers = {
            "Accept": "application/json",
                "Accept-Encoding": "gzip",
            "X-Subscription-Token": os.getenv("BRAVE_API_KEY")
            }
        response = requests.get("https://api.search.brave.com/res/v1/news/search", headers=headers, params=params)
        brave_results = response.json()
        if 'results' in brave_results:
            for result in brave_results["results"]:
                formatted_result = f"{result['page_age']} - {topic} - {result['title']} - {result['description']}"
                if "extra_snippets" in result:
                    for snippet in result["extra_snippets"]:
                        formatted_result += f"{snippet}\n"
                formatted_result += f"URL: {result['url']}\n\n"
                results.append(formatted_result)
                with open("results.txt", "a") as f:
                    f.write(formatted_result)
                print(f"Saved {formatted_result}")
                time.sleep(1)
        else:
            print(f"No results found for topic: {topic}")
        return results
    except Exception as e:
        print(f"Error searching Brave News: {e}")

def handle_incoming_messages():
    url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/getUpdates"
    last_update_id = None
    while True:
        try:
            params = {'timeout': 100, 'offset': last_update_id}
            response = requests.get(url, params=params)
            updates = response.json().get('result', [])
            for update in updates:
                last_update_id = update['update_id'] + 1
                message = update.get('message', {}).get('text', '')
                if message:
                    print(f"Received message: {message}")
                    summary = process_topic(message)
                    send_telegram_message(summary, telegram_chat_id)
            time.sleep(1)
        except Exception as e:
            print(f"Error handling incoming messages: {e}")

def process_topic(topic):
    if isinstance(topic, list):
        results = search_brave_news(topic)
    else:
        lower_topic = topic.lower()
        if lower_topic in REGION_TOPICS:
            topics = REGION_TOPICS[lower_topic]
        else:
            topics = [topic]
        results = search_brave_news(topics)
    summary = ask_llm(results)
    return summary

def send_telegram_message(message: str, chat_id: int):
    url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    try:
        print(f"Sending message to Telegram: {message}")
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

def main():
    with open("results.txt", "w") as f:
        f.write("")
    handle_incoming_messages()

if __name__ == "__main__":
    main()