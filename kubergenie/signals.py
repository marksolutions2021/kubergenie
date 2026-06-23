import os
import pandas as pd

BASE_DIR = os.path.dirname(__file__)
SIGNALS_DIR = os.path.join(BASE_DIR, "signals")
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(SIGNALS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)


def save_genie_signal(stock, signal, confidence, date, price,
                      rsi=None, macd=None, pattern=None,
                      insider=None, news=None, risks=None):

    row = {
        "Date": date,
        "Stock": stock,
        "Price": round(float(price), 2),

        "RSI": round(float(rsi), 2) if rsi is not None else None,
        "MACD": round(float(macd), 2) if macd is not None else None,

        "Pattern": pattern or "",
        "Insider": insider or "",
        "News": round(float(news), 4) if news is not None else None,
        "Risks": risks or "",

        "GenieSignal": signal,
        "GenieConfidence": float(confidence)
    }

    # Combined signal file
    combined_path = os.path.join(SIGNALS_DIR, "GenieSignals.csv")

    if os.path.exists(combined_path):
        df = pd.read_csv(combined_path, on_bad_lines="skip")
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])

    df.to_csv(combined_path, index=False)

    # Per-stock file
    file_path = os.path.join(
        DATA_DIR,
        f"{stock.replace('.', '_')}_indicators.csv"
    )

    if os.path.exists(file_path):
        df_stock = pd.read_csv(file_path, on_bad_lines="skip")
        df_stock = pd.concat([df_stock, pd.DataFrame([row])], ignore_index=True)
    else:
        df_stock = pd.DataFrame([row])

    df_stock.to_csv(file_path, index=False)

    print(f"✅ GenieSignal saved for {stock}: {signal} ({confidence}%)")