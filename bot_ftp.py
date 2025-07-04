import freecurrencyapi
client = freecurrencyapi.Client('fca_live_vAnFC5yRpXJtIDpVLkrqJX2PDsgytPbZm9Bcodpj')

EUR_curr = client.latest(base_currency='EUR')
SET_curr = ['USD', 'RUB']
filtered_curr = {k: v for k, v in EUR_curr['data'].items() if k in SET_curr}
needed_curr = "\n".join([f"1 EUR = {v:.2f} {k}" for k, v in filtered_curr.items()])
print(needed_curr)
print(f"{filtered_curr['USD']:.2f}")

""" response = requests.get(freecurrencyapi)
data = response.json()
# Constants
EUR_RUB = data['data']['RUB']
print(EUR_RUB) """