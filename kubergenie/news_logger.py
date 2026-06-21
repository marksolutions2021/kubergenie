import os
from datetime import datetime

def save_news_log(ticker, headlines, sentiment_score):
    import os
    from datetime import datetime

    folder = "news_logs"
    os.makedirs(folder, exist_ok=True)
    filename = os.path.join(folder, f"{ticker}_news_log.txt")

    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"\n=== {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        f.write(f"Sentiment Score: {sentiment_score:.2f}\n")
        f.write("Top Headlines:\n")
        for item in headlines:
            f.write(f"• {item}\n")  # ← This must be indented under 'for'
