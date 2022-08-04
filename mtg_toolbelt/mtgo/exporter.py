"""
Script to automate exporting MTGO decks to file.
Automates the mouse and keyboard movement required to export decks from MTGO.
Organizes decks into folters

Notes:
- You must have MTGO client open.
- You must be on the Collection page.
- You must select the first deck to export.
- Only decks in the selected deck category are exported.
- You can not change windows while the script is running.
"""

from typing import List
import sys
from pathlib import Path
import pyautogui
import pyperclip
from tqdm import tqdm
from mtg_toolbelt.utils import setup_dir


def focus_mtgo_window():
    """Focus the MTGO window by clicking the title bar (top)"""
    pyautogui.click(338, 9, button='left')


def auto_export(filepath):
    pyautogui.PAUSE = 0.5
    pyautogui.FAILSAFE = True

    # Check if first deck is selected
    prep = input('Have you selected the first deck you want to export? ([y]/n): ')
    if prep not in ['', 'y', 'yes', 'Y', 'Yes']:
        sys.exit('Please select the first deck you want to export and run the script again.')

    # How many decks to save
    decks_to_save = input('How many decks would you like to export? (320): ')
    if decks_to_save == '':
        deck_number = 320
    else:
        try:
            deck_number = int(decks_to_save)
        except ValueError:
            sys.exit('Please enter an integer number or leave blank to use the default value.')

    print('Initiating exporting.\nMove the mouse to the upper-left corner to cancel.')

    # Focus MTGO window
    focus_mtgo_window()

    # Scroll over decks and export
    with tqdm(total=deck_number) as pbar:
        deck_count = 1
        while True:
            pbar.update()

            # Press context menu key
            pyautogui.hotkey('shift', 'f10')

            # Use keyboard to select Export from the context menu
            pyautogui.typewrite(['down', 'down', 'down', 'down', 'enter'])

            # Use keyboard to select path
            if filepath:
                pyautogui.press('left')
                pyperclip.copy(filepath)
                pyautogui.hotkey("ctrl", "v")

            # Use keyboard to select file type and save
            pyautogui.typewrite(['tab', 'down', 'down', 'enter', 'enter'])

            # End job
            if deck_count == deck_number:
                break

            # Focus MTGO window
            focus_mtgo_window()

            # Press down to go to next deck
            pyautogui.press('down')

            deck_count += 1


def clean_file_names(filepath, chars_to_strip):
    """
    Clean deck filenames.
    """
    folder_path = filepath.parent  # path to folder
    filename = filepath.stem  # file name without extension

    for char in chars_to_strip:
        filename = filename.strip().strip('!').replace(char, '').strip()
    new_filename = filename + '.txt'
    new_filepath = folder_path / new_filename

    if filepath != new_filepath:
        try:
            filepath.rename(new_filepath)
        except FileExistsError:
            print(f"File already exists: {new_filepath}")


def organize(decks_path: Path, strip_chars: List[str] = None, banlist: List[str] = None):
    """Manage exported decks.
    The following actions are taken:
        - clean up deck file names by removing prefixes ands suffixes
        - separate decks with banned cards from valid decks (sorts into two folders)
    """
    if strip_chars is None:
        strip_chars = ['#T1 ', '#T2 ', '.txt']

    deck_files = [f for f in decks_path.iterdir() if f.is_file() and str(f).endswith('.txt')]

    # Clean deck names
    for deck_file in deck_files:
        clean_file_names(deck_file, strip_chars)

    # Separate decks with banned cards from valid decks (sorts into two folders)
    if banlist:
        deck_files = [f for f in decks_path.iterdir() if f.is_file() and str(f).endswith('.txt')]  # required again because deck names have been cleaned
        banned_dir_path = decks_path / 'banned'
        ready_dir_path = decks_path / 'valid'

        # Create Banned and Ready dirs if needed
        setup_dir(banned_dir_path)
        setup_dir(ready_dir_path)
        # if not banned_dir_path.exists():
        #     banned_dir_path.mkdir()
        # if not ready_dir_path.exists():
        #     ready_dir_path.mkdir()

        # Move deck files to appropriate folder
        for deck_file in deck_files:
            with open(deck_file, 'r') as f:
                data = f.read()

            if any(card in data for card in banlist):
                deck_file.rename(decks_path / 'banned' / deck_file.name)
            else:
                deck_file.rename(decks_path / 'valid' / deck_file.name)


if __name__ == '__main__':
    decks_path_ = Path('../../data/mtgo-decks')
    setup_dir(decks_path_)
    auto_export(decks_path_)
    organize(decks_path_, strip_chars=None, banlist=None)
