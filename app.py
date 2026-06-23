from flask import Flask, render_template, request, jsonify
from kubergenie.pipeline import run_genie_pipeline
from kubergenie.analyzer import analyze_stock
from kubergenie.accuracy_chart import plot_accuracy_from_csv
import json
import os
import pandas as pd

app = Flask(__name__)

LEADERBOARD_FILE = "kubergenie/leaderboard.json"
CSV_PATH = "kubergenie/signals/GenieSignals.csv"



# ✅ Home page
@app.route('/')
def index():
    return render_template('index.html')

# ✅ Test route
@app.route('/test')
def test():
    return "KuberGenie Test OK"

# ✅ Web Form Analyze (Manual Single Stock Input)
@app.route('/analyze', methods=['POST'])
def analyze():
    stock_symbol = request.form.get('symbol', '').upper()

    try:
        # Run stock analysis
        result = analyze_stock(stock_symbol)

        # Update leaderboard
        update_leaderboard_entry(result)

        # ✅ Save to GenieSignals.csv
        signal = result.get("signal", "N/A")
        genie_confidence = result.get("confidence", 0)
        indicators = result.get("indicators", {})
        risks = result.get("risks", "No Risks")

        new_signal = {
            "Ticker": stock_symbol,
            "Signal": signal,
            "Confidence": genie_confidence,
            "RSI": indicators.get("RSI", "N/A"),
            "MACD": indicators.get("MACD", "N/A"),
            "Pattern": indicators.get("Pattern", "N/A"),
            "Insider": indicators.get("Insider", "N/A"),
            "News": indicators.get("News", "N/A"),
            "Risks": risks
        }

        if os.path.exists(CSV_PATH):
            df = pd.read_csv(CSV_PATH)
        else:
            df = pd.DataFrame()

        df = pd.concat([df, pd.DataFrame([new_signal])], ignore_index=True)
        df.to_csv(CSV_PATH, index=False)

        # ✅ Prepare output for web display
        output = f"""
🔮 Genie Analysis for {stock_symbol}:

Signal: {signal}
Confidence: {genie_confidence}%
Indicators: {json.dumps(indicators)}
Risks: {risks}
"""

    except Exception as e:
        output = f"Error: {str(e)}"

    return render_template('index.html', result=output)


# ✅ API Analyze (JSON POST method)
@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    data = request.json
    symbol = data.get('symbol', '').upper()

    try:
        result = analyze_stock(symbol)

        # Update leaderboard
        update_leaderboard_entry(result)

        return jsonify({
            'status': 'success',
            'symbol': symbol,
            'result': result
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ✅ Run Pipeline for Predefined Stocks
@app.route('/run_pipeline', methods=['POST'])
def run_pipeline_route():
    stock_list = ["WIPRO.NS", "TCS.NS", "RELIANCE.NS"]

    try:
        pipeline_results = run_genie_pipeline(stock_list)

        # ✅ Update leaderboard for each result
        for res in pipeline_results:
            update_leaderboard_entry(res)

        # ✅ Prepare output for web display
        output = ""
        for res in pipeline_results:
            output += f"""
Ticker: {res['ticker']}
Signal: {res['signal']}
Confidence: {res['confidence']}%
Indicators: {res['indicators']}
Risks: {res['risks']}
------------------------------
"""

        return render_template('index.html', result=output)

    except Exception as e:
        return render_template('index.html', result=f"Error: {str(e)}")


# ✅ Web Leaderboard (Clean, Just View)
@app.route('/leaderboard')
def leaderboard():
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []

    # Optional: Sort leaderboard by confidence descending
    sorted_data = sorted(
    data,
    key=lambda x: float(x.get("confidence") or 0),
    reverse=True
)


    return render_template('leaderboard.html', leaderboard=sorted_data)


# ✅ Accuracy Chart Viewer with dynamic generation
@app.route('/accuracy_chart/<stock>')
def accuracy_chart(stock):
    try:
        # Generate accuracy chart dynamically
        plot_accuracy_from_csv(stock)

        # Check if chart was created
        filename = f"accuracy_{stock}.png"
        file_path = os.path.join('static/charts', filename)

        if not os.path.exists(file_path):
            return f"Chart could not be generated for {stock}"

        return render_template('charts.html', stock=stock, chart_file=filename)

    except Exception as e:
        return f"Error generating accuracy chart for {stock}: {str(e)}"


# ✅ Helper Function to Update Leaderboard (Avoid Duplicate)
def update_leaderboard_entry(new_entry):
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r") as f:
            leaderboard = json.load(f)
    else:
        leaderboard = []

    found = False
    for idx, item in enumerate(leaderboard):
        if item.get("ticker") == new_entry.get("ticker"):
            leaderboard[idx] = new_entry
            found = True
            break

    if not found:
        leaderboard.append(new_entry)

    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(leaderboard, f, indent=4)


# ✅ Render Deployment
if __name__ == '__main__':
    print("KuberGenie Server Starting...")
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)