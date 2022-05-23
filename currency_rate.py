import requests


def get_currency_rate(currency):
    print(currency)
    if currency == "PLN" or currency == "pln":
        return 1
    else:
        request = requests.get(f"https://api.nbp.pl/api/exchangerates/rates/a/{currency}/?format=json")
        result = request.json()
        rate = result['rates'][0]['mid']
        return rate
