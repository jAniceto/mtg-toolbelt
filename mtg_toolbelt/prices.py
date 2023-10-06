from pathlib import Path
from mtg_toolbelt.database.cards import load_card_db


def get_card_price(card_name: str, unit: str = 'tix', card_db_path: Path = Path('data/db/card-db.json')):
    # Validate price currency
    VALID_PRICE_UNITS = ['tix', 'usd', 'eur']
    if unit not in VALID_PRICE_UNITS:
        print(f"Invalid price unit. Select one of {', '.join(VALID_PRICE_UNITS)}")
        return

    # Load card DB
    if card_db_path.exists():
        card_db = load_card_db(card_db_path)
    else:
        print('Card DB not found.')
        return

    # Search card in database
    try:
        # Search exact card name
        matches = [card_db[card_name]]
    except KeyError as e:
        matches = [v for k, v in card_db.items() if card_name in k]

    # Extract desired price
    for c in matches:
        if c['prices'][unit]:
            return float(c['prices'][unit])

    # If no price is found return 0
    print(f"No price found for {card_name} in {unit}.")
    return 0


if __name__ == '__main__':
    # Example cards
    CARDS = [
        'Brainstorm',
        'Delver of Secrets',
        'Ancient Den',
    ]
    UNIT = 'tix'

    for card in CARDS:
        p = get_card_price(card, unit=UNIT, card_db_path=Path('../data/db/card-db.json'))
        print(f"{card}: {p:.2f} {UNIT}")
