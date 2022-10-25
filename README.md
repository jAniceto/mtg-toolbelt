# mtg-toolbelt
 
A collection of tools for Magic the Gathering.

## Main features

`mtg-toolbelt` is a package and `CLI` with several tools for Magic the Gathering. Here are its main features:
- Automatically export decks from the Magic the Gathering Online (MTGO) client into `.txt` files. Optionally you can process this decks to JSON.
- Scrape decklists from the results' page at magic.wizards.com. 
- Analyse metagame (most used cards).
- Calculate mana curve probabilities.


## Instalation

Using `pipenv`:
```
$ pipenv install
```


## Usage
```
$ mtg-tools --help
```

```
Usage: mtg-tools [OPTIONS] COMMAND [ARGS]...

Commands:
  export        Auto export decks from MTGO into .txt.
  mana-sim      Run simulation to create a mana curve table (CSV).
  meta          Analyze metagame card usage and frequency.
  standings     Scrape decklists from MTGO standings provided by...
  update-db     Create or update card database from Scryfall (JSON).
  update-decks  Create deck data files (JSON).
```

For each command, get usage instructions by running:

```
$ mtg-tools meta --help
```

```
Usage: mtg-tools meta [OPTIONS]

  Get metagame data on card frequencies.

Options:
  --sideboard / --no-sideboard    [default: no-sideboard]
  --total-count / --no-total-count
                                  [default: no-total-count]
  --top INTEGER                   [default: 25]
  --help                          Show this message and exit.
```


## Configuration

Use the `config.json` file to set configuration variables.

```json
{
    "global": {
        "help": "Global configuration options.",
        "data_files_path": "data"
    },
    "mtg": {
        "help": "Configurations options regarding MtG.",
        "pauper_banlist": [
            "Daze", "Gitaxian Probe", "Gush", "Arcum's Astrolabe", "Expedition Map", "Mystic Sanctuary", "Fall from Favor",
            "Cloud of Faeries", "Cloudpost", "Cranial Plating", "Empty the Warrens", "Frantic Search", "Grapeshot", "High Tide",
            "Hymn to Tourach", "Invigorate", "Peregrine Drake", "Sinkhole", "Temporal Fissure", "Treasure Cruise", "Chatterstorm",
            "Sojourner's Companion", "Bonder's Ornament", "Disciple of the Vault", "Galvanic Relay", "Prophetic Prism"
        ]
    },
    "mtgo-exporter": {
        "help": "Configurations options for MTGO Exporter tool.",
        "strip_chars": ["#T1 ", "#T2 ", ".txt"]
    },
    "database" : {
        "help": "Configurations options for card database.",
        "oracle_cards_url": "https://c2.scryfall.com/file/scryfall-bulk/oracle-cards/oracle-cards-20220714090218.json"

    }
}
```

## Typical Workflow

```
$ mtg-tools update-db
$ mtg-tools export
$ mtg-tools update-decks
```