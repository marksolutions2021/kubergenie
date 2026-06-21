# kubergenie_web/kubergenie/filters.py

import os
import pandas as pd
from datetime import datetime

BASE_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
BASE_SIGNALS_DIR = os.path.join(os.path.dirname(__file__), "..", "signals")

def save_signal_report(ticker, indicators, output_dir=BASE_DATA_DIR):
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"{ticker.replace('.', '_')}_indicators.csv")

    row = {
        "Date": datetime.today().strftime("%Y-%m-%d"),
        "RSI": indicators.get("RSI"),
        "MACD": indicators.get("MACD"),
        "EMA_Trend": indicators.get("EMA_Trend"),
        "VolumeSpike": indicators.get("VolumeSpike"),
        "PatternSignal": indicators.get("PatternSignal"),
        "SR_Breakout": indicators.get("SR_Breakout"),
        "NewsSentiment": indicators.get("NewsSentiment"),
        "Price": indicators.get("Price"),
        "Signal": indicators.get("Signal"),
        "GenieConfidence": indicators.get("GenieConfidence", 0)
    }

    df = pd.DataFrame([row])
    if os.path.exists(filename):
        df.to_csv(filename, mode='a', index=False, header=False)
    else:
        df.to_csv(filename, index=False)


def apply_smart_filter(indicators, risks):
    rsi = indicators.get("RSI")
    macd = indicators.get("MACD")
    ema_trend = indicators.get("EMA_Trend")
    pattern = indicators.get("PatternSignal", "")
    volume_spike = indicators.get("VolumeSpike", False)
    breakout = indicators.get("SR_Breakout", False)

    score = 0
    if 40 < rsi < 60:
        score += 1
    if macd > 0:
        score += 1
    if ema_trend == "UP":
        score += 1
    if pattern in ["Hammer", "Bullish Engulfing"]:
        score += 1
    if breakout:
        score += 1
    if volume_spike:
        score += 1
    if not risks:
        score += 1

    confidence = score * 15
    decision = "HOLD"
    if score >= 5:
        decision = "BUY ✅"
    elif score <= 2:
        decision = "SELL ⚠️"

    return decision, confidence


def append_smart_signal(ticker, signal, confidence, output_dir=BASE_SIGNALS_DIR):
    os.makedirs(output_dir, exist_ok=True)

    row = {
        "Date": datetime.today().strftime("%Y-%m-%d"),
        "Stock": ticker,
        "Signal": signal,
        "GenieConfidence": confidence,
        "Price": None
    }

    # Get last known price from indicators CSV
    ind_path = os.path.join(BASE_DATA_DIR, f"{ticker.replace('.', '_')}_indicators.csv")
    if os.path.exists(ind_path):
        df = pd.read_csv(ind_path)
        if not df.empty and "Price" in df.columns:
            row["Price"] = df.iloc[-1]["Price"]

    path = os.path.join(output_dir, "GenieSignals.csv")
    df = pd.DataFrame([row])
    if os.path.exists(path):
        df.to_csv(path, mode="a", index=False, header=False)
    else:
        df.to_csv(path, index=False)
