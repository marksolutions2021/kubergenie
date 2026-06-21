import pandas as pd
import ta

def calculate_indicators(df):
    try:
        print("📊 Calculating indicators...")
        df['Close'] = pd.to_numeric(df['Close'], errors='coerce')

        df['EMA'] = ta.trend.ema_indicator(df['Close'], window=20)
        df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
        macd_calc = ta.trend.MACD(df['Close'])
        df['MACD'] = macd_calc.macd()
        df['Signal_Line'] = macd_calc.macd_signal()

        print("✅ Indicator columns added.")
        print(df[['RSI', 'MACD', 'Signal_Line']].tail())

        # ✅ Use iloc instead of values to keep type compatibility
        rsi_value = df['RSI'].dropna().iloc[-1]
        macd_value = df['MACD'].dropna().iloc[-1] - df['Signal_Line'].dropna().iloc[-1]

        print(f"✅ RSI: {rsi_value}, MACD: {macd_value}")
        return df, rsi_value, macd_value

    except Exception as e:
        print(f"❌ Exception in indicators.py: {e}")
        return None, None, None
