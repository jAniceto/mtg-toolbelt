from typing import List, Dict


def get_card_counts(decks: List[Dict], board: str = 'mainboard', rank: str = 'total_count'):
    """Given a list of Deck objects, get card frequencies.
    total_count gives the total number of times a card appears in all decks.
    unique_count gives the number of decks in which the card appeared.
    """
    if board not in ['mainboard', 'sideboard']:
        raise ValueError('board must be either mainboard or sideboard.')
    if rank not in ['total_count', 'unique_count']:
        raise ValueError('rank must be either total_count or unique_count')

    card_freq = dict()
    for deck in decks:
        for card in deck[board]:
            if card[1] in card_freq:
                card_freq[card[1]]['total_count'] += card[0]
                card_freq[card[1]]['unique_count'] += 1
            else:
                card_freq[card[1]] = {
                    'total_count': card[0],
                    'unique_count': 1,
                }

    sorted_card_freq = {k: v for k, v in sorted(card_freq.items(), key=lambda item: item[1][rank], reverse=True)}

    return sorted_card_freq


if __name__ == '__main__':
    import json
    from pathlib import Path

    standings_path = Path('../../data') / 'metagame' / 'standings.json'
    with open(standings_path, 'r') as f:
        standings_dict = json.load(f)
        decks = standings_dict['data']

    card_rank = get_card_counts(decks)

