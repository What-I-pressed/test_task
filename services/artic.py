import json
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


def place_exists(external_place_id: str) -> bool:
    url = f"https://api.artic.edu/api/v1/artworks/{external_place_id}?fields=id,title"
    try:
        with urlopen(url, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
            data = payload.get("data", {})
            return str(data.get("id")) == str(external_place_id)
    except (HTTPError, URLError, TimeoutError, ValueError, OSError):
        return False
