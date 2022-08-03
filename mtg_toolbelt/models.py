from dataclasses import dataclass, field, asdict
from datetime import date
from typing import List, Tuple, Optional
from pathlib import Path


@dataclass
class Deck:
    mainboard: List[Tuple]
    sideboard: Optional[List[Tuple]] = None
    name: Optional[str] = None
    color: Optional[str] = None
    tags: Optional[List[str]] = None
    author: Optional[str] = None
    source: Optional[str] = None
    created_at: Optional[str] = None

    def __post_init__(self):
        self.created_at = date.today().strftime("%Y/%m/%d")

    def to_dict(self):
        # return asdict(self)
        return self.__dict__

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


if __name__ == '__main__':
    deck = Deck(
        mainboard=[
            (1, 'Rancor'),
            (10, 'Forest')
        ],
        sideboard=[
            (2, 'Relic of Progenitus'),
        ],
        name='Test Deck',
        color='gruul',
        tags=['gruul', 'gruul'],
        author='me'
    )

    print(deck.to_dict())
    print(deck.mainboard_size())
    # print(deck.to_txt('.'))
    deck.print()
