import json
from pathlib import Path
from requests import get
from mtg_toolbelt.utils import setup_dir


def scryfall_db_download(url: str, file_path: Path):
    """Download data from URL and save to filepath"""
    with open(file_path, "wb") as file:
        response = get(url)
        file.write(response.content)


def update_db(source_url: str, db_dir: Path):
    """
    Create or update database
    """
    setup_dir(db_dir)

    # Download Scryfall data
    filename = source_url.split('/')[-1]
    oracle_file_path = db_dir / filename
    scryfall_db_download(source_url, oracle_file_path)

    # Load Scryfall data
    with open(oracle_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Create cards dict
    cards_dict = dict()
    for card in data:
        cards_dict[card['name']] = card

    # Save to JSON
    card_json_file_path = db_dir / 'card-db.json'
    with open(card_json_file_path, 'w', encoding='utf-8') as f:
        json.dump(cards_dict, f)

    # Log
    print('JSON database created at:', card_json_file_path)
    print('Number of cards:', len(cards_dict))


if __name__ == '__main__':
    update_db(
        'https://c2.scryfall.com/file/scryfall-bulk/oracle-cards/oracle-cards-20220714090218.json',
        Path('../../data/db')
    )
