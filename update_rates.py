import os
import json
from dotenv import load_dotenv
import freecurrencyapi

# Load API key from .env
load_dotenv()
API_KEY = os.environ["FREECURRENCY_API_KEY"]

client = freecurrencyapi.Client(API_KEY)

def fetch_and_save_rates():
    EUR_curr = client.latest(base_currency='EUR')
    SET_curr = ['USD', 'RUB']
    filtered = {k: v for k, v in EUR_curr['data'].items() if k in SET_curr}

    with open("exchange_rates.json", "w", encoding="utf-8") as f:
        json.dump(filtered, f, indent=2, ensure_ascii=False)
    
    print("Rates updated successfully:", filtered)

if __name__ == "__main__":
    fetch_and_save_rates()