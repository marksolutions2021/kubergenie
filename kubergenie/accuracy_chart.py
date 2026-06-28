import pandas as pd
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHART_FOLDER = os.path.join(PROJECT_ROOT, "static", "charts")
os.makedirs(CHART_FOLDER, exist_ok=True)

def plot_accuracy_chart(input_data, stock_name):
    """
    Unified function to plot accuracy chart from either:
    - A list of backtest results (main.py)
    - A ticker string to load from CSV (app.py)
    """

    # Case 1: If input_data is a list (from backtest)
    if isinstance(input_data, list):
        df = pd.DataFrame(input_data)
        if df.empty or not {"Date", "Change%", "Outcome"}.issubset(df.columns):
            print(f"⚠️ Invalid backtest data for {stock_name}")
            return None

        color_map = {
            "Correct": "green",
            "Wrong": "red",
            "Neutral": "gray"
        }

        df["Color"] = df["Outcome"].map(color_map)
        df["Change%"] = pd.to_numeric(df["Change%"], errors='coerce')

        plt.figure(figsize=(10, 5))
        plt.bar(df["Date"], df["Change%"], color=df["Color"])
        plt.title(f"🎯 Backtest Accuracy: {stock_name}")
        plt.ylabel("Change after 3 Days (%)")

    # Case 2: If input_data is a stock symbol string (load from CSV)
    elif isinstance(input_data, str):
        ticker = input_data.upper().replace('.NS', '')
        csv_path = os.path.join("kubergenie", "accuracy_data", f"{ticker}.csv")
        if not os.path.exists(csv_path):
            print(f"❌ CSV not found for {ticker}")
            return None

        df = pd.read_csv(csv_path)
        if df.empty or not {"Date", "Outcome"}.issubset(df.columns):
            print(f"⚠️ Invalid CSV format for {ticker}")
            return None

        correct = (df["Outcome"] == "Correct").cumsum()
        wrong = (df["Outcome"] == "Wrong").cumsum()
        total = correct + wrong
        accuracy = (correct / total) * 100

        plt.figure(figsize=(10, 4))
        plt.plot(df["Date"], accuracy, marker='o', linestyle='-')
        plt.title(f"📈 Accuracy Trend: {ticker}")
        plt.ylabel("Accuracy (%)")

    else:
        print("❌ Unsupported input for accuracy chart.")
        return None

    plt.xlabel("Date")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    filename = f"accuracy_{stock_name.replace('.NS','').upper()}.png"
    filepath = os.path.join(CHART_FOLDER, filename)
    plt.savefig(filepath)
    plt.close()
    print(f"✅ Accuracy chart saved to {filepath}")
    return filename

def plot_accuracy_from_csv(stock_name):
    import pandas as pd
    file_path = os.path.join("signals", "GenieBacktest.csv")

    if not os.path.exists(file_path):
        print("⚠️ GenieBacktest.csv not found")
        return None

    df = pd.read_csv(file_path)

    # Filter for the specific stock
    filtered = df[df['Ticker'] == stock_name]

    if filtered.empty:
        print(f"⚠️ No backtest data for {stock_name}")
        return None

    # Prepare results in expected format
    results = []
    for _, row in filtered.iterrows():
        results.append({
            "Date": row.get("Date", ""),
            "Change%": row.get("Change%", 0),
            "Outcome": row.get("ActualOutcome", "Neutral")
        })

    return plot_accuracy_chart(results, stock_name)
