import pandas as pd
import os
from datetime import datetime

def generate_leaderboard_data(save_csv=True):
    """Generates leaderboard from indicator CSVs and optionally saves it."""
    today = datetime.now().strftime("%Y-%m-%d")
    folder = "data/"
    results = []

    for file in os.listdir(folder):
        if file.endswith("_indicators.csv"):
            df = pd.read_csv(os.path.join(folder, file))
            if df.empty or "GenieSignal" not in df.columns:
                continue

            latest = df.dropna().iloc[-1]
            stock_name = file.replace("_indicators.csv", "").replace("_", ".")

            # ----- Handle GenieConfidence safely -----
            raw_conf = latest.get("GenieConfidence", 0)
            try:
                conf_val = float(raw_conf)
            except:
                conf_val = 0

            results.append({
                "Stock": stock_name,
                "Signal": latest.get("GenieSignal", "HOLD"),
                "RSI": round(latest.get("RSI", 0), 2),
                "MACD": round(latest.get("MACD", 0), 2),
                "Date": latest.get("Date", today),

                # 👇 Replaced with numeric usable key for sorting
                "confidence": conf_val,

                "Insider": latest.get("InsiderTag", "Unknown"),
                "OptionScore": latest.get("OptionScore", 50),
                "ManagementTrustScore": latest.get("ManagementTrustScore", 60)
            })

    leaderboard_df = pd.DataFrame(results)

    if leaderboard_df.empty:
        print("⚠️ No stock data found for leaderboard.")
        return leaderboard_df

    # Rank order: BUY > HOLD > SELL
    signal_order = {"BUY": 1, "HOLD": 2, "SELL": 3}
    leaderboard_df["Rank"] = leaderboard_df["Signal"].map(lambda x: signal_order.get(str(x).upper(), 99))

    # Sort by Signal Rank + Confidence + RSI
    leaderboard_df = leaderboard_df.sort_values(
        by=["Rank", "confidence", "RSI"],
        ascending=[True, False, False]
    )

    print("\n📊 Top Stock Leaderboard:")
    print(leaderboard_df[["Stock", "Signal", "RSI", "MACD", "confidence", "Date"]].to_string(index=False))

    if save_csv:
        os.makedirs("results", exist_ok=True)
        leaderboard_df.to_csv(f"results/leaderboard_{today}.csv", index=False)

    return leaderboard_df


def update_leaderboard():
    """Called by pipeline to refresh leaderboard CSV."""
    generate_leaderboard_data(save_csv=True)


def get_leaderboard():
    """Called by web API to return leaderboard as list of dicts."""
    df = generate_leaderboard_data(save_csv=False)
    return df.to_dict(orient="records") if not df.empty else []
