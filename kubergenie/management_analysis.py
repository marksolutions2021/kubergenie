# management_analysis.py

import random

def fetch_management_data(ticker):
    """
    Simulates fetching management-related data.
    In future versions, replace this with real data scraping/API calls.
    """
    management_info = {
        "PromoterHolding": round(random.uniform(35, 75), 2),  # %
        "PledgedShares": round(random.uniform(0, 10), 2),     # %
        "InsiderActivity": random.choice(["Buying", "Selling", "Neutral"]),
        "SEBIAlerts": random.choice(["None", "Warning", "Banned"]),
        "Sentiment": random.choice(["Positive", "Negative", "Neutral"])
    }

    # Custom scoring logic
    score = 100
    if management_info["PromoterHolding"] < 50:
        score -= 15
    if management_info["PledgedShares"] > 5:
        score -= 20
    if management_info["InsiderActivity"] == "Selling":
        score -= 10
    if management_info["SEBIAlerts"] != "None":
        score -= 20
    if management_info["Sentiment"] == "Negative":
        score -= 10

    score = max(0, min(100, score))
    management_info["TrustScore"] = score
    return management_info
