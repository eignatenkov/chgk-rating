import numpy as np
import pandas as pd


def rolling_window(a, window):
    a = np.append(a, np.zeros(window - 1))
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)


def calculate_bonus_predictions(tournament_ratings, c=1):
    """
    produces array of bonuses based on the array of ratings of participants
    """
    tournament_ratings[::-1].sort()
    raw_preds = np.round(rolling_window(tournament_ratings, 15).dot(2.**np.arange(0, -15, -1)) * c)
    samesies = tournament_ratings[:-1] == tournament_ratings[1:]
    for ind in np.nonzero(samesies)[0]:
        raw_preds[ind + 1] = raw_preds[ind]
    return raw_preds


def calc_c(ratings):
    ratings[::-1].sort()
    return 2300 / ratings[:15].dot(2.**np.arange(0, -15, -1))


def calc_score_real(predicted_scores, positions):
    positions = positions - 1
    pos_counts = pd.Series(positions).value_counts().reset_index()
    pos_counts.columns = ['pos', 'n_teams']
    pos_counts['bonus'] = pos_counts.apply(
        lambda x: np.mean(predicted_scores[int(x.pos - (x.n_teams - 1) / 2) : int(x.pos + (x.n_teams - 1) / 2) + 1]), axis=1)
    return np.round(pos_counts.set_index('pos').loc[positions, 'bonus'].values)



