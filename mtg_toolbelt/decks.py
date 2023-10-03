import json
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import date
from typing import List, Tuple, Optional


@dataclass
class Deck:
    name: str = None
    mainboard: Optional[List[Tuple]] = None
    sideboard: Optional[List[Tuple]] = None
    color: Optional[str] = None
    tags: Optional[List[str]] = None
    author: Optional[str] = None
    source: Optional[str] = None
    created_at: Optional[str] = None
    price: Optional[Tuple[float, float, float]] = None
    price_currency: Optional[str] = None

    def __post_init__(self):
        self.created_at = date.today().strftime("%Y/%m/%d")

    def to_dict(self):
        return self.__dict__

    def to_dict_for_edit(self):
        return {
            "name": self.name,
            "color": self.color,
            "tags": self.tags,
            "author": self.author,
            "source": self.source,
            "created_at": self.created_at,
        }

    def get_board_from_txt(self, txt_file: Path):
        is_mainboard = True
        self.mainboard = []
        self.sideboard = []
        with open(txt_file, 'r') as f:
            for line in f:
                if line in ['\n', '\r\n']:
                    is_mainboard = False
                else:
                    card_line = line.strip('\n').split(' ', 1)
                    if is_mainboard:
                        self.mainboard.append((card_line[0], card_line[1]))
                    else:
                        self.sideboard.append((card_line[0], card_line[1]))

    def to_txt(self, location):
        # filename = f"{location}/Deck-{self.name.replace(' ', '-')}.txt"
        filename = Path(location) / f"Deck-{self.name.replace(' ', '-')}.txt"
        with open(filename, 'w') as f:
            # Write mainboard
            for c in self.mainboard:
                f.write(' '.join(str(s) for s in c) + '\n')
            f.write('\n')  # write space between mainboard and sideboard
            # Write sideboard
            for c in self.sideboard:
                f.write(' '.join(str(s) for s in c) + '\n')

    def print(self):
        print(self.name or 'Unknown')
        for c in self.mainboard:
            print(f"{c[0]: <3} {c[1]}")
        print()
        print('Sideboard')
        for c in self.sideboard:
            print(f"{c[0]: <3} {c[1]}")
        print()
        if self.author:
            print(f"Author: {self.author}")
        if self.source:
            print(f"Source: {self.source}")
        if self.color:
            print(f"Color: {self.color}")
        if self.tags:
            print(f"Tags: {', '.join(self.tags)}")
        if self.created_at:
            print(f"Created: {self.created_at}")

    def mainboard_size(self):
        n = 0
        for c in self.mainboard:
            n += c[0]
        return n

    def sideboard_size(self):
        n = 0
        for c in self.sideboard:
            n += c[0]
        return n

    def get_price(self, currency: str = 'tix', card_db_path: Path = Path('data/db/card-db.json')):
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
        for card in self.mainboard:
            try:
                price = float(card_db[card[1]]['prices'][currency])
            except TypeError:
                price = 0
            mainboard_price += (card[0] * price)

        sideboard_price = 0
        for card in self.sideboard:
            try:
                price = float(card_db[card[1]]['prices'][currency])
            except TypeError:
                price = 0
            sideboard_price += (card[0] * price)

        decklist_price = mainboard_price + sideboard_price

        self.price = (decklist_price, mainboard_price, sideboard_price)
        self.price_currency = currency
        return self.price


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
    

if __name__ == '__main__':
    # Example deck
    deck1 = Deck(
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
        tags=['gruul', 'aggro'],
        author='me'
    )

    # Test basic Deck functions
    print('Print deck to dict')
    print(deck1.to_dict())
    print()

    print(f"Mainboard has {deck1.mainboard_size()} cards")
    print()

    # print(deck1.to_txt('.'))
    deck1.print()
    print()

    # Test organizing mainboard by card type
    print('Organizing mainboard by card type')
    print(mainboard_by_types(deck1, card_db_path=Path('../data/db/card-db.json')))
    print()

    # Test calculating deck price
    print('Calculate deck price')
    total_price, price_main, price_side = deck1.get_price('tix', card_db_path=Path('../data/db/card-db.json'))
    print(f"Mainboard: {price_main:.2f} | Sideboard: {price_side:.2f} | Total: {total_price:.2f} tix")
    print()
