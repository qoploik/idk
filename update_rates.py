import os
import json
import sys
from dotenv import load_dotenv
import freecurrencyapi
load_dotenv()
API_KEY = os.environ["FREECURRENCY_API_KEY"]

client = freecurrencyapi.Client(API_KEY)

def fetch_and_save_rates():
    try:
        # 1) Fetch rates
        EUR_curr = client.latest(base_currency='EUR')
        SET_curr = ['USD', 'RUB']

        # 2) Validate API response structure
        if (
            not EUR_curr 
            or "data" not in EUR_curr 
            or not all(k in EUR_curr["data"] for k in SET_curr)
        ):
            print("API response missing expected currencies or structure.")
            sys.exit(1)  # exit without overwriting existing file

        # 3) Filter desired currencies
        filtered = {k: v for k, v in EUR_curr['data'].items() if k in SET_curr}

        # 4) Save only if fetch & validation succeeded
        with open("exchange_rates.json", "w", encoding="utf-8") as f:
            json.dump(filtered, f, indent=2, ensure_ascii=False)

        print("Rates updated successfully:", filtered)

    except Exception as e:
        print("Fetch failed. Keeping last successful rates untouched.\nError:", e)
        sys.exit(1)  # exit with error status but do not overwrite existing file

if __name__ == "__main__":
    fetch_and_save_rates()