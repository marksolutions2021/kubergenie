import os
import pandas as pd
import matplotlib.pyplot as plt

def plot_genie_confidence(stocks):
    confidences = {}
    
    for ticker in stocks:
        file = f"data/{ticker.replace('.', '_')}_indicators.csv"
        if not os.path.exists(file):
            continue
        df = pd.read_csv(file)
        if "GenieConfidence" in df.columns and not df.empty:
            try:
                latest = df.dropna().iloc[-1]
                score = float(latest.get("GenieConfidence", 0))
                confidences[ticker] = round(score, 2)
            except:
                continue

    if not confidences:
        print("⚠️ No GenieConfidence data to plot.")
        return

    plt.figure(figsize=(8, 5))
    stocks = list(confidences.keys())
    values = list(confidences.values())

    bar_colors = ['green' if v >= 80 else 'orange' if v >= 60 else 'red' for v in values]

    plt.barh(stocks, values, color=bar_colors)
    plt.xlabel("GenieConfidence (%)")
    plt.title("🧞‍♂️ GenieConfidence Across Stocks")
    plt.xlim(0, 100)
    plt.grid(axis='x', linestyle='--', alpha=0.4)

    os.makedirs("charts", exist_ok=True)
    file_path = "charts/genie_confidence.png"
    plt.tight_layout()
    plt.savefig(file_path)
    plt.close()
    print(f"📊 GenieConfidence chart saved to {file_path}")
