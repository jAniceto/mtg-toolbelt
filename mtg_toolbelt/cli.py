import typer
from pathlib import Path
from mtg_toolbelt.utils import load_config
from mtg_toolbelt.database import cards


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
    db_dir = Path(data_files_path) / 'db'
    cards.update_db(scryfall_db_url, db_dir)


def cli():
    app()
