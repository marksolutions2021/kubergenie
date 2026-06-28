# kubergenie/reporter.py

import csv
import os
from datetime import datetime
import pandas as pd

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# ✅ Signal report saving function
def save_signal_report(ticker, signal, indicators):
    date = datetime.now().strftime("%Y-%m-%d")
    filename = os.path.join(
        RESULTS_DIR,
        f"genie_signal_report_{date}.csv"
    )

    
    file_exists = os.path.isfile(filename)

    with open(filename, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "Date", "Ticker", "Signal", "RSI", "MACD", "Pattern", "SR_Breakout", "Confidence"
            ])

        writer.writerow([
            date,
            ticker,
            signal,
            round(indicators.get("RSI", 0), 2),
            round(indicators.get("MACD", 0), 2),
            indicators.get("PatternSignal", "-"),
            indicators.get("SR_Breakout", "-"),
            indicators.get("GenieConfidence", "-")
        ])

# ✅ Accuracy export function
def export_accuracy_to_csv(
    score_data,
    filename=os.path.join(RESULTS_DIR, "genie_accuracy_log.csv")
):
    df = pd.DataFrame(score_data)
    df.to_csv(filename, index=False)
