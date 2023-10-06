import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import List, Tuple, Optional
from mtg_toolbelt.scryfall import get_best_price


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
    mainboard_price: Optional[float] = None
    sideboard_price: Optional[float] = None
    price: Optional[float] = None

    def __post_init__(self):
        """If creating a new deck object, add a creation date."""
        if not self.created_at:
            self.created_at = date.today().strftime("%Y/%m/%d")

    def to_dict(self):
        """Deck object to dictionary."""
        return self.__dict__

    def to_dict_for_edit(self):
        """Deck object to a simple dictionary for editing deck info."""
        return {
            "name": self.name,
            "color": self.color,
            "tags": self.tags,
            "author": self.author,
            "source": self.source,
            "created_at": self.created_at,
        }

    def get_decklist_from_txt(self, txt_file: Path):
        """Load decklist from a txt of the following type. Sideboard after a black line.
        Example .txt:
            10 Forest
            4 Rancor
            ...
            1 Young Wolf

            4 Relic of Progenitus
        """
        is_mainboard = True
        self.mainboard = []
        self.sideboard = []
        with open(txt_file, 'r', encoding="utf-8") as f:
            for line in f:
                if line in ['\n', '\r\n']:
                    is_mainboard = False
                else:
                    card_line = line.strip('\n').split(' ', 1)
                    if is_mainboard:
                        self.mainboard.append((int(card_line[0]), card_line[1]))
                    else:
                        self.sideboard.append((int(card_line[0]), card_line[1]))

    def to_txt(self, location):
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

    def get_price(self, currency: str = 'tix'):
        # Calculate prices
        self.mainboard_price = 0
        for card in self.mainboard:
            price = get_best_price(card[1], currency=currency)
            self.mainboard_price += card[0] * price

        self.sideboard_price = 0
        for card in self.sideboard:
            price = get_best_price(card[1], currency=currency)
            self.sideboard_price += card[0] * price

        self.price = self.mainboard_price + self.sideboard_price
        return self.price, self.mainboard_price, self.sideboard_price


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
            (4, 'Basilisk Gate'),
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

    # print(deck1.to_txt('.'))
    deck1.print()
    print()

    # Test organizing mainboard by card type
    print('Organizing mainboard by card type')
    print(mainboard_by_types(deck1, card_db_path=Path('../data/db/card-db.json')))
    print()

    # Test calculating deck price
    print('Calculate deck price')
    total_price, price_main, price_side = deck1.get_price(currency='tix')
    print(f"Mainboard: {price_main:.2f} | Sideboard: {price_side:.2f} | Total: {total_price:.2f} tix")
    print()
