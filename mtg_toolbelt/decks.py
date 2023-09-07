import json
from pathlib import Path
from mtg_toolbelt.models import Deck


def mainboard_by_types(deck: Deck, card_db_path: Path = Path('data/db/card-db.json')):
    """
    Organize mainboard cards by type.
    
    Example output:
    {
        'creatures': [
            (4, 'Vault Skirge'), 
            (4, 'Quirion Ranger')
        ], 
        'sorceries': [], 
        'instants': [], 
        'enchantments': [
            (4, 'Rancor')
        ], 
        'artifacts': [
            (1, 'Relic of Progenitus')
        ], 
        'lands': [
            (10, 'Forest')
            (4, 'Ancient Den'),
        ]
    }
    """
    # Load card database if available
    if card_db_path.exists():
        with open(card_db_path, 'r') as f:
                card_db = json.load(f)
    else:
        print('Card DB not found.')
        return

    mainboard_by_type = {
        'creatures': [], 
        'sorceries': [], 
        'instants': [], 
        'enchantments': [], 
        'artifacts': [], 
        'lands': [],
    }

    for card in deck.mainboard:
        if 'Land' in card_db[card[1]]['type_line']:
            mainboard_by_type['lands'].append(card)
        elif 'Creature' in card_db[card[1]]['type_line']:
            mainboard_by_type['creatures'].append(card)
        elif 'Sorcery' in card_db[card[1]]['type_line']:
            mainboard_by_type['sorceries'].append(card)
        elif 'Instant' in card_db[card[1]]['type_line']:
            mainboard_by_type['instants'].append(card)
        elif 'Enchantment' in card_db[card[1]]['type_line']:
            mainboard_by_type['enchantments'].append(card)
        elif 'Artifact' in card_db[card[1]]['type_line']:
            mainboard_by_type['artifacts'].append(card)
        else:
            print(f'None of the main types found for {card[1]}')

    return mainboard_by_type


def get_price(deck: Deck, currency: str = 'tix', card_db_path: Path = Path('data/db/card-db.json')):

    # Validate price currency
    valid_currencies = ['tix', 'usd', 'eur']
    if currency not in valid_currencies:
        print(f"Invalid currency. Select one of {', '.join(valid_currencies)}")
        return
    
    # Load card database if available
    if card_db_path.exists():
        with open(card_db_path, 'r') as f:
                card_db = json.load(f)
    else:
        print('Card DB not found.')
        return
    
    # Calculate prices
    mainboard_price = 0
    for card in deck.mainboard:
        try:
            price = float(card_db[card[1]]['prices'][currency])
        except TypeError:
            price = 0
        mainboard_price += ( card[0] * price )

    sideboard_price = 0
    for card in deck.sideboard:
        try:
            price = float(card_db[card[1]]['prices'][currency])
        except TypeError:
            price = 0
        sideboard_price += ( card[0] * price )

    decklist_price = mainboard_price + sideboard_price

    return decklist_price, mainboard_price, sideboard_price
    

if __name__ == '__main__':
    # Example deck
    deck = Deck(
        mainboard=[
            (4, 'Rancor'),
            (4, 'Vault Skirge'),
            (4, 'Quirion Ranger'),
            (10, 'Forest'),
            (4, 'Ancient Den'),
            (1, 'Relic of Progenitus'),
        ],
        sideboard=[
            (2, 'Relic of Progenitus'),
        ],
        name='Test Deck',
        color='gruul',
        tags=['gruul', 'gruul'],
        author='me'
    )

    # Test organizing mainboard by price
    print(mainboard_by_types(deck))

    # Test calculating deck price
    price, price_main, price_side = get_price(deck, 'tix')
    print(price, price_main, price_side)
