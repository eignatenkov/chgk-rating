from rating_api.tournaments import get_tournament_results
from release_procs.tools import calc_tech_rating
import pandas as pd
import numpy as np


class Tournament:
    def __init__(self, tournament_id):
        raw_results = get_tournament_results(tournament_id, recaps=True)
        self.data = pd.DataFrame([
            {
                'team_id': t['team']['id'],
                'name': t['team']['name'],
                'current_name': t['current']['name'],
                'questionsTotal': t['questionsTotal'],
                'position': t['position'],
                'n_base': sum(player['flag'] in {'Б', 'К'} for player in t['teamMembers']),
                'teamMembers': [x['player']['id'] for x in t['teamMembers']]
            } for t in raw_results if t['position'] != 9999
        ])
        self.data['heredity'] = (self.data.n_base > 3) | (self.data.n_base == 3) & \
                                (self.data.name == self.data.current_name)

    @staticmethod
    def calc_rt(player_ids, player_rating, q):
        """
        вычисляет тех рейтинг по фактическому составу команды
        """
        prs = player_rating.data.rating.reindex(player_ids).fillna(0).values
        return calc_tech_rating(prs, q)

    def add_ratings(self, team_rating, player_rating):
        self.data['rt'] = self.data.teamMembers.map(lambda x: self.calc_rt(x, player_rating, team_rating.q))
        self.data['r'] = np.where(self.data.heredity, self.data.team_id.map(team_rating.get_team_rating), 0)
        self.data['rb'] = np.where(self.data.heredity, self.data.team_id.map(team_rating.get_trb), 0)
        self.data['rg'] = np.where(self.data.rb, self.data.r * self.data.rt / self.data.rb, self.data.rt)
        self.data['rg'] = np.where(self.data.rt < self.data.rb, np.maximum(self.data.rg, 0.5 * self.data.r),
                                   np.minimum(self.data.rg, np.maximum(self.data.r, self.data.rt)))
