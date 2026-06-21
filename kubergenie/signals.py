import os
import pandas as pd
from datetime import datetime

# Ensure directories exist
os.makedirs("signals", exist_ok=True)
os.makedirs("data", exist_ok=True)

def save_genie_signal(stock, signal, confidence, date, price,
                      rsi=None, macd=None, pattern=None, insider=None, news=None, risks=None):
    
    # ✅ Sanitize and format values before saving
    row = {
        'Stock': stock,
        'Signal': signal,
        'Confidence': float(confidence),
        'Date': date,
        'Price': round(float(price), 2),
        'RSI': round(float(rsi), 2) if rsi is not None else '',
        'MACD': round(float(macd), 2) if macd is not None else '',
        'Pattern': pattern if pattern else '',
        'Insider': insider if insider else '',
        'News': round(float(news), 4) if news is not None else '',
        'Risks': risks if risks else ''
    }

    # ✅ Save to combined GenieSignals.csv
    combined_path = os.path.join("signals", "GenieSignals.csv")
    if os.path.exists(combined_path):
        df_combined = pd.read_csv(combined_path, on_bad_lines='skip')
        df_combined = pd.concat([df_combined, pd.DataFrame([row])], ignore_index=True)
    else:
        df_combined = pd.DataFrame([row])
    df_combined.to_csv(combined_path, index=False)

    # ✅ Save to per-stock file
    file_path = f"data/{stock.replace('.', '_')}_indicators.csv"
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, on_bad_lines='skip')
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    else:
        df = pd.DataFrame([row])
    df.to_csv(file_path, index=False)

    print(f"✅ GenieSignal saved for {stock}: {signal} ({confidence}%)")
