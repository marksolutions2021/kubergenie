# insider.py

import random

# Simulated insider activity data for known stocks
SIMULATED_INSIDER_DATA = {
    "WIPRO.NS": {"buy": 5, "sell": 1},
    "TCS.NS": {"buy": 1, "sell": 4},
    "RELIANCE.NS": {"buy": 3, "sell": 2},
    "INFY.NS": {"buy": 2, "sell": 2},
}

def get_insider_sentiment(ticker):
    """
    Returns a sentiment score and label based on insider trading activity.
    Positive buying activity increases confidence.
    """
    activity = SIMULATED_INSIDER_DATA.get(ticker.upper(), None)
    
    if activity:
        buys = activity["buy"]
        sells = activity["sell"]

        if buys > sells:
            return 5, "Insider Buying 💰"
        elif sells > buys:
            return -5, "Insider Selling ⚠️"
        else:
            return 0, "Neutral Insider Activity 😐"
    else:
        # If no data, return neutral
        return 0, "No Insider Data ❔"
