import logging

import requests
from django.core.cache import cache

logger = logging.getLogger(__name__)

QUOTE_CACHE_KEY = "analytics:motivational_quote"
QUOTE_CACHE_TIMEOUT = 60 * 60
FALLBACK_QUOTE = {
    "content": "Маленькие шаги каждый день приводят к большим результатам.",
    "author": "Трекер привычек",
}


def get_motivational_quote() -> dict:
    cached_quote = cache.get(QUOTE_CACHE_KEY)
    if cached_quote is not None:
        return cached_quote

    try:
        response = requests.get(
            "https://api.quotable.io/random",
            timeout=5,
        )
        response.raise_for_status()
        payload = response.json()
        quote = {
            "content": payload["content"],
            "author": payload["author"],
        }
    except (KeyError, ValueError, requests.RequestException) as exc:
        logger.warning("Failed to fetch motivational quote: %s", exc)
        quote = FALLBACK_QUOTE

    cache.set(QUOTE_CACHE_KEY, quote, QUOTE_CACHE_TIMEOUT)
    return quote
