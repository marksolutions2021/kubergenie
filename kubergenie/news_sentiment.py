# news_sentiment.py

import requests
from datetime import datetime, timedelta
from textblob import TextBlob
import pandas as pd
import os

def fetch_news_and_analyze_sentiment(ticker):
    # Step 1: Setup query and timeframe
    company_name = ticker.replace('.NS', '')
    today = datetime.now()
    last_week = today - timedelta(days=5)
    formatted_today = today.strftime('%Y-%m-%d')
    formatted_last_week = last_week.strftime('%Y-%m-%d')

    # Step 2: Use Bing News Search API (you can replace this with NewsAPI or scraping)
    url = f"https://news.google.com/rss/search?q={company_name}+stock+after:{formatted_last_week}+before:{formatted_today}&hl=en-IN&gl=IN&ceid=IN:en"
    try:
        import feedparser
    except ImportError:
        print("⚠️ Please install feedparser: pip install feedparser")
        return 0.0, []

    feed = feedparser.parse(url)
    headlines = [entry.title for entry in feed.entries[:10]]

    if not headlines:
        return 0.0, []

    # Step 3: Analyze sentiment using TextBlob
    sentiments = []
    for title in headlines:
        blob = TextBlob(title)
        sentiments.append(blob.sentiment.polarity)

        avg_sentiment = sum(sentiments) / len(sentiments)

    # Save to CSV (optional)
    os.makedirs("results", exist_ok=True)
    news_file = f"results/news_sentiment_{datetime.now().strftime('%Y-%m-%d')}.csv"
    df = pd.DataFrame({
        "Ticker": [ticker]*len(headlines),
        "Headline": headlines,
        "Sentiment": sentiments
    })
    df.to_csv(news_file, mode='a', index=False, header=not os.path.exists(news_file))

    # ✅ FIXED: Return the actual headline list
    return avg_sentiment, headlines
