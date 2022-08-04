from datetime import date, timedelta
import json
import typer
from pathlib import Path
from mtg_toolbelt.utils import load_config, setup_dir
from mtg_toolbelt.database import cards
from mtg_toolbelt.metagame import mtgo_standings, metagame


config = load_config()
data_files_path = config['global']['data_files_path']
scryfall_db_url = config['database']['oracle_cards_url']

app = typer.Typer()


@app.command()
def test():
    """Test command"""
    import os
    print('Working dir:', os.getcwd())
    print('Data files path', os.getcwd() + '\\' + config['global']['data_files_path'])
    print('Works!')


@app.command()
def db_update():
    """Create or update card database from Scryfall."""
    db_path = Path(data_files_path) / 'db'
    cards.update_db(scryfall_db_url, db_path)


@app.command()
def standings(format_: str, start_date: str = None, end_date: str = None, show: bool = False):
    """Scrape decklists from MTGO standings provided by magic.wizards.com."""
    if not end_date:
        end_date = date.today().strftime("%Y-%m-%d")
    if not start_date:
        start = date.today() - timedelta(days=30)
        start_date = start.strftime("%Y-%m-%d")

    metagame_path = Path(data_files_path) / 'metagame'
    setup_dir(metagame_path)

    decks = mtgo_standings.scrape_decklists(start_date, end_date, format_, metagame_path)

    # Display deck lists in terminal
    if show:
        for deck in decks:
            deck.print()
            input("Press Enter see next deck...")


@app.command()
def meta(sideboard: bool = False, total_count: bool = False, top: int = 25):
    """Get metagame data on card frequencies."""
    if sideboard:
        board = 'sideboard'
    else:
        board = 'mainboard'
    if total_count:
        rank = 'total_count'
    else:
        rank = 'unique_count'

    # Load standings
    standings_path = Path(data_files_path) / 'metagame' / 'standings.json'
    with open(standings_path, 'r') as f:
        standings_dict = json.load(f)
        decks = standings_dict['decks']

    # Ranks cards
    card_rank = metagame.get_card_counts(decks, board=board, rank=rank)

    # Print results
    print(f"{standings_dict['format'].upper()} METAGAME")
    print(f"- {standings_dict['start_date']} - {standings_dict['end_date']}")
    print(f"- {board} only, {rank.replace('_', ' ')}\n")
    print('Rank', 'Count', 'Card')
    i = 1
    for card, freq in card_rank.items():
        if i == top + 1:
            break
        print(f"{(str(i) + ')').ljust(4)} {str(freq[rank]).ljust(5)} {card}")
        i += 1
    print()


def cli():
    app()
