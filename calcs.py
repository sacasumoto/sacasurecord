import math
import operator
import os
import trueskill
from trueskill.backends import cdf
import scraping_functions as sf
import pandas as pd

trueskill.setup(draw_probability=0)


class Player:
    def __init__(self):
        self.Rating = trueskill.Rating()
        self.match_count = 0
        self.win_count = 0
        self.loss_count = 0
        self.win_list = []
        self.loss_list = []

    def get_rating(self):
        return self.Rating.mu, self.Rating.sigma

    def add_match(self):
        self.match_count += 1

    def get_match_count(self):
        return self.match_count

    def add_win(self,other):
        self.win_count += 1
        self.win_list.append(other)

    def add_loss(self,other):
        self.loss_count += 1
        self.loss_list.append(other)
    def get_record(self):
        return(self.win_count,self.loss_count,self.win_list,self.loss_list)
    def get_win_mu_sig_avg(self,Players):
        L = self.get_record()[2]
        if len(L) != 0:
            m = 0
            s = 0
            for player in L:
                m += Players.table[player].Rating.mu
                s += Players.table[player].Rating.sigma
            m = m/len(L)
            s = s/len(L)
            return([m,s])
        else:
            return([None,None])

        
    def get_loss_mu_sig_avg(self,Players):
        L = self.get_record()[3]
        if len(L) != 0:
            m = 0
            s = 0
            for player in L:
                m += Players.table[player].Rating.mu
                s += Players.table[player].Rating.sigma
            m = m/len(L)
            s = s/len(L)
            return([m,s])
        else:
            return([None,None])

class Players:
    def __init__(self):
        self.table = {}

    def add_player(self, name):
        self.table[name] = Player()

    def check_player(self, name):
        try:
            self.table[name]
        except KeyError:
            self.add_player(name)

    def rate_1vs1(self, winner, loser):
        self.check_player(winner)
        self.check_player(loser)
        self.table[winner].add_win(loser)
        self.table[loser].add_loss(winner)

        self.table[winner].Rating, self.table[loser].Rating = \
            trueskill.rate_1vs1(self.table[winner].Rating, self.table[loser].Rating)

        self.add_matches([winner, loser])
        
    def add_matches(self, players):
        for player in players:
            self.table[player].add_match()

    def win_stdev(self, player, opp=None):
        player_rating = self.table[player].Rating
        if not opp:
            opp_rating = trueskill.Rating()
        else:
            opp_rating = self.table[opp].Rating

        delta_mu = player_rating.mu - opp_rating.mu
        rsss = math.sqrt(player_rating.sigma**2 + opp_rating.sigma**2)
        return delta_mu/rsss

    def win_pct(self, player, opp=None):
        return cdf(self.win_stdev(player, opp))

    def calculate_ratings(self, filename):
        with open(filename, "r") as match_file:
            for line in match_file:
                winner, loser = line.strip().split(",")
                self.rate_1vs1(winner.title(), loser.title())

    def get_trueskill_pct(self,sigma,top,matchesmin):
        pct_table = {}
        for player in self.table:
            pct_table[player] = self.rate_player(player,sigma)
        ordered_table = sorted(pct_table.items(), key=operator.itemgetter(1), reverse=True)
        i = 0
        final = ''
        for pair in ordered_table:
            
            player_rating = self.table[pair[0]].Rating
            num_matches = self.table[pair[0]].get_match_count()
            if top == 'all':
                if num_matches >= matchesmin:
                    final += ('{}\t{}\t{}\t{}\t{}\n'.format(pair[0], format_score(pair[1]),
                                                            format_score(player_rating.mu),
                                                            format_score(player_rating.sigma),
                                                            num_matches))   
            else:
                if num_matches >= matchesmin and i < top and top < len(ordered_table):               
                    i += 1
                    final += ('{}\t{}\t{}\t{}\t{}\n'.format(pair[0], format_score(pair[1]),
                                                            format_score(player_rating.mu),
                                                            format_score(player_rating.sigma), num_matches))
                
        return(final)

    def get_trueskill_str(self,sigma,top,matchesmin):
        pct_table = {}
        for player in self.table:
            pct_table[player] = self.rate_player(player,sigma)
        ordered_table = sorted(pct_table.items(), key=operator.itemgetter(1), reverse=True)
        i = 0
        final = '{:<5}\t{:<30}\t{:<15}\t{:<15}\t{:<15}\t{:<15}\n'.format('Rank:','Name:','Score:','Mu:','Sigma:','Matches:')
        for pair in ordered_table:
            player_rating = self.table[pair[0]].Rating
            num_matches = self.table[pair[0]].get_match_count()
            if top == 'all':
                if num_matches >= matchesmin:
                    i += 1
                    final += '{:<5}\t{:<30}\t{:<15}\t{:<15}\t{:<15}\t{:<15}\n'.format(i,pair[0], format_score(pair[1]),
                                                            format_score(player_rating.mu),
                                                            format_score(player_rating.sigma),
                                                            num_matches)  
            else:
                if num_matches >= matchesmin and i < top and top < len(ordered_table):               
                    i += 1
                    final += '{:<5}\t{:<30}\t{:<15}\t{:<15}\t{:<15}\t{:<15}\n'.format(i,pair[0], format_score(pair[1]),
                                                            format_score(player_rating.mu),
                                                            format_score(player_rating.sigma),
                                                            num_matches)
        return(final)



    def rate_player(self, player,sigma):
        p_rating = self.table[player].Rating
        return p_rating.mu -  sigma*p_rating.sigma

    #I want Score,Mu,Sigma,win pct,Matches
    
    def create_panda(self,sigma,matchesmin):
        pct_table = {}
        for player in self.table:
            pct_table[player] = self.rate_player(player,sigma)
        ordered_table = sorted(pct_table.items(), key=operator.itemgetter(1), reverse=True)
        i = 0
        D = {'Rank':[],'Name':[],'Score':[],'Mu':[],'Sigma':[],'Matches':[]}
        for pair in ordered_table:
            player_rating = self.table[pair[0]].Rating
            num_matches = self.table[pair[0]].get_match_count()
            if num_matches >= matchesmin:
                i += 1
                D['Rank'].append(i)
                D['Name'].append(pair[0])
                D['Score'].append(format_score(pair[1]))
                D['Mu'].append(format_score(player_rating.mu)),
                D['Sigma'].append(format_score(player_rating.sigma))
                D['Matches'].append(num_matches)
        df = pd.DataFrame(D)
        return(df.set_index('Name'))

def format_score(score):
    return round(score, 6)


game_dict = {}
for game in sf.get_valid_games():
    game_dict[game] = Players()


def process_rankings(tournament, game):
    tournament_file = sf.get_filename(game + "Results/", tournament)
    with open(tournament_file, mode="r", encoding="ISO-8859-1") as tournament:
        for match in tournament:
            winner, loser = match.split(",")
            game_dict[game].rate_1vs1(winner, loser)


def show_rankings(game, number=100, format="human"):
    game_dict[game].get_trueskill_pct()


def process_game_by_date(game):
    """Run Glicko2 ranking process for a single game in batches, with tournaments between dates processed in the same
    batch."""
    print("Processing " + game + "...")
    date_file, url_folder, result_folder = sf.get_game_folders(game)
    with open(date_file, 'r', encoding="ISO-8859-1") as f:
        content = f.readlines()
        for line in content:
            line = line.strip()
            is_date = sf.check_if_date(line)
            if not is_date:
                if not os.path.isfile(sf.get_filename(result_folder, line)):
                    sf.scrape_tournament_by_game(game, line)
                process_rankings(line, game)


def process_all_games():
    """Run Glicko2 ranking process for all games"""
    for game in sf.get_valid_games():
        try:
            process_game_by_date(game)
        except FileNotFoundError:
            print("Processing files not found for " + game)

##
##if __name__ == "__main__":
##    ranking = Players()
##    ranking.calculate_ratings("matches.txt")
##    ranking.get_trueskill_pct()
