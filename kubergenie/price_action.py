import pandas as pd
import numpy as np

def detect_candlestick_patterns(df):
    pattern_signals = []

    for i in range(len(df)):
        if i == 0:
            pattern_signals.append(None)
            continue

        try:
            open_price = df['Open'].iloc[i]
            close_price = df['Close'].iloc[i]
            high = df['High'].iloc[i]
            low = df['Low'].iloc[i]

            body = abs(close_price - open_price)
            candle_range = high - low

            if candle_range == 0:
                pattern_signals.append("NoPattern")
                continue

            # Pattern: Doji
            if body < 0.1 * candle_range:
                pattern_signals.append("Doji")

            # Bullish Engulfing
            elif close_price > open_price and body > 0.6 * candle_range:
                pattern_signals.append("BullishEngulfing")

            # Bearish Engulfing
            elif open_price > close_price and body > 0.6 * candle_range:
                pattern_signals.append("BearishEngulfing")

            else:
                pattern_signals.append("NoPattern")

        except Exception as e:
            pattern_signals.append(None)

    df['PatternSignal'] = pattern_signals
    return df  # ✅ Must return the modified DataFrame


def detect_sr_breakouts(df):
    if df is None or len(df) < 20:
        return df  # or return None, depending on your logic

    df['SR_Breakout'] = 'No Breakout'

    close_price = df['Close'].iloc[-1]
    recent_high = df['High'].rolling(window=20).max().iloc[-1]
    recent_low = df['Low'].rolling(window=20).min().iloc[-1]

    if close_price > recent_high:
        df.at[df.index[-1], 'SR_Breakout'] = 'Resistance Breakout'
    elif close_price < recent_low:
        df.at[df.index[-1], 'SR_Breakout'] = 'Support Breakdown'

    return df  # ✅ MAKE SURE THIS IS PRESENT

def analyze_price_action(df):
    """
    Master function to apply both candlestick and S/R breakout detection
    """
    df = detect_candlestick_patterns(df)
    df = detect_sr_breakouts(df)
    return df  # ✅ Final df with both new columns
