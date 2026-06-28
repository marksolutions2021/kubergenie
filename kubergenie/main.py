import sys
import os
import datetime
import pandas as pd

# Path fix
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from kubergenie.analyzer import analyze_stock
from kubergenie.pipeline import run_genie_pipeline  # optional
from kubergenie.accuracy_chart import plot_accuracy_chart  # optional

# These two functions must match app.py behaviour
from kubergenie.filters import append_smart_signal
from kubergenie.leaderboard import update_leaderboard


# ---------------- CONFIG ----------------
STOCK_LIST = ["WIPRO.NS", "TCS.NS", "RELIANCE.NS"]
CSV_PATH = "kubergenie/signals/GenieSignals.csv"
# ----------------------------------------


def welcome():
    print("\n🧞‍♂️ Welcome to KuberGenie Terminal Edition")
    print("Today's Date:", datetime.date.today())
    print("Analyzing your selected stocks...\n")


def print_debug_output(result):
    """Pretty full debug output formatting"""

    print("\n" + "=" * 55)
    print(f"📌 Ticker: {result.get('ticker', 'N/A')}")
    print(f"🔮 Signal: {result.get('signal', 'N/A')}")
    print(f"🤖 Confidence: {result.get('confidence', 0)}%")

    print("\n📊 Indicators:")
    indicators = result.get("indicators", {})
    for k, v in indicators.items():
        print(f"  - {k}: {v}")

    print("\n⚠ Risk Factors:")
    risks = result.get("risks", [])
    if risks:
        for r in risks:
            print(f"  - {r}")
    else:
        print("  - No major risks detected")

    print("=" * 55 + "\n")


def save_to_csv(result):
    """Save or append consistent signal result to CSV"""

    row = {
        "Ticker": result.get("ticker"),
        "Signal": result.get("signal"),
        "Confidence": result.get("confidence"),
        "RSI": result.get("indicators", {}).get("RSI"),
        "MACD": result.get("indicators", {}).get("MACD"),
        "Pattern": result.get("indicators", {}).get("Pattern"),
        "News": result.get("indicators", {}).get("News"),
        "Insider": result.get("indicators", {}).get("Insider"),
        "Risks": "|".join(result.get("risks", []))
    }

    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
    else:
        df = pd.DataFrame()

    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(CSV_PATH, index=False)
    print("💾 Saved to GenieSignals.csv")

    ticker = result.get("ticker")
    plot_accuracy_chart(ticker, ticker)
    print(f"📈 Accuracy chart updated for {ticker}")

if __name__ == "__main__":
    welcome()

    for ticker in STOCK_LIST:

        print(f"🚀 Running analyze_stock() for {ticker}...")
        result = analyze_stock(ticker)

        if not result or result.get("signal") is None:
            print(f"⚠ No valid analysis returned for {ticker}\n")
            continue

        # 🔍 Detailed debug print
        print_debug_output(result)

        # 🏆 Leaderboard update
        update_leaderboard()

        # 📥 Save to CSV
        save_to_csv(result)

    print("\n🎉 Analysis Completed Successfully!")
