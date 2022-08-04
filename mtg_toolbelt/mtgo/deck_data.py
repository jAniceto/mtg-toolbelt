import os
import json
import time
import datetime
import logging
import requests
from tqdm import tqdm
from pathlib import Path
from mtg_toolbelt.utils import COLORS, FAMILIES


# Dictionary to store card info
CARD_INFO_DICT = {}


def search_deck(name, deck_list):
    """
    Given a deck name, return the deck info dictionary if it exist in a given list of deck dictionaries.
    """
    for d in deck_list:
        if d['name'] == name:
            return d
    return None


def find_family(deck_name):
    """
    Given a deck name, try to find the deck family.
    """
    for family in FAMILIES:
        if family in deck_name.lower():
            return family


def create_json(decks_path=None):
    """
    Create new deck info dictionary.
    """
    if decks_path is None:
        print('Must provide argument decks_path.')
        return

    # Get old deck info is it exists
    old_decks_json = Path(decks_path, 'decks.json')
    if old_decks_json.exists():
        with open(old_decks_json, 'r') as f:
            decks_old = json.load(f)

    # Get new decks
    valid_decks_path = decks_path / 'valid'
    deck_files = [f for f in valid_decks_path.iterdir() if f.is_file() and str(f).endswith('.txt')]

    # Create new deck data
    deck_info = []
    for deck_file in deck_files:
        deck_name = deck_file.stem

        # Create deck entry
        info = {
            'name': deck_name,
            'tags': [],
            'family': None,
            'source': {'name': None, 'link': None}
        }

        if old_decks_json.exists():
            # Check for deck info in previous json deck info file
            prev_deck_info = search_deck(deck_name, decks_old)

            if prev_deck_info:
                # Update new deck dictionary with previous info
                info['tags'] = prev_deck_info['tags']
                info['family'] = prev_deck_info['family']
                info['source'] = prev_deck_info['source']
            else:
                info['family'] = find_family(deck_name)

        deck_info.append(info)

    # Create new json file
    new_decks_json = Path(decks_path, 'decks_new.json')
    with open(new_decks_json, 'w') as f:
        json.dump(deck_info, f, indent=4)

    # Delete previous backup
    try:
        old_backup_path = decks_path / 'decks_old.json'
        old_backup_path.unlink()
    except:
        pass

    # Rename files
    try:
        old_decks_json.rename(decks_path / 'decks_old.json')
    except FileNotFoundError:
        pass
    new_decks_json.rename(decks_path / 'decks.json')


def get_card_data(card_name):
    """
    Get relevant card info from Scyfall API.

    Parameters
    ----------
    card_name : str
        Name of card to search.

    Returns
    -------
    card_info : dict
        Dictionary of relevant card properties.

    Example output
    --------------
    {
        'name': 'Rancor',
        'prices': [
            ['PC2', '1.56'],
            ['DDD', '1.25'], ...
        ],
        'best_price': ['A25', '0.93'],
        'scryfall_uri': 'https://scryfall.com/card/f05/1/rancor?utm_source=api',
        'cmc': 1.0,
        'legalities': {
            'pioneer': 'not_legal',
            'modern': 'legal',
            'pauper': 'legal', ...
        },
        'image_uris': {
            'small': 'https://img.scryfall.com/cards/small/front/7/2/72a6c655-92f8-486d-b56c-9f6753f58512.jpg?1562639861',
            'normal': 'https://img.scryfall.com/cards/normal/front/7/2/72a6c655-92f8-486d-b56c-9f6753f58512.jpg?1562639861', ...
        },
        'mana_cost': '{G}',
        'colors': ['G'],
        'type': 'Enchantment — Aura',
        'is_land': False
    }
    """

    # Get list of all cards with a name: https://api.scryfall.com/cards/search?order=released&q=%2B%2B%21%22Rancor%22
    query = '++!"{}"'.format(card_name)
    params = {
        'order': 'tix',
        'unique': 'prints',
        'q': query
    }
    r = requests.get('https://api.scryfall.com/cards/search', params=params)
    reprint_dict = r.json()

    # Create return dict
    card_info = {'name': card_name,
                 'prices': [],
                 'best_price': None}

    # Get prices of all reprints
    for reprint in reprint_dict['data']:
        # Only do stuff for reprints available on MTGO
        if reprint['prices']['tix']:
            card_info['prices'].append([reprint['set'].upper(), reprint['prices']['tix']])

    if card_info['prices']:
        # card_info['best_price'] = str(min([float(set_price[1]) for set_price in card_info['prices']]))
        card_info['best_price'] = min(card_info['prices'], key=lambda x: float(x[1]))
    else:
        print(f'\nWARNING: No price found for {card_info["name"]}')

    # Get card data
    card_info['scryfall_uri'] = reprint_dict['data'][-1]['scryfall_uri']
    card_info['cmc'] = reprint_dict['data'][-1]['cmc']
    card_info['legalities'] = reprint_dict['data'][-1]['legalities']
    try:
        card_info['image_uris'] = reprint_dict['data'][-1]['image_uris']
        card_info['mana_cost'] = reprint_dict['data'][-1]['mana_cost']
        card_info['colors'] = reprint_dict['data'][-1]['colors']
        card_info['type'] = reprint_dict['data'][-1]['type_line']
    except KeyError:  # handles card with multiple faces
        card_info['image_uris'] = reprint_dict['data'][-1]['card_faces'][0]['image_uris']
        card_info['image_uris_2'] = reprint_dict['data'][-1]['card_faces'][1]['image_uris']
        card_info['mana_cost'] = reprint_dict['data'][-1]['card_faces'][0]['mana_cost']
        card_info['colors'] = reprint_dict['data'][-1]['card_faces'][0]['colors']
        card_info['type'] = reprint_dict['data'][-1]['card_faces'][0]['type_line']

    if 'Land' in card_info['type']:
        card_info['is_land'] = True
    else:
        card_info['is_land'] = False

    return card_info


def get_path(name, decks_path):
    """
    Returns the deck path from name
    """
    path = decks_path / 'valid' / f"{name}.txt"
    return path


def sort_card_list(card_list):
    """
    Sorts a list of card objects (dictionaries) by converted mana cost (placing lands first)
    :param card_list: card_list is a list of dictionaries containing info on quantity, card_name, mc, cmc, and is_land
    :return: sorted_list, a card list sorted according to the defined order
    """
    sorted_list = card_list
    sorted_list.sort(key=lambda k: k['is_land'], reverse=True)
    sorted_list.sort(key=lambda k: k['cmc'])
    return sorted_list


def store_card_info(card_info):
    global CARD_INFO_DICT
    CARD_INFO_DICT[card_info['name']] = card_info


def parse_decklist(deck_file):
    """
    Parses a decklist file
    """
    is_mainboard = True
    mainboard = []
    sideboard = []
    with open(deck_file, 'r') as f:
        for line in f:
            if line in ['\n', '\r\n']:
                is_mainboard = False
            else:
                card_line = line.strip('\n').split(' ', 1)
                if is_mainboard:
                    mainboard.append({'quantity': card_line[0],
                                      'card_name': card_line[1]})
                else:
                    sideboard.append({'quantity': card_line[0],
                                      'card_name': card_line[1]})

    # Get card info
    for card in mainboard:
        try:
            # Try to grab info from cache dict
            card.update(CARD_INFO_DICT[card['card_name']])
        except KeyError:
            # If info not in cache grab it from Scryfall API and update cache
            card_info = get_card_data(card['card_name'])
            card.update(card_info)
            store_card_info(card_info)
            time.sleep(50 / 1000)

    for card in sideboard:
        try:
            # Try to grab info from cache dict
            card.update(CARD_INFO_DICT[card['card_name']])
        except KeyError:
            # If info not in cache grab it from Scryfall API and update cache
            card_info = get_card_data(card['card_name'])
            card.update(card_info)
            store_card_info(card_info)
            time.sleep(50 / 1000)

    # Sort decklist by converted mana cost
    sorted_mainboard = sort_card_list(mainboard)
    sorted_sideboard = sort_card_list(sideboard)
    mainboard = sorted_mainboard
    sideboard = sorted_sideboard

    return mainboard, sideboard


def parse_deck_files(decks_path: Path):
    """
    Parses deck files for all decks in decks.json."""
    # Logging config
    log_file = decks_path / 'scryfall.log'
    logging.basicConfig(filename=log_file, filemode='w', level=logging.INFO)

    start_time = time.time()
    print('Grabbing data...')
    logging.info('Grabbing data...')

    # Get current list of decks (decks.json)
    decks_file = decks_path / 'decks.json'
    with open(decks_file, 'r') as f:
        deck_list = json.load(f)

    total_decks = len(deck_list)
    logging.info(f'Processing {total_decks} decks.')

    # Sort list of decks by deck name
    all_decks = sorted(deck_list, key=lambda k: k['name'])

    all_decks_list = []
    progress_bar = tqdm(all_decks)
    for i, deck in enumerate(progress_bar):
        # Get list of colors from family
        if deck['family']:
            try:
                deck['color'] = COLORS[deck['family']]
            except KeyError:
                logging.info(f"Invalid family in deck {deck['name']}.")
        else:
            logging.info(f"No specified family for deck {deck['name']}.")

        try:
            # Get path to deck file
            deck_path = get_path(deck['name'], decks_path)
            # Get last modified date
            date_modified_datetime = datetime.datetime.fromtimestamp(os.path.getmtime(deck_path))
            date_modified_string = date_modified_datetime.strftime('%Y-%m-%d')
            deck['last_modified'] = date_modified_string

        except FileNotFoundError as e:
            print(f"\nDeck file not found for {deck['name']}! ({e})")
            logging.warning(f"Deck file not found for {deck['name']}! ({e}).")
            continue

        # Parse decklist from file
        deck['mainboard'], deck['sideboard'] = parse_decklist(deck_path)

        # Calculated decklist price
        price = 0
        for card in deck['mainboard']:
            if card['best_price']:
                price += float(card['best_price'][1]) * int(card['quantity'])
        for card in deck['sideboard']:
            if card['best_price']:
                price += float(card['best_price'][1]) * int(card['quantity'])
        deck['price'] = '{:.2f}'.format(price)

        all_decks_list.append(deck)

        progress_bar.set_description(f"Completed {deck['name']}")

    # Save deck data to JSON
    full_decks_path = decks_path / 'decks_full.json'
    with open(full_decks_path, 'w') as decks_json:
        json.dump(all_decks_list, decks_json, sort_keys=True, indent=2)

    # Save card data to JSON
    cards_path = decks_path / 'cards.json'
    with open(cards_path, 'w') as cards_json:
        json.dump(CARD_INFO_DICT, cards_json, sort_keys=True, indent=2)

    # Save deck data to JSON (simple)
    KEYS_TO_REMOVE = ['card_name', 'prices', 'best_price', 'scryfall_uri', 'cmc', 'legalities', 'image_uris',
                      'mana_cost', 'colors', 'type', 'is_land']
    for deck in all_decks_list:
        for card in deck['mainboard']:
            for k in KEYS_TO_REMOVE:
                card.pop(k, None)
        for card in deck['sideboard']:
            for k in KEYS_TO_REMOVE:
                card.pop(k, None)

    simple_decks_path = decks_path / 'decks_simple.json'
    with open(simple_decks_path, 'w') as decks_simple_json:
        json.dump(all_decks_list, decks_simple_json, sort_keys=True, indent=2)

    print('\nCompleted in {0:.1f} minutes'.format((time.time() - start_time) / 60))
    logging.info('Completed in {0:.1f} minutes'.format((time.time() - start_time) / 60))
