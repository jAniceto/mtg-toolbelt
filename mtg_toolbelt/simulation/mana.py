import csv
from dataclasses import dataclass
import random


# Options
MIN_LANDS = 2  # minimum number of lands in starting hand to keep hand. If less, mulligan hand
MAX_LANDS = 5  # maximum number of lands in starting hand to keep hand. If more, mulligan hand


@dataclass
class Deck:
    n_cards: int  # number of cards in deck
    n_lands: int  # number of lands in deck
    n_desired_lands: int  # number of lands of desired type

    def draw(self):
        """Draw a (random) card

        RETURNS:
            card_type : int
                Type of card drawn:
                1 -> land of the desired type
                2 -> land (not of the desired type)
                3 -> non land card
        """
        n = random.randint(1, self.n_cards)
        # card_type = 0
        desired_land_cutoff = self.n_desired_lands
        land_cutoff = self.n_lands

        # If a land of the desired type is drawn
        if n <= desired_land_cutoff:
            card_type = 1
            self.n_desired_lands -= 1
            self.n_lands -= 1
            self.n_cards -= 1

        # If any land is drawn
        elif (n > desired_land_cutoff) and (n <= land_cutoff):
            card_type = 2
            self.n_lands -= 1
            self.n_cards -= 1

        # If non-land card is drawn
        elif n > land_cutoff:
            card_type = 3
            self.n_cards -= 1

        return card_type


def simulate(deck_size=None, n_lands=None, n_desired_lands=None, turns=None, on_play=True, consider_mulligans=True,
             iterations=100000):
    """Magic the Gathering draw simulation to evaluate probability of drawing a certain number of lands.

    Runs many simulations of a MtG game draw for a certain amount of turns.
    Never mulligans below 4 cards.

    ARGUMENTS:
        deck_size : int
            Number of cards in the deck.
        n_lands : int
            Total number of lands.
        n_desired_lands : int
            Number of lands of desired type.
        turns : int
            Run the draw simulation for this number of turns. For instance, if turns=3, it simulates
            the draw of the opening hand and the first three turns, i.e., draws 7 + 2 cards (considers
            the player is on the play).
        on_play : bool
            Whether the player is on the play (True) or on the draw (False).
        consider_mulligans : bool
            Whether to consider the possibility of mulliganing bad hands. Must set MIN_LANDS and MAX_LANDS
            variables.
        iterations : int
            Repeat the simulation this number of times.
    """
    # Print simulation conditions
    print(
        f"Simulation conditions: {deck_size} card deck | {n_lands} lands | {n_desired_lands} desired lands | {'on the play' if on_play else 'on the draw'} | run for {turns} turns {'with' if consider_mulligans else 'without'} mulligan")

    count_games_desired = 0  # number of games where you draw enough lands and the right colored sources
    count_games_any = 0  # number of relevant games where you draw enough lands

    for i in range(iterations):
        # Initialize deck
        deck = Deck(n_cards=deck_size, n_lands=n_lands, n_desired_lands=n_desired_lands)

        # Draw opening hand (7 cards)
        lands_hand = 0  # total amount of lands in your hand
        desired_lands_hand = 0  # number of lands that can produce the right color in your hand
        for _ in range(7):
            card_type = deck.draw()
            if card_type < 3:
                lands_hand += 1
            if card_type == 1:
                desired_lands_hand += 1

        # Whether to account for the possibility of mulligans
        if consider_mulligans:
            mull6, mull5, mull4 = 0, 0, 0
            # Check whether to mulligan
            if (lands_hand < MIN_LANDS) or (lands_hand > MAX_LANDS):
                mulligan = True
            else:
                mulligan = False

            # Mulligan to 6
            if mulligan:
                mull6 += 1
                deck = Deck(n_cards=deck_size, n_lands=n_lands, n_desired_lands=n_desired_lands)
                lands_hand = 0
                desired_lands_hand = 0
                for _ in range(7):
                    card_type = deck.draw()
                    if card_type < 3:
                        lands_hand += 1
                    if card_type == 1:
                        desired_lands_hand += 1

                # Check whether to mulligan
                if (lands_hand < MIN_LANDS) or (lands_hand > MAX_LANDS):
                    mulligan = True
                else:
                    mulligan = False
                    deck.n_cards += 1  # return 1 non-land card to deck

            # Mulligan to 5
            if mulligan:
                mull5 += 1
                deck = Deck(n_cards=deck_size, n_lands=n_lands, n_desired_lands=n_desired_lands)
                lands_hand = 0
                desired_lands_hand = 0
                for _ in range(7):
                    card_type = deck.draw()
                    if card_type < 3:
                        lands_hand += 1
                    if card_type == 1:
                        desired_lands_hand += 1

                # Check whether to mulligan
                if (lands_hand < MIN_LANDS) or (lands_hand > MAX_LANDS):
                    mulligan = True
                else:
                    mulligan = False
                    deck.n_cards += 2  # return 2 non-land card to deck

            # Mulligan to 4
            if mulligan:
                mull4 += 1
                deck = Deck(n_cards=deck_size, n_lands=n_lands, n_desired_lands=n_desired_lands)
                lands_hand = 0
                desired_lands_hand = 0
                for _ in range(7):
                    card_type = deck.draw()
                    if card_type < 3:
                        lands_hand += 1
                    if card_type == 1:
                        desired_lands_hand += 1

                # Stop mulliganing
                mulligan = False
                deck.n_cards += 3  # return 3 non-land card to deck

        # Draw step for turn 2 onwards
        if on_play:
            first_draw_turn = 2
        else:
            first_draw_turn = 1

        for t in range(first_draw_turn, turns + 1):
            card_type = deck.draw()
            if card_type < 3:
                lands_hand += 1
            if card_type == 1:
                desired_lands_hand += 1

        # Count iterations where enough lands or desired lands are found
        if desired_lands_hand >= turns:
            count_games_desired += 1
        if lands_hand >= turns:
            count_games_any += 1

    # Print results of N iterations
    prob_desired = count_games_desired / iterations
    prob_any = count_games_any / iterations
    print(f" - Results after {iterations} iterations: Prob good mana curve = {prob_desired}")

    sim_results = {
        'in': {
            'deck_size': deck_size,
            'n_lands': n_lands,
            'n_desired_lands': n_desired_lands,
            'turns': turns,
            'on_play': on_play,
            'consider_mulligans': consider_mulligans,
            'iterations': iterations
        },
        'out': {
            'prob_desired_land': prob_desired,
            'prob_any_land': prob_any,
            'count_games_desired': count_games_desired,
            'count_games_any': count_games_any,
            'no_mulligan': iterations - ((mull6 - mull5 - mull4) + (mull5 - mull4) + mull4),
            'mulligans_to_6': mull6 - mull5 - mull4,
            'mulligans_to_5': mull5 - mull4,
            'mulligans_to_4': mull4
        }
    }

    return sim_results


def mana_curve_table(sim_path, n_lands_range=[], deck_size=60, turns=5, on_play=True, consider_mulligans=True, iterations=100000):
    """Calculate the probability to find at least a certain number of lands after a certain
    number of draw steps. Meaning hitting X lands by turn X.
    """
    prob_table = []
    for n_lands in range(n_lands_range[0], n_lands_range[1] + 1):
        row = []
        for t in range(2, turns + 1):
            results = simulate(
                deck_size=deck_size,
                n_lands=n_lands,
                n_desired_lands=n_lands,
                turns=t,
                on_play=on_play,
                consider_mulligans=consider_mulligans,
                iterations=iterations
            )
            row.append(results['out']['prob_desired_land'])
        prob_table.append(row)

    # Save to CSV
    mana_table_path = sim_path / 'mana_sim.csv'
    with open(mana_table_path, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerows(prob_table)

    return prob_table


if __name__ == '__main__':
    # simulate(deck_size=60, n_lands=20, n_desired_lands=20, turns=5, consider_mulligans=True, iterations=100000)

    mana_curve_table(n_lands_range=[16, 26], deck_size=60, turns=7, on_play=False, consider_mulligans=True, iterations=10000)
