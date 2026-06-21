import yfinance as yf
import pandas as pd
import traceback
from kubergenie.indicators import calculate_indicators
from .price_action import detect_candlestick_patterns, detect_sr_breakouts
from .news_sentiment import fetch_news_and_analyze_sentiment
from .news_logger import save_news_log
from .management_analysis import fetch_management_data
from .insider import get_insider_sentiment
from .options import fetch_option_data
from .signals import save_genie_signal


def fetch_stock_data(ticker, period="6mo", interval="1d", save_signal=True):
    try:
        print(f"📥 Fetching data for {ticker}...")
        df = yf.download(ticker, period=period, interval=interval, group_by="column")

        if isinstance(df.columns, pd.MultiIndex):
            if ticker in df.columns.levels[1]:
                df = df.xs(ticker, axis=1, level=1, drop_level=True)
            else:
                print(f"⚠️ Ticker {ticker} not found in MultiIndex.")
                return None, None, None, None

        df = df.dropna().copy()
        df.reset_index(inplace=True)

        if not isinstance(df, pd.DataFrame) or df.empty or 'Close' not in df.columns:
            print(f"⚠️ Invalid data for {ticker}.")
            return None, None, None, None

        print("✅ Data before indicators:\n", df.head())
        print(f"📦 Raw DF: {type(df)}, shape: {df.shape}")

        # Indicators
        df, rsi_value, macd_diff = calculate_indicators(df)
        if df is None or rsi_value is None or macd_diff is None:
            print(f"⚠️ Indicator calculation failed for {ticker}.")
            return None, None, None, None

        # Price Action
        df = detect_candlestick_patterns(df)
        df = detect_sr_breakouts(df)

        final_row = df.iloc[-1]
        pattern_signal = final_row.get("PatternSignal", None)
        sr_breakout = final_row.get("SR_Breakout", None)

        # Basic Signal
        signal = "BUY" if rsi_value > 50 and macd_diff > 0 else "SELL"

        indicators = {
            'RSI': round(rsi_value, 2),
            'MACD': round(macd_diff, 2),
            'PatternSignal': pattern_signal,
            'SR_Breakout': sr_breakout
        }

        # Insider
        insider_boost, insider_tag = get_insider_sentiment(ticker)
        indicators["InsiderSentiment"] = insider_boost
        indicators["InsiderTag"] = insider_tag

        # Confidence Calculation
        base_confidence = 60 if signal == "BUY" else 40
        genie_confidence = base_confidence + insider_boost

        # Volatility
        volatility_series = df['Close'].pct_change().rolling(window=14).std()
        volatility = round(float(volatility_series.dropna().iloc[-1]), 4)

        # News Sentiment
        news_sentiment_score, headlines = fetch_news_and_analyze_sentiment(ticker)
        indicators['NewsSentiment'] = news_sentiment_score

        if news_sentiment_score > 0.2:
            genie_confidence += 10
            sentiment_tag = "📈 Positive News"
        elif news_sentiment_score < -0.2:
            genie_confidence -= 10
            sentiment_tag = "📉 Negative News"
        else:
            sentiment_tag = "😐 Neutral"

        save_news_log(ticker, headlines, news_sentiment_score)

        # Management Analysis
        management_data = fetch_management_data(ticker)
        trust_score = management_data.get("TrustScore", 60)
        indicators["ManagementTrustScore"] = trust_score

        if trust_score >= 80:
            genie_confidence += 5
        elif trust_score < 50:
            genie_confidence -= 10

        # Options Data
        option_data, option_error = fetch_option_data(ticker)
        if option_data:
            indicators.update({
                "OptionCallVolume": option_data.get("CallVolume", 0),
                "OptionPutVolume": option_data.get("PutVolume", 0),
                "PCR": option_data.get("PCR", 1),
                "OptionScore": option_data.get("OptionScore", 50)
            })
            print(f"📉 Option Data: PCR={option_data['PCR']}, Score={option_data['OptionScore']}")
            if option_data["OptionScore"] > 70:
                genie_confidence += 5
        elif option_error:
            print(f"⚠️ Option Data Error: {option_error}")
            indicators["OptionScore"] = 50

        # Clamp Confidence
        genie_confidence = max(0, min(genie_confidence, 100))

        print(f"📊 Indicators: RSI={rsi_value:.2f}, MACD_diff={macd_diff:.2f}, Pattern={pattern_signal}, SR={sr_breakout}")
        print(f"🤖 Final GenieConfidence: {genie_confidence}%")

        # Save Signal only if needed
        if save_signal:
            from datetime import datetime
            latest_date = df['Date'].iloc[-1]
            if not isinstance(latest_date, str):
                latest_date = pd.to_datetime(latest_date).strftime('%Y-%m-%d')

            latest_price = df['Close'].iloc[-1]
            save_genie_signal(ticker, signal, genie_confidence, latest_date, latest_price)
            print(f"✅ GenieSignal saved for {ticker}: {signal} ({genie_confidence}%)")

        return signal, indicators, [f"Volatility: {volatility:.4f}"], genie_confidence

    except Exception as e:
        print(f"❌ Fatal error while analyzing {ticker}: {e}")
        traceback.print_exc()
        return None, None, None, None


def analyze_stock(ticker, period="6mo", interval="1d"):
    """
    API-friendly wrapper for fetch_stock_data.
    Does not save signals, just returns analysis results.
    """
    signal, indicators, extra, genie_confidence = fetch_stock_data(
        ticker, period=period, interval=interval, save_signal=False
    )

    result = {
        "ticker": ticker,
        "signal": signal,
        "confidence": genie_confidence,
        "indicators": indicators,
        "extra": extra
    }
    return result
