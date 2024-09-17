from openai import OpenAI
from crawl4ai import WebCrawler
import requests
import os
import json
from groq import Groq
import time
from twilio.rest import Client
from brave import Brave

llm_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
crawler = WebCrawler()
twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
brave = Brave(api_key=os.getenv("BRAVE_API_KEY"))
telegram_client = Client(os.getenv("TELEGRAM_BOT_TOKEN"))
telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

crawler.warmup()

# Summary template for customizing the summary format
SUMMARY_TEMPLATE = """
Daily News Summary - {date}

{summary}
"""

def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage"
    payload = {
        "chat_id": telegram_chat_id,
        "text": message
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

def brave_search(query: str):
    search_results = brave.search(q=query, count=1)
    web_results = search_results.web_results
    news_results = search_results.news_results
    video_results = search_results.video_results
    results = {
        "web_results": web_results,
        "news_results": news_results,
        "video_results": video_results
    }
    return results

def ask_llm(results):
    formatted_results = "\n".join([
        f"{item['title']} - {item['description']} (Page Age: {item['page_age']})" 
        for item in results
    ])
    response = llm_client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful summarizer. Provided a list of news results, you produce a daily summary of the news. You are a neutral summarizer, do not include any bias or opinion. Do not provide generalized disclaimers or evasive language. Be concise and to the point."},
            {"role": "user", "content": f"Results:\n{formatted_results}\n\nUse the following template:\n{SUMMARY_TEMPLATE}"}
        ]
    )
    return response.choices[0].message.content

def send_whatsapp_message(message: str):
    try:
        twilio_client.messages.create(
            from_='whatsapp:+14155238886',
            body=message,
            to='whatsapp:+5511992745950'
        )
    except Exception as e:
        print(f"Error sending WhatsApp message: {e}")

def crawl_urls(urls: list):
    for url in urls:
        crawler.crawl(url)
        print(crawler.get_results())

def main():
    results = brave_search("India")
    summary = ask_llm(results["news_results"])
    send_telegram_message(summary)

if __name__ == "__main__":
    main()