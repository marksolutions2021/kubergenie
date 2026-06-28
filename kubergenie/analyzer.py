import os

BASE_DIR = os.path.dirname(__file__)
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

        df = yf.download(
            ticker,
            period=period,
            interval=interval,
            group_by="column",
            progress=False,
            threads=False
        )

        if df is None or df.empty:
            print(f"⚠️ No data downloaded for {ticker}")
            return None, None, None, None

        if isinstance(df.columns, pd.MultiIndex):
            try:
                df = df.xs(ticker, axis=1, level=1, drop_level=True)
            except Exception:
                print(f"⚠️ Could not extract MultiIndex for {ticker}")
                return None, None, None, None

        df = df.dropna().copy()
        df.reset_index(inplace=True)

        if df.empty or "Close" not in df.columns:
            print(f"⚠️ Invalid data for {ticker}")
            return None, None, None, None

        print("✅ Data before indicators:")
        print(df.head())
        print(f"📦 Raw DF: {type(df)}, shape: {df.shape}")

        # Indicators
        df, rsi_value, macd_diff = calculate_indicators(df)

        if df is None or rsi_value is None or macd_diff is None:
            print(f"⚠️ Indicator calculation failed for {ticker}")
            return None, None, None, None

        # Price action
        df = detect_candlestick_patterns(df)
        df = detect_sr_breakouts(df)

        final_row = df.iloc[-1]
        pattern_signal = final_row.get("PatternSignal", None)
        sr_breakout = final_row.get("SR_Breakout", None)

        # Signal
        signal = "BUY" if rsi_value > 50 and macd_diff > 0 else "SELL"

        indicators = {
            "RSI": round(rsi_value, 2),
            "MACD": round(macd_diff, 2),
            "PatternSignal": pattern_signal,
            "SR_Breakout": sr_breakout
        }

        # Insider sentiment
        insider_boost, insider_tag = get_insider_sentiment(ticker)
        indicators["InsiderSentiment"] = insider_boost
        indicators["InsiderTag"] = insider_tag

        # Confidence
        base_confidence = 60 if signal == "BUY" else 40
        genie_confidence = base_confidence + insider_boost

        # Volatility
        volatility_series = df["Close"].pct_change().rolling(window=14).std()

        if volatility_series.dropna().empty:
            volatility = 0
        else:
            volatility = round(float(volatility_series.dropna().iloc[-1]), 4)

        # News sentiment
        news_sentiment_score, headlines = fetch_news_and_analyze_sentiment(ticker)
        indicators["NewsSentiment"] = news_sentiment_score

        if news_sentiment_score > 0.2:
            genie_confidence += 10
        elif news_sentiment_score < -0.2:
            genie_confidence -= 10

        save_news_log(ticker, headlines, news_sentiment_score)

        # Management
        management_data = fetch_management_data(ticker)
        trust_score = management_data.get("TrustScore", 60)
        indicators["ManagementTrustScore"] = trust_score

        if trust_score >= 80:
            genie_confidence += 5
        elif trust_score < 50:
            genie_confidence -= 10

        # Options
        option_data, option_error = fetch_option_data(ticker)

        if option_data:
            indicators.update({
                "OptionCallVolume": option_data.get("CallVolume", 0),
                "OptionPutVolume": option_data.get("PutVolume", 0),
                "PCR": option_data.get("PCR", 1),
                "OptionScore": option_data.get("OptionScore", 50)
            })

            print(
                f"📉 Option Data: PCR={option_data['PCR']}, "
                f"Score={option_data['OptionScore']}"
            )

            if option_data["OptionScore"] > 70:
                genie_confidence += 5

        elif option_error:
            print(f"⚠️ Option Data Error: {option_error}")
            indicators["OptionScore"] = 50

        genie_confidence = max(0, min(genie_confidence, 100))

        print(
            f"📊 Indicators: RSI={rsi_value:.2f}, "
            f"MACD_diff={macd_diff:.2f}, "
            f"Pattern={pattern_signal}, "
            f"SR={sr_breakout}"
        )

        print(f"🤖 Final GenieConfidence: {genie_confidence}%")

        if save_signal:
            latest_date = df["Date"].iloc[-1]

            if not isinstance(latest_date, str):
                latest_date = pd.to_datetime(latest_date).strftime("%Y-%m-%d")

            latest_price = float(df["Close"].iloc[-1])

            save_genie_signal(
                stock=ticker,
                signal=signal,
                confidence=genie_confidence,
                date=latest_date,
                price=latest_price,
                rsi=rsi_value,
                macd=macd_diff,
                pattern=pattern_signal,
                insider=insider_tag,
                news=news_sentiment_score,
                risks=f"Volatility: {volatility:.4f}"
            )

            print(
                f"✅ GenieSignal saved for {ticker}: "
                f"{signal} ({genie_confidence}%)"
            )

        return (
            signal,
            indicators,
            [f"Volatility: {volatility:.4f}"],
            genie_confidence
        )

    except Exception as e:
        print(f"❌ Fatal error while analyzing {ticker}: {e}")
        traceback.print_exc()
        return None, None, None, None


def analyze_stock(ticker, period="6mo", interval="1d"):

    signal, indicators, extra, genie_confidence = fetch_stock_data(
        ticker,
        period=period,
        interval=interval,
        save_signal=False
    )

    result = {
        "ticker": ticker,
        "signal": signal,
        "confidence": genie_confidence,
        "indicators": indicators,
        "extra": extra
    }

    return result