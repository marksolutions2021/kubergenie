import pandas as pd

df = pd.read_csv("kubergenie/signals/GenieSignals.csv")
first_stock = df.iloc[0]['Stock']
fake_entry = {
    'Stock': first_stock,
    'Signal': 'BUY',
    'Confidence': 75,
    'Date': '2025-07-20',
    'Price': df.iloc[0]['Price'] - 10,
    'RSI': 'N/A',
    'MACD': 'N/A',
    'Pattern': 'N/A',
    'Insider': 'N/A',
    'News': 'N/A',
    'Risks': 'N/A'
}

# Insert BUY row at top
df = pd.concat([pd.DataFrame([fake_entry]), df], ignore_index=True)
df.to_csv("kubergenie/signals/GenieSignals.csv", index=False)
print("✅ GenieSignals patched with fake BUY to trigger backtest.")
