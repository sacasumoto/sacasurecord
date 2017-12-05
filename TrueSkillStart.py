import calcs as cs
import smash_rankings_calculator as src
import TournamentClass as tc
import time

def createRankingSTR(tournamentList,sigma,matchesmin):
    trueSkill = cs.Players()
    final = ''

    L = []
    for tournament in tournamentList:
        L.append((tournament.date,tournament))
    L.sort(key=lambda tup: tup[0])

    for tup in L:
        for player in tup[1].getEntrantList():
            if player not in trueSkill.table.keys():
                trueSkill.add_player(player)
        sets = tup[1].getSetTuple()
        for winner,loser in sets:
            trueSkill.rate_1vs1(winner,loser)
    final += trueSkill.get_trueskill_str(sigma,'all',matchesmin)
    return(final)

def createTrueSkillPlayerHistoryFromTournament(masterTournament,target):
    trueSkill = cs.Players()
    i = 0
    own = [[],[],[]]
    wins = [[],[],[]]
    loss = [[],[],[]]

    L = []
    for tournament in masterTournament.tournamentList:
        L.append((tournament.date,tournament))
    L.sort(key=lambda tup: tup[0])
    
    for tup in L:
        for player in tup[1].getEntrantList():
            if player not in trueSkill.table.keys():
                trueSkill.add_player(player)
        sets = tup[1].getSetTuple()
        for winner,loser in sets:
            if winner == target:
                own[0].append(trueSkill.table[target].Rating.mu)
                own[1].append(trueSkill.table[target].Rating.sigma)
                wins[0].append(trueSkill.table[loser].Rating.mu)
                wins[1].append(trueSkill.table[loser].Rating.sigma)
                i += 1
                own[2].append(i)
                wins[2].append(i)

            if loser == target:
                own[0].append(trueSkill.table[target].Rating.mu)
                own[1].append(trueSkill.table[target].Rating.sigma)
                loss[0].append(trueSkill.table[winner].Rating.mu)
                loss[1].append(trueSkill.table[winner].Rating.sigma)
                i += 1
                own[2].append(i)
                loss[2].append(i)


            
            trueSkill.rate_1vs1(winner,loser)
            
    return(own,wins,loss)
