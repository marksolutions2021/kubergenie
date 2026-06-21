import os
from kubergenie.analyzer import fetch_stock_data
from kubergenie.filters import apply_smart_filter, save_signal_report, append_smart_signal
from kubergenie.accuracy import update_accuracy_data
from kubergenie.leaderboard import generate_leaderboard_data  # Changed here

BASE_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def run_genie_pipeline(stock_list, period="6mo", interval="1d"):
    results = []

    for ticker in stock_list:
        try:
            signal, indicators, risks, base_confidence = fetch_stock_data(ticker, period, interval)

            if not signal:  # No data or invalid fetch
                results.append({
                    "ticker": ticker,
                    "signal": None,
                    "confidence": 0,
                    "indicators": {},
                    "risks": {},
                    "status": "No data or signals"
                })
                continue

            # Smart filter decision
            smart_decision, confidence = apply_smart_filter(indicators, risks)

            # Save outputs
            save_signal_report(ticker, signal, indicators, output_dir=BASE_DATA_DIR)
            append_smart_signal(ticker, signal, confidence, output_dir=BASE_DATA_DIR)

            # Update accuracy & leaderboard
            update_accuracy_data(output_dir=BASE_DATA_DIR)
            generate_leaderboard_data(save_csv=True)  # Changed here

            results.append({
                "ticker": ticker,
                "signal": smart_decision,
                "confidence": confidence,
                "indicators": indicators,
                "risks": risks,
                "status": "OK"
            })

        except Exception as e:
            results.append({
                "ticker": ticker,
                "signal": None,
                "confidence": 0,
                "indicators": {},
                "risks": {},
                "status": f"Error: {str(e)}"
            })

    return results
