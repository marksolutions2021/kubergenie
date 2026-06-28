# summary.py

import pandas as pd
from datetime import datetime
import os

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

def create_summary_row(ticker, signal, indicators, confidence):
    sentiment_value = indicators.get("NewsSentiment", 0)
    insider_sentiment = indicators.get("InsiderTag", "Unknown")
    option_score = indicators.get("OptionScore", 50)

    # News Tag
    if sentiment_value > 0.2:
        news_tag = "Positive 😃"
    elif sentiment_value < -0.2:
        news_tag = "Negative 😟"
    else:
        news_tag = "Neutral 😐"

    # Option Tag
    if option_score >= 70:
        option_tag = "Bullish 📈"
    elif option_score <= 40:
        option_tag = "Bearish 📉"
    else:
        option_tag = "Neutral 😐"

    return {
        "Stock": ticker,
        "Signal": signal,
        "RSI": round(indicators.get("RSI", 0), 2),
        "MACD": round(indicators.get("MACD", 0), 2),
        "Pattern": indicators.get("PatternSignal", "None"),
        "SR_Breakout": indicators.get("SR_Breakout", "None"),
        "Confidence": confidence,
        "News": news_tag,
        "Insider": insider_sentiment,
        "OptionSentiment": option_tag
    }


def generate_genie_summary(leaderboard):
    lines = []
    lines.append("🧞‍♂️ Genie Summary Report")
    lines.append("=" * 40)

    for entry in leaderboard:
        stock = entry.get("Stock")
        signal = entry.get("Signal")
        confidence = entry.get("GenieConfidence", "N/A")
        rsi = entry.get("RSI", "N/A")
        macd = entry.get("MACD", "N/A")
        insider = entry.get("Insider", "N/A")
        date = entry.get("Date", "N/A")
        trust_score = entry.get("ManagementTrustScore", 60)

        # Decide trust tag
        if trust_score >= 80:
            trust_tag = "✅ Strong"
        elif trust_score < 50:
            trust_tag = "⚠️ Weak"
        else:
            trust_tag = "😐 Avg"
        
    option_score = entry.get("OptionScore", 50)
    if option_score >= 70:
        option_tag = "📈 Bullish Option Sentiment"
    elif option_score <= 40:
        option_tag = "📉 Bearish Option Sentiment"
    else:
        option_tag = "😐 Neutral Option View"

        lines.append(f"\n📈 {stock} ({date})")
        lines.append(f"🔍 Signal: {signal}")
        lines.append(f"🤖 GenieConfidence: {confidence}%")
        lines.append(f"🏢 Management Trust Score: {trust_score} {trust_tag}")
        lines.append(f"💬 Insight: Genie suggests a {signal.lower()} strategy based on combined indicators.")
        lines.append(f"📊 Option Score: {option_score} → {option_tag}")
        lines.append(f"📊 RSI: {rsi}, MACD: {macd}")
        lines.append(f"🔍 Insider Activity: {insider}")

    lines.append("\n🔚 End of Report")

    # Save to file
    os.makedirs("reports", exist_ok=True)
    report_path = os.path.join("reports", "GenieSummary.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    print(f"📝 Genie Summary saved to {report_path}")

def save_daily_summary(summary_rows):
    today = datetime.now().strftime("%Y-%m-%d")
    df = pd.DataFrame(summary_rows)
    
    summary_file = os.path.join(
        RESULTS_DIR,
        f"daily_summary_{today}.csv"
    )
    df.to_csv(summary_file, index=False)
    print(f"✅ Daily summary saved to {summary_file}")


