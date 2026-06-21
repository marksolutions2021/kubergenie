# options.py

import random

def fetch_option_data(ticker):
    try:
        # 🔮 Simulated option data (replace with real API later if needed)
        call_volume = random.randint(10000, 50000)
        put_volume = random.randint(1000, 30000)
        open_interest = random.randint(50000, 200000)
        
        # PCR = Put Volume / Call Volume
        pcr = round(put_volume / call_volume, 2)
        
        # OptionScore logic
        if pcr < 0.8:
            option_score = 80  # Bullish sentiment
        elif pcr > 1.2:
            option_score = 40  # Bearish sentiment
        else:
            option_score = 60  # Neutral
        
        data = {
            "CallVolume": call_volume,
            "PutVolume": put_volume,
            "PCR": pcr,
            "OpenInterest": open_interest,
            "OptionScore": option_score
        }
        
        return data, None
    except Exception as e:
        return None, str(e)
