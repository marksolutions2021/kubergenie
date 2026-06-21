import pandas as pd
import os

def get_best_pick():
    folder = "data"
    picks = []

    for filename in os.listdir(folder):
        if not filename.endswith("_indicators.csv"):
            continue

        ticker = filename.replace("_indicators.csv", "").replace("_", ".")
        filepath = os.path.join(folder, filename)

        try:
            df = pd.read_csv(filepath)
            if df.empty:
                continue

            latest = df.dropna().iloc[-1]
            confidence = float(latest.get("GenieConfidence", 0))

            picks.append((ticker, confidence))
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            continue

    if not picks:
        return "🚫 No stocks with GenieConfidence found."

    best = sorted(picks, key=lambda x: x[1], reverse=True)[:5]
    response = "🌟 Top Genie Picks:\n\n"
    for ticker, score in best:
        response += f"🔹 {ticker} → GenieConfidence: {score}\n"

    return response
