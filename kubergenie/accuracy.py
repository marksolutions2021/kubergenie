import pandas as pd
import os
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

data_folder = os.path.join(BASE_DIR, "kubergenie", "data")
signals_folder = os.path.join(BASE_DIR, "kubergenie", "signals")

# 🔍 Diagnostic: check linked folders and file presence
print(f"📂 Data folder path: {data_folder}")
print(f"📂 Signals folder path: {signals_folder}")

if os.path.exists("data"):
    print("📄 Data folder contents:", os.listdir("data"))
else:
    print("❌ Data folder not found")

if os.path.exists("signals"):
    print("📄 Signals folder contents:", os.listdir("signals"))
else:
    print("❌ Signals folder not found")

def classify_accuracy(
    backtest_path=os.path.join(RESULTS_DIR, "backtest_v2.csv"),
    output_path=os.path.join(RESULTS_DIR, "accuracy_results.csv")
):
    if not os.path.exists(backtest_path):
        print("⚠️ No backtest results found.")
        return

    df = pd.read_csv(backtest_path)

    if 'Profit %' not in df.columns:
        print("❌ 'Profit %' column not found in backtest results.")
        return

    df['Profit %'] = pd.to_numeric(df['Profit %'], errors='coerce')
    df.dropna(subset=['Profit %'], inplace=True)

    if df.empty:
        print("❌ No valid data in backtest file after cleaning.")
        return

    df['Accuracy'] = df['Profit %'].apply(lambda x: 'Correct' if x > 0 else 'Wrong')
    df.to_csv(output_path, index=False)

    accuracy = df['Accuracy'].value_counts(normalize=True).to_dict()
    correct_pct = round(accuracy.get('Correct', 0) * 100, 2)
    wrong_pct = round(accuracy.get('Wrong', 0) * 100, 2)

    print(f"✅ Accuracy results saved to {output_path}")
    print(f"🎯 Accuracy: {correct_pct}% Correct, {wrong_pct}% Wrong")


def plot_accuracy(
    accuracy_path=os.path.join(RESULTS_DIR, "accuracy_results.csv")
):
    if not os.path.exists(accuracy_path):
        print("⚠️ No accuracy results found.")
        return

    df = pd.read_csv(accuracy_path)

    if 'Accuracy' not in df.columns:
        print("⚠️ 'Accuracy' column missing in results file.")
        return

    accuracy_counts = df['Accuracy'].value_counts()

    plt.figure(figsize=(6, 4))
    accuracy_counts.plot(kind='bar', color=['green', 'red'])
    plt.title('Prediction Accuracy')
    plt.ylabel('Count')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "accuracy_chart.png"))
    plt.show()


def log_accuracy_results():
    print("🧠 Accuracy evaluation done.")


def export_accuracy_to_csv():
    classify_accuracy()
    plot_accuracy()


def clean_genie_signals(file_path="kubergenie/signals/GenieSignals.csv"):
    if not os.path.exists(file_path):
        print("⚠️ GenieSignals.csv not found.")
        return

    df = pd.read_csv(file_path)
    initial_rows = len(df)
    df = df.dropna(subset=["Price", "Signal", "Confidence"])

    optional_columns = ["RSI", "MACD", "Pattern", "Insider", "News", "Risks"]
    for col in optional_columns:
        if col in df.columns:
            df[col] = df[col].fillna("N/A")

    df = df.drop_duplicates()
    df.to_csv(file_path, index=False)
    print(f"🧼 Cleaned GenieSignals.csv ({initial_rows} → {len(df)} rows)")


# ✅ FIX: Add missing update_accuracy_data function
def update_accuracy_data(signals_file="kubergenie/signals/GenieSignals.csv", actual_outcome=None):
    """
    Generate one accuracy CSV per stock from GenieSignals.csv.
    """

    if not os.path.exists(signals_file):
        print(f"Signals file not found: {signals_file}")
        return

    df = pd.read_csv(signals_file)

    if df.empty:
        print("No signals found.")
        return

    # Use whichever column actually contains the stock symbol
    stock_col = "Ticker" if "Ticker" in df.columns else "Stock"

    accuracy_dir = os.path.join("kubergenie", "accuracy_data")
    os.makedirs(accuracy_dir, exist_ok=True)

    for stock in df[stock_col].dropna().unique():

        stock_df = df[df[stock_col] == stock].copy()

        if actual_outcome is not None:
            stock_df["Outcome"] = actual_outcome
        elif "ActualOutcome" in stock_df.columns:
            stock_df["Outcome"] = stock_df["ActualOutcome"]
        else:
            stock_df["Outcome"] = "Neutral"

        outfile = os.path.join(
            accuracy_dir,
            f"{stock.replace('.NS','').upper()}.csv"
        )

        stock_df.to_csv(outfile, index=False)
        print(f"Created: {outfile}")