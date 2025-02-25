# TheNews Bot 🗞️

A Telegram bot that fetches and summarizes news articles on any topic using the Brave Search API and Groq LLM-powered summarization.

## Features

- 🔍 Real-time news search using Brave Search API
- 🤖 AI-powered news summarization using Groq LLM
- 📱 Telegram bot interface for easy interaction
- ⏱️ Adaptive time-based search (past day, week, month, year)
- 🌍 Global English news coverage

## Prerequisites

- Python 3.x
- Telegram Bot Token
- Groq API Key
- Brave Search API Key

## Installation

1. Clone the repository:

```bash
git clone https://github.com/ghsaboias/the-news.git
cd the-news
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

You can either:

- Create a `.env` file in the project root:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GROQ_API_KEY=your_groq_api_key
BRAVE_API_KEY=your_brave_api_key
TELEGRAM_CHAT_ID=your_chat_id
```

- Or set the environment variables directly in your system/shell

The code uses python-dotenv to load the `.env` file, but will also work with system environment variables if they're set directly.

## Usage

1. Start the bot:

```bash
python main.py
```

2. In Telegram, send any topic to the bot to get news summaries:

- Simply type a topic (e.g., "climate change")
- Use `/help` to see usage instructions

## Features in Detail

### News Search

- Searches for news using Brave Search API
- Automatically adjusts search timeframe if no recent results are found
- Supports various freshness levels:
  - Past day (pd)
  - Past week (pw)
  - Past month (pm)
  - Past year (py)
  - All time (all)
- Returns up to 5 most relevant articles per search

### News Summarization

- Uses Groq's Llama 3.1 8B Instant model for summarization
- Focuses on key facts and important details
- Includes source links in summaries
- Maintains neutrality and objectivity
- Avoids introductory phrases and editorializing
- Includes dates when available

### Telegram Integration

- Real-time message handling
- Instant news delivery
- Simple and intuitive interface
- Help command for user guidance
- Error handling with user notifications

## Project Structure

- `main.py`: Core application logic including news search, summarization, and Telegram bot functionality
- `requirements.txt`: Project dependencies
- `.env`: Configuration and API keys (optional, can use system environment variables instead)
- `results.json`: Cached search results (appended mode)
- `results.txt`: Clean slate file for new sessions

## Dependencies

- `groq`: Groq API client for LLM services
- `brave-search`: Brave Search API client
- `requests`: HTTP library for API calls
- `python-dotenv`: For loading environment variables from .env file

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Brave Search for providing the news search API
- Groq for the LLM API
- Telegram for the bot platform
