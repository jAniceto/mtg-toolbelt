import json
from pathlib import Path
import requests
from mtg_toolbelt.utils import setup_dir


def sort_price_func(price):
    if price is None:
        return float('inf')
    else:
        return float(price)


def scryfall(card_name):
    """
    Get relevant card info from Scyfall API.

    Parameters
    ----------
    card_name : str
        Name of card to search.

    Returns
    -------
    prices : dict
        Dictionary of relevant card properties.

    Example output
    --------------
    {
        'name': 'Rancor',
        'best_price': {
            'tix': {
                'set': 'set_name',
                'set_abbreviation': 'set_abb',
                'value': '1.2',
            },
            'usd': ...,
            'eur': ...
        },
        'prints': [
            {
                'set': 'set_name',
                'set_abbreviation': 'set_abb',
                'tix': '1.2',
                'usd': '1.2',
                'eur': '1.2'

            },
            ...
        ]
    }
    """
    # Get list of all cards with a name: https://api.scryfall.com/cards/search?order=released&q=%2B%2B%21%22Rancor%22
    query = f'++!"{card_name}"'
    params = {
        'order': 'released',
        'unique': 'prints',
        'q': query
        }
    r = requests.get('https://api.scryfall.com/cards/search', params=params)
    reprints = r.json()

    # Create return dict
    card = {
        'name': reprints['data'][0]['name'],
        'best_price': {}
    }

    # Get prices of all reprints
    prices = []
    for reprint in reprints['data']:
        reprint_prices = {
            'name': reprint['name'],
            'set_name': reprint['set_name'],
            'set_abbreviation': reprint['set'],
            'tix': reprint['prices']['tix'],
            'usd': reprint['prices']['usd'],
            'eur': reprint['prices']['eur']
        }
        prices.append(reprint_prices)
    card['prints'] = prices

    # Calculate best prices
    prices_by_tix = sorted(prices, key=lambda d: sort_price_func(d['tix']))
    prices_by_usd = sorted(prices, key=lambda d: sort_price_func(d['usd']))
    prices_by_eur = sorted(prices, key=lambda d: sort_price_func(d['eur']))

    card['best_price']['tix'] = {
        'set': prices_by_tix[0]['set_name'],
        'set_abbreviation': prices_by_tix[0]['set_abbreviation'],
        'value': prices_by_tix[0]['tix'],
    }
    card['best_price']['usd'] = {
        'set': prices_by_usd[0]['set_name'],
        'set_abbreviation': prices_by_usd[0]['set_abbreviation'],
        'value': prices_by_usd[0]['usd'],
    }
    card['best_price']['eur'] = {
        'set': prices_by_eur[0]['set_name'],
        'set_abbreviation': prices_by_eur[0]['set_abbreviation'],
        'value': prices_by_eur[0]['eur'],
    }

    return card


def get_prices():
    """Get a bulk data file containing every card object on Scryfall.

    Returns
    -------
    list
        List of card objects (dicts)
    """
    response = requests.get('https://api.scryfall.com/bulk-data')
    bulk_data = response.json()['data']
    for item in bulk_data:
        if item['type'] == 'default_cards':
            response = requests.get(item['download_uri'])
            data = response.json()
            return data


if __name__ == '__main__':
    from pprint import pprint

    # card_prices = scryfall('Rancor')
    # pprint(card_prices)

    card_prices = get_prices()
    pprint(card_prices[0])
