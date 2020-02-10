import numpy as np
from collections import Counter

from release_procs.tools import calculate_bonus_predictions


def calc_rg(tournament_results, team_release, player_release):
    """
    mock function for now
    returns np.array of rgs
    """
    return np.array([int(t['tech_rating_rg']) for t in tournament_results])


def calc_bonus(tournament_df, coeff=0.5):
    """
    tournament_df should have columns: score_real, score_pred, n_leg
    6 ms for bb, kinda long
    """
    d_one = tournament_df.score_real - tournament_df.score_pred
    d_one[d_one < 0] *= 0.5
    d_two = 300 * np.exp((tournament_df.score_real - 2300) / 350)
    d = coeff * (d_one + d_two)
    d[(d > 0) & (tournament_df.n_legs > 2)] *= tournament_df.n_legs[(d > 0) & (tournament_df.n_legs > 2)]
    return d.astype('int')


def calculate_changes(team_release, player_release, tournament_results):
    """
    returns Counter({team_id: change}) based on the tournament results
    """
    rgs = calc_rg(tournament_results, team_release, player_release)
    bonus_predictions = calculate_bonus_predictions(rgs)

    return Counter()


def calculate_rating_release(team_release: Counter, player_release, tournaments):
    total_changes = Counter()
    for tournament in tournaments:
        total_changes += calculate_changes(team_release, player_release, tournament)
    return team_release + total_changes