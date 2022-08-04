from datetime import datetime, timedelta
import json
from typing import List
from bs4 import BeautifulSoup
from pathlib import Path
import requests
from tqdm import tqdm
from mtg_toolbelt.models import Deck


def scrape_decklists(start_date_str, end_date_str, format_, metagame_path):
    """
    Program which allows retrieval of decks from any format from MTGO, using a set start and end date in a
    YYYY-MM-DD format and a format_ (standard, modern, legacy, pauper, pioneer, vintage).
    """
    # Convert start and end dates into Date objects, as well as assign interval for checking
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    meta_delta = end_date - start_date
    delta = timedelta(days=1)

    # Create a request list with each possible instance leagues/challenges of the chosen format for each day
    requests_list = []
    while start_date <= end_date:
        requests_list.append(
            'https://magic.wizards.com/en/articles/archive/mtgo-standings/' + format_ + '-league-' + start_date.strftime('%Y-%m-%d'))
        requests_list.append(
            'https://magic.wizards.com/en/articles/archive/mtgo-standings/' + format_ + '-challenge-' + start_date.strftime('%Y-%m-%d'))
        start_date += delta

    # Iterate through each possible URL
    decks = []
    for website in tqdm(requests_list):
        # Request each URL, translate into a parsable format, and filter all individual instances of decklists.
        mtg_page = requests.get(website)
        mtg_soup = BeautifulSoup(mtg_page.content, "html.parser")
        deck_divs = mtg_soup.find_all('div', class_='deck-group')

        if deck_divs:
            # For each deck div
            for deck_div in deck_divs:
                mainboard_div = deck_div.find_all('div', class_='sorted-by-overview-container sortedContainer')[0]
                sideboard_div = deck_div.find_all('div', class_='sorted-by-sideboard-container clearfix element')[0]
                author = deck_div.find('span', class_='deck-meta').h4.text
                source = website

                # Mainboard
                card_counts = []
                card_names = []
                # For each card count and name
                for ccount in mainboard_div.find_all('span', class_='card-count'):
                    card_counts.append(int(ccount.contents[0]))
                for cname in mainboard_div.find_all('a', class_='deck-list-link'):
                    card_names.append(cname.contents[0])

                mainboard = []
                for card_qty, card_name in zip(card_counts, card_names):
                    mainboard.append(
                        (card_qty, card_name)
                    )

                # Sideboard
                card_counts = []
                card_names = []
                # For each card count and name
                for ccount in sideboard_div.find_all('span', class_='card-count'):
                    card_counts.append(int(ccount.contents[0]))
                for cname in sideboard_div.find_all('a', class_='deck-list-link'):
                    card_names.append(cname.contents[0])

                sideboard = []
                for card_qty, card_name in zip(card_counts, card_names):
                    sideboard.append(
                        (card_qty, card_name)
                    )

                # Create deck instance
                d = Deck(
                    mainboard=mainboard,
                    sideboard=sideboard,
                    author=author,
                    source=source
                )
                decks.append(d)

    # Save standings
    standings_dict = {
        'format': format_,
        'start_date': start_date_str,
        'end_date': end_date_str,
    }

    deck_dict = []
    for deck in decks:
        deck_dict.append(deck.to_dict())
    standings_dict['decks'] = deck_dict
    standings_dict['n_decks'] = len(deck_dict)

    standings_path = metagame_path / 'standings.json'
    with open(standings_path, 'w') as f:
        json.dump(standings_dict, f)

    # Log
    print(f"{format_.upper()} format standings.")
    print(f"Found {len(deck_dict)} decks in the period {start_date_str} - {end_date_str} ({meta_delta.days} days).")
    print(f"Standings JSON saved to {str(standings_path)}.")

    return decks


if __name__ == '__main__':
    standings_path_ = Path('../../data/metagame')
    res = scrape_decklists('2022-07-25', '2022-08-03', 'pauper', standings_path_)
    print(res[1].print())
