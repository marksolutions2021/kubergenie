from kubergenie.genie_best_pick import get_best_pick
import os
import pandas as pd
import re

def load_latest_indicators(ticker):
    filename = f"data/{ticker.replace('.', '_')}_indicators.csv"
    if not os.path.exists(filename):
        return None

    df = pd.read_csv(filename)
    if df.empty:
        return None

    latest = df.dropna().iloc[-1]
    return {
        "RSI": round(float(latest.get("RSI", 0)), 2),
        "MACD": round(float(latest.get("MACD", 0)), 2),
        "Signal": round(float(latest.get("Signal", 0)), 2),
        "Close": round(float(latest.get("Close", 0)), 2),
        "Volume": int(latest.get("Volume", 0)),
    }

def genie_respond(ticker, question):
    # Normalize and clean input
    q = question.lower()
    q = q.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    q = q.replace("whats", "what is")
    q = re.sub(r"[^\w\s]", "", q)  # remove all punctuation
    q = q.strip()

    print("[Genie parsed]:", q)

    # Auto-detect ticker
    for possible in ["wipro", "tcs", "reliance"]:
        if possible in q:
            ticker = possible.upper() + ".NS"

    # ✅ Best pick logic
    if "best pick" in q:
        print("[Genie debug]: detected 'best pick' exact phrase ✅")
        return get_best_pick()

    if "best" in q and "pick" in q:
        print("[Genie debug]: detected 'best' and 'pick' separately ✅")
        return get_best_pick()

    # Load latest indicators
    indicators = load_latest_indicators(ticker)
    if not indicators:
        return f"📉 Sorry, I couldn't find data for {ticker}"

    if "rsi" in q:
        return f"📊 RSI for {ticker} is {indicators['RSI']}"

    elif "macd" in q:
        return f"📊 MACD for {ticker} is {indicators['MACD']}, Signal line is {indicators['Signal']}"

    elif "price" in q or "close" in q:
        return f"💰 Latest close price for {ticker} is ₹{indicators['Close']}"

    elif "volume" in q:
        return f"📦 Volume for {ticker} was {indicators['Volume']:,}"

    elif "buy" in q or "sell" in q or "should i" in q:
        if indicators['RSI'] < 30 and indicators['MACD'] > indicators['Signal']:
            return f"✅ {ticker} looks oversold with bullish MACD — a BUY signal."
        elif indicators['RSI'] > 70 and indicators['MACD'] < indicators['Signal']:
            return f"⚠️ {ticker} looks overbought with bearish MACD — consider SELLING."
        else:
            return f"⏳ {ticker} has no strong buy/sell signal. Hold or wait."

    return f"🤔 I didn’t understand. Try asking about RSI, MACD, or say 'Should I buy TCS'."