def apply_smart_filter(indicators):
    """
    Returns a smart signal decision and confidence score based on indicators + price action
    """
    rsi = indicators.get("RSI")
    macd = indicators.get("MACD")
    pattern = indicators.get("PatternSignal")
    breakout = indicators.get("SR_Breakout")

    decision = "Hold"
    confidence = 50  # base confidence

    # Basic layer: RSI + MACD logic
    if rsi and macd:
        if rsi > 60 and macd > 0:
            decision = "Buy"
            confidence += 20
        elif rsi < 40 and macd < 0:
            decision = "Sell"
            confidence += 20

    # Price Action Layer: Candlestick Patterns
    if pattern in ["BullishEngulfing"]:
        confidence += 10
    elif pattern in ["BearishEngulfing"]:
        confidence -= 10
    elif pattern == "Doji":
        confidence -= 5  # indecision

    # Price Action Layer: Support/Resistance Breakout
    if breakout == "ResistanceBreakout":
        confidence += 10
    elif breakout == "SupportBreakdown":
        confidence -= 10

    # Final cap and floor
    confidence = max(0, min(confidence, 100))

    return decision, confidence
