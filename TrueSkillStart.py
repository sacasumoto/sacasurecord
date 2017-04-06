import calcs as cs
import smash_rankings_calculator as src
import TournamentClass as tc
import time

#List of Tournament class
def importTournamentDictFromFile(filename):
    file = open(filename,'r')
    L = file.readlines()
    tournamentList = []
    for D in L:
        tournamentList.append(tc.Tournament(0,'Loading',**eval(D)))
    return(tournamentList)

def createRankingTSV(filename,sigma,top,matchesmin):
    final = ''
    header = 'Name:\tScore:\tMu:\tSigma:\tMatches:\n'
    final += header
    final += trueSkill.get_trueskill_pct(sigma,top,matchesmin)
    file = open(filename,'w')
    file.write(final)
    file.close()
def createRankingSTR(tournamentlist,sigma,matchesmin):
    trueSkill = cs.Players()
    final = ''
    for tournament in tournamentlist:
        for player in tournament.getEntrantList():
            if player not in trueSkill.table.keys():
                trueSkill.add_player(player)
        sets = tournament.getSetTuple()
        for winner,loser in sets:
            trueSkill.rate_1vs1(winner,loser)
    final += trueSkill.get_trueskill_str(sigma,'all',matchesmin)
    return(final)
def createTrueSkillPlayersAndMasterTournamentFromFile(filename):
    masterTournament = tc.MasterTournament([]);masterTournament.loadFromFile(filename)
    trueSkill = cs.Players()
    for tournament in masterTournament.tournamentList:
        for player in tournament.getEntrantList():
            if player not in trueSkill.table.keys():
                trueSkill.add_player(player)
        sets = tournament.getSetTuple()
        for winner,loser in sets:
            trueSkill.rate_1vs1(winner,loser)
    return(trueSkill,masterTournament)

def createTrueSkillPlayerHistoryFromFile(filename,target):
    masterTournament = tc.MasterTournament([]);masterTournament.loadFromFile(filename)
    trueSkill = cs.Players()
    i = 0
    own = [[],[],[]]
    wins = [[],[],[]]
    loss = [[],[],[]]
    for tournament in masterTournament.tournamentList:
        for player in tournament.getEntrantList():
            if player not in trueSkill.table.keys():
                trueSkill.add_player(player)
        sets = tournament.getSetTuple()
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

def createTrueSkillPlayerHistoryFromTournament(masterTournament,target):
    trueSkill = cs.Players()
    i = 0
    own = [[],[],[]]
    wins = [[],[],[]]
    loss = [[],[],[]]
    for tournament in masterTournament.tournamentList:
        for player in tournament.getEntrantList():
            if player not in trueSkill.table.keys():
                trueSkill.add_player(player)
        sets = tournament.getSetTuple()
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


def createTrueSkillHistoryFromFile(filename):
    masterTournament = tc.MasterTournament([]);masterTournament.loadFromFile(filename)
    trueSkill = cs.Players()
    i = 0
    won = [[],[],[],[],[],[],[],[],[],[],[],[]]
    lost = [[],[],[],[],[],[],[],[],[],[],[],[]]
    for tournament in masterTournament.tournamentList:
        for player in tournament.getEntrantList():
            if player not in trueSkill.table.keys():
                trueSkill.add_player(player)
        sets = tournament.getSetTuple()
        for winner,loser in sets:
            
            if trueSkill.table[loser].Rating.mu != trueSkill.table[winner].Rating.mu \
                and trueSkill.table[loser].Rating.sigma != trueSkill.table[winner].Rating.sigma:

                i += 1
            
                won[0].append(i)
                won[1].append(winner)
                won[2].append(trueSkill.table[winner].Rating.mu)
                won[3].append(trueSkill.table[winner].Rating.sigma)
                won[4].append(trueSkill.table[winner].get_match_count())
                won[5].append(trueSkill.table[winner].get_record()[0]) #wincount
                won[6].append(trueSkill.table[winner].get_record()[1]) #losscount
                won[7].append(trueSkill.win_pct(winner,loser))
                won[8].append(trueSkill.table[winner].get_win_mu_sig_avg(trueSkill)[0])#winavgmu
                won[9].append(trueSkill.table[winner].get_win_mu_sig_avg(trueSkill)[1])#winavgsig
                won[10].append(trueSkill.table[winner].get_loss_mu_sig_avg(trueSkill)[0])#lossavgmu
                won[11].append(trueSkill.table[winner].get_loss_mu_sig_avg(trueSkill)[1])#lossavgsig
                              

                lost[0].append(i)
                lost[1].append(loser)
                lost[2].append(trueSkill.table[loser].Rating.mu)
                lost[3].append(trueSkill.table[loser].Rating.sigma)
                lost[4].append(trueSkill.table[loser].get_match_count())
                lost[5].append(trueSkill.table[loser].get_record()[0]) #wincount
                lost[6].append(trueSkill.table[loser].get_record()[1]) #losscount
                lost[7].append(trueSkill.win_pct(loser,winner))
                lost[8].append(trueSkill.table[loser].get_win_mu_sig_avg(trueSkill)[0])#winavgmu
                lost[9].append(trueSkill.table[loser].get_win_mu_sig_avg(trueSkill)[1])#winavgsig
                lost[10].append(trueSkill.table[loser].get_loss_mu_sig_avg(trueSkill)[0])#lossavgmu
                lost[11].append(trueSkill.table[loser].get_loss_mu_sig_avg(trueSkill)[1])#lossavgsig

            trueSkill.rate_1vs1(winner,loser)
            
    return(won,lost)
        
##if __name__ == '__main__':
##    tournamentList = importTournamentDictFromFile('SpringPRData.txt')
##                        
###    tournamentList += importTournamentDictFromFile('ZSmashBi15.txt')
##    for tournament in tournamentList: print(tournament.getTournamentName())
##    trueSkill = cs.Players()
##    for tournament in tournamentList:
##        for player in tournament.getEntrantList():
##            if player not in trueSkill.table.keys():
##                trueSkill.add_player(player)
##        sets = tournament.getSetTuple()
##        for winner,loser in sets:
##            trueSkill.rate_1vs1(winner,loser)
##
##    createRankingTSV('UpToDate3-10.tsv',3,'all',10)
##    #createRankingTSV('RankingsALL3Sigma.tsv',3,'all')
##    

