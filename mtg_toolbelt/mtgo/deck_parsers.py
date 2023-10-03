import sys
import json
import logging
import sys
import time
from pathlib import Path
from typing import List, Dict

from mtg_toolbelt.decks import Deck
from mtg_toolbelt.utils import FAMILIES

# Logging config
logger = logging.getLogger(__name__)
logging.basicConfig(
    handlers=[
        logging.StreamHandler(sys.stdout),  # print log to terminal
        # logging.FileHandler("log_file_name.log", mode="w"),  # log to file
    ],
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)


def search_deck(name: str, deck_list: List[Dict]):
    """Given a deck name, return the deck info dictionary if it exists in a given list of deck dictionaries."""
    for d in deck_list:
        if d['name'] == name:
            return d
    return None


def find_family(deck_name: str) -> str:
    """Given a deck name, try to find the deck family."""
    for family in FAMILIES:
        if family in deck_name.lower():
            return family


def count_missing_properties(decks_list: List[Deck], prop: str) -> int:
    """For a list of Deck objects (decks_list), count the number of decks with missing property (prop)."""
    return sum((getattr(d, prop) is None) or (getattr(d, prop) == []) for d in decks_list)


def create_deck_json(decks_dir_path: Path = Path('data/mtgo-decks')):
    """Create or update a deck info dict.
    This is a JSON file with a list of dictionaries containing basic deck info to be edited by the user
    """
    # Get old deck info is it exists
    old_decks_json = decks_dir_path / 'decks.json'
    if old_decks_json.exists():
        logger.info('Found deck.json. Updating data...')
        with open(old_decks_json, 'r') as f:
            decks_old = json.load(f)
    else:
        logger.info('No decks.json file found. Creating a new one...')

    # Get new decks
    valid_decks_path = decks_dir_path / 'valid'
    deck_files = [f for f in valid_decks_path.iterdir() if f.is_file() and str(f).endswith('.txt')]

    # Create new deck data
    decks = []
    for deck_file in deck_files:
        # Create deck object
        deck_name = deck_file.stem
        deck = Deck(name=deck_name)

        # Add info from existing data, if available
        if old_decks_json.exists():
            # Check for deck info in previous json deck info file
            prev_deck_info = search_deck(deck_name, decks_old)

            if prev_deck_info:
                # Update deck object with previous info
                try:
                    deck.tags = prev_deck_info['tags']
                except KeyError:
                    pass
                try:
                    deck.color = prev_deck_info['family']  # compatibility with older versions
                except KeyError:
                    deck.color = prev_deck_info['color']
                try:
                    deck.author = prev_deck_info['author']
                except (KeyError, TypeError):
                    deck.author = prev_deck_info['source']['name']  # compatibility with older versions
                try:
                    deck.source = prev_deck_info['source']['link']  # compatibility with older versions
                except (KeyError, TypeError):
                    deck.source = prev_deck_info['source']
                try:
                    deck.created_at = prev_deck_info['created_at']
                except KeyError:
                    pass
            else:
                deck.color = find_family(deck_name)

        decks.append(deck)

    decks_dicts = [d.to_dict_for_edit() for d in decks]

    # Summarise data
    logger.info(f"Total decks: {len(decks)}")
    logger.info(f"Decks with missing color: {count_missing_properties(decks, 'color')}")
    logger.info(f"Decks with missing tags: {count_missing_properties(decks, 'tags')}")
    logger.info(f"Decks with missing author: {count_missing_properties(decks, 'author')}")
    logger.info(f"Decks with missing source: {count_missing_properties(decks, 'source')}")

    # Create new json file
    new_decks_json = decks_dir_path / 'decks_new.json'
    with open(new_decks_json, 'w') as f:
        json.dump(decks_dicts, f, indent=4)

    # Delete previous backup
    try:
        old_backup_path = decks_dir_path / 'decks_old.json'
        old_backup_path.unlink()
    except:
        pass

    # Rename files
    try:
        old_decks_json.rename(decks_dir_path / 'decks_old.json')
    except FileNotFoundError:
        pass
    new_decks_json.rename(decks_dir_path / 'decks.json')

    logger.info("Done")


def parse_deck_files(decks_dir_path: Path = Path('data/mtgo-decks')):
    """Parses deck files (.txt) for all decks in decks.json."""
    start_time = time.time()
    logger.info('Loading decks from JSON file...')

    # Get current list of decks (decks.json)
    decks_file = decks_dir_path / 'decks.json'
    with open(decks_file, 'r') as f:
        deck_list = json.load(f)

    total_decks = len(deck_list)
    logger.info(f'Processing {total_decks} decks.')

    # Sort list of decks by deck name
    all_decks = sorted(deck_list, key=lambda k: k['name'])

    # Create deck objects
    decks = [Deck(**d) for d in all_decks]

    # Parse decklists and update deck objects
    for deck in decks:
        deck_txt_file = decks_dir_path / f"valid/{deck.name}.txt"
        deck.get_board_from_txt(deck_txt_file)

    pass


if __name__ == '__main__':
    # Create or update a deck.json file
    create_deck_json(decks_dir_path=Path('../../data/mtgo-decks'))

    # Create a complete (including decklist) deck_full.json file
    parse_deck_files(decks_dir_path=Path('../../data/mtgo-decks'))


