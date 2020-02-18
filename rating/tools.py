import numpy as np
import pandas as pd


def rolling_window(a, window):
    a = np.append(a, np.zeros(window - 1))
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)


def calc_tech_rating(players_ratings, q=None):
    players_ratings[::-1].sort()
    coeffs = np.zeros(players_ratings.size)
    coeffs[:6] = (np.arange(6,0, -1) / 6)[:coeffs.size]
    tech_rating = np.round(players_ratings.dot(coeffs))
    if q is not None:
        tech_rating *= q
    return tech_rating


def calc_score_real(predicted_scores, positions):
    positions = positions - 1
    pos_counts = pd.Series(positions).value_counts().reset_index()
    pos_counts.columns = ['pos', 'n_teams']
    pos_counts['bonus'] = pos_counts.apply(
        lambda x: np.mean(predicted_scores[int(x.pos - (x.n_teams - 1) / 2) : int(x.pos + (x.n_teams - 1) / 2) + 1]), axis=1)
    return np.round(pos_counts.set_index('pos').loc[positions, 'bonus'].values)


def calc_bonus(score_real, score_pred, n_legs, coeff=0.5):
    """
    tournament_df should have columns: score_real, score_pred, n_leg
    6 ms for bb, kinda long
    """
    d_one = score_real - score_pred
    d_one[d_one < 0] *= 0.5
    d_two = 300 * np.exp((score_real - 2300) / 350)
    d = coeff * (d_one + d_two)
    d[(d > 0) & (n_legs > 2)] *= n_legs[(d > 0) & (n_legs > 2)]
    return d.astype('int')