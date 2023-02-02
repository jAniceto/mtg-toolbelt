from datetime import date, timedelta
import json
import typer
from pathlib import Path
from mtg_toolbelt.database import cards
from mtg_toolbelt.metagame import mtgo_standings, metagame
from mtg_toolbelt.mtgo import exporter, deck_data
from mtg_toolbelt.simulation import mana
from mtg_toolbelt.utils import load_config, setup_dir


config = load_config()
data_files_path = config['global']['data_files_path']
working_path = Path().absolute()
decks_path = Path(data_files_path) / 'mtgo-decks'

app = typer.Typer()


@app.command()
def update_db():
    """Create or update card database from Scryfall (JSON)."""
    db_path = Path(data_files_path) / 'db'
    cards.update_db(db_path)


@app.command()
def export(format_: str = 'pauper'):
    """Auto export decks from MTGO into .txt."""
    deck_path_absolute = working_path / decks_path
    setup_dir(decks_path)

    # Export decks
    exporter.auto_export(str(deck_path_absolute) + '\\')
    # exporter.auto_export(str(decks_path) + '\\')

    # Organize decks
    exporter.organize(
        decks_path=decks_path,
        strip_chars=config['mtgo-exporter']['strip_chars'],
        banlist=config['mtg']['banlist'][format_]
    )


@app.command()
def organize(format_: str = 'pauper'):
    """Organize exported decks. Usefull if deck files are already available."""
    exporter.organize(
        decks_path=decks_path,
        strip_chars=config['mtgo-exporter']['strip_chars'],
        banlist=config['mtg']['banlist'][format_]
    )
    

@app.command()
def update_decks():
    """Create deck data files (JSON)."""
    deck_data.create_json(decks_path=decks_path)
    deck_data.parse_deck_files(decks_path=decks_path)


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
    """Analyze metagame card usage and frequency."""
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
    print(f"{standings_dict['format'].upper()} METAGAME ({standings_dict['n_decks']} decks)")
    print(f"- from {standings_dict['start_date']} to {standings_dict['end_date']}")
    print(f"- {board} only, sorted by {rank.replace('_', ' ')}\n")
    print('Rank', 'Total', 'Unique', 'Freq(%)', 'Card')
    i = 1
    for card, count in card_rank.items():
        if i == top + 1:
            break
        freq = count['unique_count'] / len(decks) * 100
        print(f"{(str(i) + ')').ljust(4)} {str(count['total_count']).ljust(5)} {str(count['unique_count']).ljust(6)} {freq:<7.1f} {card}")
        i += 1
    print()


@app.command()
def mana_sim(deck_size: int = 60, turns: int = 7, on_play: bool = False, mulligans: bool = True, iterations: int = 10000):
    """Run simulation to create a mana curve table (CSV)."""
    sim_path = Path(data_files_path) / 'simulations'
    setup_dir(sim_path)

    mana.mana_curve_table(
        sim_path=sim_path,
        n_lands_range=[16, 26],
        deck_size=deck_size,
        turns=turns,
        on_play=on_play,
        consider_mulligans=mulligans,
        iterations=iterations
    )


def cli():
    app()
