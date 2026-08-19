"""
amazon.py — Amazon Price Tracker & Search Helper
"""

import urllib.parse
import webbrowser


def search_amazon(product_name: str) -> str:
    """Search for a product on Amazon."""
    q = urllib.parse.quote_plus(product_name)
    url = f"https://www.amazon.in/s?k={q}"
    webbrowser.open(url)
    return f"Searching Amazon for '{product_name}', Sir."
