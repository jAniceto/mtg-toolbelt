import json
from pathlib import Path
import requests
from mtg_toolbelt.utils import setup_dir


def get_bulk_data_url():
    """Scryfall API request to get the URL of the bulk card data."""
    scryfall_oracle_url = 'https://api.scryfall.com/bulk-data/oracle-cards'
    r = requests.get(scryfall_oracle_url)
    return r.json()['download_uri']


def scryfall_db_download(file_path: Path):
    """Download data from URL and save to filepath."""
    download_uri = get_bulk_data_url()
    with open(file_path, "wb") as file:
        response = requests.get(download_uri)
        file.write(response.content)


def update_db(db_dir: Path):
    """Create or update database."""
    setup_dir(db_dir)

    # Download Scryfall data
    oracle_file_path = db_dir / 'oracle-cards.json'
    scryfall_db_download(oracle_file_path)

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
    update_db(Path('../../data/db'))
