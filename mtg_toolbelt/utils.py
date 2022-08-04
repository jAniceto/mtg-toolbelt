"""
General utilities
"""

import json
from pathlib import Path


# List of color family names
FAMILIES = [
    'white', 'blue', 'black', 'red', 'green', 'selesnya', 'orzhov', 'boros', 'azorius', 'dimir', 'rakdos', 'golgari',
    'izzet', 'simic', 'gruul', 'naya', 'esper', 'grixis', 'jund', 'bant', 'abzan', 'temur', 'jeskai', 'mardu', 'sultai',
    'glint', 'dune', 'ink', 'whitch', 'yore', 'domain', 'colorless'
]


# Dictionary to convert deck family to a list of color codes
COLORS = dict(white=['w'], blue=['u'], black=['b'], red=['r'], green=['g'], selesnya=['w', 'g'],
              orzhov=['w', 'b'], boros=['w', 'r'], azorius=['w', 'u'], dimir=['u', 'b'],
              rakdos=['b', 'r'], golgari=['b', 'g'], izzet=['u', 'r'], simic=['u', 'g'],
              gruul=['r', 'g'], naya=['w', 'r', 'g'], esper=['w', 'u', 'b'], grixis=['u', 'b', 'r'],
              jund=['b', 'r', 'g'], bant=['w', 'u', 'g'], abzan=['w', 'b', 'g'],
              temur=['u', 'r', 'g'], jeskai=['w', 'u', 'r'], mardu=['w', 'b', 'r'],
              sultai=['u', 'b', 'g'], glint=['u', 'b', 'r', 'g'], dune=['w', 'b', 'r', 'g'],
              ink=['w', 'u', 'r', 'g'], whitch=['w', 'u', 'b', 'g'], yore=['w', 'u', 'b', 'r'],
              domain=['w', 'u', 'b', 'r', 'g'], colorless=['c'])


def load_config():
    """Load configuration file."""
    with open('config.json', 'r') as f:
        config = json.load(f)
        return config


def setup_dir(dir_name):
    """Create directory if it doesn't exist."""
    dir_path = Path(dir_name)
    dir_path.mkdir(parents=True, exist_ok=True)
