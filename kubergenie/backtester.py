import pandas as pd
import os


def run_backtest_v2(
        signal_data_path="kubergenie/signals/GenieSignals.csv",
        output_path="results/backtest_v2.csv"):

    if not os.path.exists(signal_data_path):
        print("⚠️ No signal data found.")
        return

    df = pd.read_csv(signal_data_path)

    # Rename Stocks → Stock if needed
    if 'Stocks' in df.columns and 'Stock' not in df.columns:
        df.rename(columns={"Stocks": "Stock"}, inplace=True)

    print(f"📂 Found signal file: {signal_data_path}")

    # Remove rows with missing required columns
    df.dropna(subset=['Stock', 'Signal', 'Confidence', 'Date', 'Price'], inplace=True)

    # Remove duplicates
    df = df.drop_duplicates()

    # Convert Date
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])

    # Clean Signal values
    df['Signal'] = df['Signal'].astype(str).str.strip().str.upper()

    # Convert numeric columns
    df['Confidence'] = pd.to_numeric(df['Confidence'], errors='coerce')
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')

    # Drop bad rows
    df.dropna(subset=['Confidence', 'Price'], inplace=True)

    if df.empty:
        print("⚠️ Signal file is empty after cleaning.")
        return

    print("\n🧪 DEBUG: Columns in loaded DataFrame:")
    print(df.columns)
    print(df.head())

    backtest_results = []

    for stock in df['Stock'].unique():

        print(f"🔍 Processing {stock}")

        stock_df = df[df['Stock'] == stock].sort_values('Date')

        in_position = False
        entry_price = None
        entry_date = None
        entry_confidence = None

        for idx, row in stock_df.iterrows():

            signal = str(row['Signal']).strip().upper()
            price = float(row['Price'])
            date = pd.to_datetime(row['Date'])

            try:
                confidence = int(row.get('GenieConfidence', row.get('Confidence', 0)))
            except:
                confidence = 0

            # BUY Entry
            if not in_position and signal == "BUY" and confidence >= 60:

                entry_price = price
                entry_date = date
                entry_confidence = confidence
                in_position = True

                print(
                    f"✅ BUY {stock} | {entry_date.date()} | Price={entry_price} | Confidence={entry_confidence}"
                )

            # SELL Exit
            elif in_position and (signal == "SELL" or idx == stock_df.index[-1]):

                exit_price = price
                exit_date = date

                profit_pct = ((exit_price - entry_price) / entry_price) * 100
                duration = (exit_date - entry_date).days

                if profit_pct > 0:
                    outcome = "WIN"
                else:
                    outcome = "LOSS"

                print(
                    f"❌ SELL {stock} | {exit_date.date()} | Profit={round(profit_pct,2)}%"
                )

                backtest_results.append({
                    "Stock": stock,
                    "Entry Date": entry_date.strftime("%Y-%m-%d"),
                    "Exit Date": exit_date.strftime("%Y-%m-%d"),
                    "Entry Price": round(entry_price, 2),
                    "Exit Price": round(exit_price, 2),
                    "Profit %": round(profit_pct, 2),
                    "Holding Days": duration,
                    "Confidence": entry_confidence,
                    "ActualOutcome": outcome
                })

                in_position = False

    if backtest_results:

        result_df = pd.DataFrame(backtest_results)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        result_df.to_csv(output_path, index=False)

        print(f"\n📊 Backtest V2 results saved to {output_path}")
        print(result_df)

    else:
        print("⚠️ No valid trades found for backtesting.")