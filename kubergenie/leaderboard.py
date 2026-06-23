import pandas as pd
import os
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
RESULTS_DIR = os.path.join(BASE_DIR, "results")


def generate_leaderboard_data(save_csv=True):
    """Generates leaderboard from indicator CSVs and optionally saves it."""
    today = datetime.now().strftime("%Y-%m-%d")
    results = []

    if not os.path.exists(DATA_DIR):
        print("⚠️ Data folder not found.")
        return pd.DataFrame()

    for file in os.listdir(DATA_DIR):

        if file.endswith("_indicators.csv"):

            try:
                df = pd.read_csv(os.path.join(DATA_DIR, file))

                if df.empty:
                    continue

                clean_df = df.dropna(how="all")

                if clean_df.empty:
                    continue

                latest = clean_df.iloc[-1]

                stock_name = file.replace("_indicators.csv", "").replace("_", ".")

                raw_conf = latest.get("GenieConfidence", 0)

                try:
                    conf_val = float(raw_conf)
                except:
                    conf_val = 0

                results.append({
                    "Stock": stock_name,
                    "Signal": latest.get("GenieSignal", "HOLD"),
                    "RSI": round(float(latest.get("RSI", 0)), 2),
                    "MACD": round(float(latest.get("MACD", 0)), 2),
                    "Date": latest.get("Date", today),
                    "confidence": conf_val,
                    "Insider": latest.get("InsiderTag", "Unknown"),
                    "OptionScore": latest.get("OptionScore", 50),
                    "ManagementTrustScore": latest.get("ManagementTrustScore", 60)
                })

            except Exception as e:
                print(f"⚠️ Error reading {file}: {e}")
                continue

    leaderboard_df = pd.DataFrame(results)

    if leaderboard_df.empty:
        print("⚠️ No stock data found for leaderboard.")
        return leaderboard_df

    # BUY > HOLD > SELL
    signal_order = {
        "BUY": 1,
        "HOLD": 2,
        "SELL": 3
    }

    leaderboard_df["Rank"] = leaderboard_df["Signal"].astype(str).str.upper().map(
        lambda x: signal_order.get(x, 99)
    )

    leaderboard_df = leaderboard_df.sort_values(
        by=["Rank", "confidence", "RSI"],
        ascending=[True, False, False]
    )

    print("\n📊 Top Stock Leaderboard:")
    print(
        leaderboard_df[
            ["Stock", "Signal", "RSI", "MACD", "confidence", "Date"]
        ].to_string(index=False)
    )

    if save_csv:
        os.makedirs(RESULTS_DIR, exist_ok=True)

        leaderboard_df.to_csv(
            os.path.join(
                RESULTS_DIR,
                f"leaderboard_{today}.csv"
            ),
            index=False
        )

    return leaderboard_df


def update_leaderboard():
    """Refresh leaderboard CSV."""
    generate_leaderboard_data(save_csv=True)


def get_leaderboard():
    """Return leaderboard as list of dictionaries."""
    df = generate_leaderboard_data(save_csv=False)

    if df.empty:
        return []

    return df.to_dict(orient="records")