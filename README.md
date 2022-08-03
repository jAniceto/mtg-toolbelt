# mtg-toolbelt
 
A collection of tools for Magic the Gathering.

## Instalation

Using `pipenv`:
```
$ pipenv install
```


## Usage
```
$ python mtgo_toolbelt [command]
```

Main commands:

- `db_update` - create or update card DB.


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
