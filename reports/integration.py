import datetime
from functools import lru_cache

import requests

from reports.constants import NBP_API, PLN


# This could potentailly grow without bound (however unlikely it is)
@lru_cache
def get_exchange_rate(currency: str, date: datetime.date) -> float:
    """
    Assuming we can ask for exchange rates once a day we can cache the anwser for that long.
    We can make this as granular as we want. Asking the API for exchange
    rated on every request is probably a bad idea.
    """
    if currency == PLN:
        return 1.0
    currency = currency.lower()
    date = str(date.date())
    response = requests.get(
        f"{NBP_API}/api/exchangerates/rates/a/{currency}/{date}/{date}",
        params={"format": "json"},
    )
    if response.status_code != 200:
        # Exception is raised in order not to cache an invalid anwser
        raise RuntimeError(f"{NBP_API} could not be reached")
    data = response.json()
    return data["rates"][0]["mid"]
