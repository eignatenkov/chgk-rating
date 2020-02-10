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


def calc_q(rating_release, players_release):
    """
    Коэффициент Q вычисляется при релизе как среднее значение отношения рейтинга R к техническому
    рейтингу по базовому составу RB для команд, входящих в 100 лучших по последнему релизу
    (исключая те, которые получают в этом релизе стартовые рейтинги) и имеющих не менее шести
    игроков в базовом составе.
    """

    def calc_rb_raw(players_ratings):
        pr_sorted = players_ratings.sort_values(ascending=False)
        coeffs = np.zeros(pr_sorted.size)
        coeffs[:6] = (np.arange(6, 0, -1) / 6)[:coeffs.size]
        return np.round(pr_sorted.dot(coeffs))

    top_h = rating_release.iloc[:100].set_index('Ид')
    top_h_ids = set(top_h.index)
    rb_raws = players_release[players_release['ИД базовой команды'].isin(top_h_ids)].groupby('ИД базовой команды')['Рейтинг'].apply(calc_rb_raw)
    top_h = top_h.join(rb_raws, rsuffix='_raw')
    return (top_h['Рейтинг'] / top_h['Рейтинг_raw']).mean()


def calc_score_real(predicted_scores, positions):
    positions = positions - 1
    pos_counts = pd.Series(positions).value_counts().reset_index()
    pos_counts.columns = ['pos', 'n_teams']
    pos_counts['bonus'] = pos_counts.apply(
        lambda x: np.mean(predicted_scores[int(x.pos - (x.n_teams - 1) / 2) : int(x.pos + (x.n_teams - 1) / 2) + 1]), axis=1)
    return np.round(pos_counts.set_index('pos').loc[positions, 'bonus'].values)



