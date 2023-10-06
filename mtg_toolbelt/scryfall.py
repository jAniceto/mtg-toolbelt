from functools import lru_cache
import requests


@lru_cache(maxsize=None)
def get_card(name: str, currency: str = 'tix'):
    """Get a Scryfall card object for a given card name.
    Calculates the best price in the chosen currency.
    Example:
        {
            ... other Scryfall object keys ...
            'name': 'Delver of Secrets // Insectile Aberration',
            'searched_name': 'Delver of Secrets',
            'price_unit': 'tix',
            'prices': [('SET1', '0.04'), ('SET2', '0.06')],
            'best_price': ('SET1', '0.04')
        }
    """
    # Validate price currency
    valid_price_currencies = ['tix', 'usd', 'eur']
    if currency not in valid_price_currencies:
        print(f"Invalid price unit. Select one of {', '.join(valid_price_currencies)}")
        return

    # Get list of all cards with a name: https://api.scryfall.com/cards/search?order=released&q=%2B%2B%21%22Rancor%22
    query = f'!"{name}"'  # search by exact name
    params = {
        'q': query,
        'order': currency,
        'unique': 'prints',
    }
    r = requests.get('https://api.scryfall.com/cards/search', params=params)
    reprints = r.json()['data']  # list of Scryfall card objects

    # Create info dict
    desired_keys = ['name', 'image_uris', 'mana_cost', 'cmc', 'type_line', 'oracle_text', 'colors', 'legalities', 'set', 'set_name']
    card_info = {k: v for k, v in reprints[0].items() if k in desired_keys}
    card_info['searched_name'] = name  # name used in the card search
    card_info['price_unit'] = currency
    card_info['prices'] = []  # to fill with (set, price) for the selected currency
    card_info['best_price'] = None  # to fill with the best price

    # Get prices of all reprints
    for reprint in reprints:
        if reprint['prices'][currency]:
            card_info['prices'].append((reprint['set'].upper(), reprint['prices'][currency]))

    if card_info['prices']:
        card_info['best_price'] = min(card_info['prices'], key=lambda prc: float(prc[1]))
    else:
        print(f'\nWARNING: No price found for {card_info["name"]}')

    return card_info


@lru_cache
def get_best_price(name: str, currency: str = 'tix'):
    """Return the best price of a card for a given currency from Scryfall."""
    card = get_card(name, currency=currency)
    try:
        return float(card['best_price'][1])
    except TypeError:
        return 0


if __name__ == '__main__':
    # Example cards
    CARDS = [
        'Brainstorm',
        'Delver of Secrets',
        'Ancient Den',
        'Basilisk Gate',
    ]
    CURRENCY = 'tix'

    for card_name in CARDS:
        price = get_best_price(card_name, currency=CURRENCY)
        print(f"{card_name}: {price} {CURRENCY}")
