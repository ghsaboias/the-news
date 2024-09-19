from openai import OpenAI
from crawl4ai import WebCrawler
import requests
import os
from groq import Groq
import time
from brave import Brave
from datetime import datetime
import base64
import json

llm_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
brave = Brave(api_key=os.getenv("BRAVE_API_KEY"))
telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
crawler = WebCrawler()

crawler.warmup()

def get_screenshot(urls):
    for url in urls:
        result = crawler.run(url=url, screenshot=True)

        with open(f"{url.split('/')[-1]}.png", "wb") as f:
            print(result)
            f.write(base64.b64decode(result.screenshot))

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

def ask_llm(results):
    try:
        response = llm_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": """
                You are a precise and efficient news summarizer. Given a list of news results, create a concise summary.

                Guidelines:
                - Do NOT start with "Here's a summary of the news" or similar introductory phrases.
                - Focus on hard data, facts, objective information, dates and places.
                - Maintain neutrality; avoid bias, opinions, or editorializing.
                - Be concise and direct; omit unnecessary details or repetition.
                - Avoid generalized disclaimers or evasive language.
                - Do not include double asterisks or single asterisks in the summary.
                - Include source links in the summary!
                - Add date to each news item if possible.
                """},
                {"role": "user", "content": f"Results:\n{json.dumps(results, indent=2)}\n\n."},
            ],
            max_tokens=8000
        )
        return response.choices[0].message.content
    except Exception as e:
        send_telegram_message(f"Error asking LLM: {e}")
        return ""

def search_brave_news(topic, freshness='pd'):
    results = []
    try:
        params = {
            "q": topic,
            "count": 5,
            "country": "all",
            "search_lang": "en",
            "spellcheck": 1,
            "extra_snippets": True,
            "freshness": freshness
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
                formatted_result = {
                    "page_age": result['page_age'],
                    "topic": topic,
                    "title": result['title'],
                    "description": result['description'],
                    "extra_snippets": result.get("extra_snippets", []),
                    "url": result['url']
                }
                results.append(formatted_result)
                with open("results.json", "a") as f:
                    json.dump(formatted_result, f)
                    f.write('\n')
                time.sleep(1)
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
                    if message.lower() == '/help':
                        send_help_message()
                    else:
                        process_topic(message)
            time.sleep(1)
        except Exception as e:
            print(f"Error handling incoming messages: {e}")

def send_help_message():
    help_text = """
Welcome to TheNews bot! Here's how to use it:

1. Simply send any topic or search query, and I'll fetch the latest news for you.
2. I'll search for news from the past day, week, month, year, or all time until I find results.
3. You'll receive a concise summary of the news articles found.

Example: Send "climate change" to get the latest news about climate change.

For any issues or feedback, please contact the bot administrator.
    """
    send_telegram_message(help_text)

def process_topic(message: str):
    freshness_levels = ['pd', 'pw', 'pm', 'py', 'all']
    topic = message
    results = []

    for freshness in freshness_levels:
        results = search_brave_news(topic, freshness)
        if results:
            break

    if results:
        summary = ask_llm(results)
        send_telegram_message(summary)
        return summary
    else:
        no_results_message = f"No results found for topic: {topic}"
        send_telegram_message(no_results_message)
        return no_results_message

def main():
    welcome_message = """
TheNews bot is now running!

To get started, simply send any topic you're interested in, and I'll fetch the latest news for you.
For more information on how to use the bot, send /help.

Happy news reading!
    """
    send_telegram_message(welcome_message)
    with open("results.txt", "w") as f:
        f.write("")
    handle_incoming_messages()

if __name__ == "__main__":
    main()