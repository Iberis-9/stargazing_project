import requests

def search_locations_raw(query: str, api_key: str):
    url = "https://api.weatherapi.com/v1/search.json"
    r = requests.get(
        url,
        params={"key": api_key, "q": query},
        timeout=10
    )
    r.raise_for_status()
    return r.json()

