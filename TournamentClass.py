import requests
import scraping_functions as sf
import pytz as pytz
from datetime import datetime
import parse
"""
Copyright (c) 2015 Andrew Nestico

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""

"""
Thanks to Andrew Nestico

"""


'''Smash.GG Code'''

def get_tournament_slug_from_smashgg_urls(url):
    return(url.split("/")[4])


def get_tournament_info(slug):
    tournament_url = "https://api.smash.gg/tournament/" + slug
    t = requests.get(tournament_url, verify='cacert.pem')
    tournament_data = t.json()
    tournament_name = tournament_data["entities"]["tournament"]["name"]
    
    timezone = tournament_data["entities"]["tournament"]["timezone"]
    if timezone != True:
        timezone = 'America/Los_Angeles'
        

    # Scrape event page in case event ends earlier than tournament
##    if slug == 'the-road-to-genesis':
    if 'weds-night-fights' in slug:
        event_url = "https://api.smash.gg/tournament/" + slug + "/event/" + "smash-melee"
    elif 'training-mode-tuesdays-13' == slug:
        event_url = "https://api.smash.gg/tournament/" + slug + "/event/" + "tmt-top-8"
    else:
        event_url = "https://api.smash.gg/tournament/" + slug + "/event/" + "melee-singles"
    try:
        e = requests.get(event_url, verify='cacert.pem')
        event_data = e.json()
        event_id = event_data["entities"]["event"]["id"]
    except:
        event_url = "https://api.smash.gg/tournament/" + slug + "/event/" + "melee-singles"
        e = requests.get(event_url, verify='cacert.pem')
        event_data = e.json()
        event_id = event_data["entities"]["event"]["id"]

    timestamp = event_data["entities"]["event"]["endAt"]
    if not timestamp:
        timestamp = tournament_data["entities"]["tournament"]["endAt"]
    # Get local date
    date = datetime.fromtimestamp(timestamp, pytz.timezone(timezone)).date()
    date = str(date)

    ## Get standings
    if 'training-mode-tuesdays' in slug:
        attendee_url = 'https://api.smash.gg/tournament/'+slug+'/attendees?filter=%7B"eventIds"%3A'+str(event_id)+'%7D'
        a_data = requests.get(attendee_url, verify='cacert.pem').json()
        count = a_data["total_count"]
    else:
        try:
            standing_string = "/standings?expand[]=attendee&per_page=100"
            standing_url = event_url + standing_string
            s = requests.get(standing_url,verify='cacert.pem')
            s_data = s.json()
            count = s_data["total_count"]
        except:
            attendee_url = 'https://api.smash.gg/tournament/'+slug+'/attendees?filter=%7B"eventIds"%3A'+str(event_id)+'%7D'
            a_data = requests.get(attendee_url, verify='cacert.pem').json()
            count = a_data["total_count"]
    return([tournament_name,event_id,count,str(date)])
    
def create_smashgg_api_urls(slug):
    """from master url creates list of api urls for pools and bracket"""

    if 'weds-night-fights' in slug:
        url = "https://api.smash.gg/tournament/" + slug + "/event/smash-melee?expand[0]=groups&expand[1]=phase"
    elif 'training-mode-tuesdays-13' == slug:
        url = "https://api.smash.gg/tournament/" + slug + "/event/tmt-top-8?expand[0]=groups&expand[1]=phase"
    else:
        url = 'http://api.smash.gg/tournament/' + slug + '/event/melee-singles?expand[0]=groups&expand[1]=phase'
    try:
        data = requests.get(url,verify='cacert.pem').json()
        groups = data["entities"]["groups"]
    except:
        url = 'http://api.smash.gg/tournament/' + slug + '/event/melee-singles?expand[0]=groups&expand[1]=phase'
        data = requests.get(url,verify='cacert.pem').json()
        groups = data["entities"]["groups"]
        
    urlList = []
    for i in range(len(groups)):
        iD = str(groups[i]["id"])
        urlList.append("http://api.smash.gg/phase_group/" + iD + "?expand[0]=sets&expand[1]=entrants")

    if 'red-bull-smash-gods-and-gatekeepers-2' in slug:
        url = "https://api.smash.gg/tournament/" + slug + "/event/forsaken-bracket?expand[0]=groups&expand[1]=phase"
        data = requests.get(url,verify='cacert.pem').json()
        groups = data["entities"]["groups"]
        for i in range(len(groups)):
            iD = str(groups[i]["id"])
            urlList.append("http://api.smash.gg/phase_group/" + iD + "?expand[0]=sets&expand[1]=entrants")

    return(urlList)

def parse_smashgg_set(set,entrant_dict):
    winnerId = set["winnerId"]
    entrant1Id = set["entrant1Id"]
    entrant1Score = set["entrant1Score"]
    entrant2Id = set["entrant2Id"]
    entrant2Score = set["entrant2Score"]

    if entrant1Id and entrant2Id:
        entrant1Name = sf.normalize_name(entrant_dict[entrant1Id])
        entrant2Name = sf.normalize_name(entrant_dict[entrant2Id])

        if entrant1Name != '' or entrant2Name != '':
            if type(entrant1Score) is int and type(entrant2Score) is int:
                if entrant1Score > -1 and entrant2Score > -1:
                    if entrant1Id == winnerId:
                        return entrant1Name + "," + entrant2Name
                    else:
                        return entrant2Name + "," + entrant1Name
            else:
                if entrant1Id == winnerId:
                    return entrant1Name + "," + entrant2Name
                elif entrant2Id == winnerId:
                    return entrant2Name + "," + entrant1Name
        else:
            return('error1,error2')


def write_txt_from_smashgg(slug):
    """Writes smash.gg bracket data to a file."""
    urlList = create_smashgg_api_urls(slug)
    strTuple = ''
    for url in urlList:
        try:
            data = requests.get(url,verify='cacert.pem').json()
            entrants = data["entities"]["entrants"]
            entrant_dict = {}
            for entrant in entrants:
                entrant_dict[entrant["id"]] = entrant["name"]
            sets = data["entities"]["sets"]
            set_data = ""
            grand_finals = ""
            for set in sets:
                parsed_set = parse_smashgg_set(set, entrant_dict)
                if parsed_set:
                    if set["isGF"]:
                        grand_finals += parsed_set + "\n"
                    else:
                        set_data += parsed_set + "\n"
            parsed_matches = set_data + grand_finals
            strTuple += parsed_matches
        except:
            continue
    return(strTuple)

def setTuple(strTuple):
    sets = strTuple.split('\n')
    setTuple = []
    for match in sets:
        if len(match) > 0:
            if len(match.split(",")) == 2:
                setTuple.append(match.split(","))
    return(setTuple)

def playerWins(player,setTuple):
    winList = []
    for p1,p2 in setTuple:
        if p1 == player:
            winList.append(p2)  
    return(winList)

def playerLoss(player,setTuple):
    lossList = []
    for p1,p2 in setTuple:
        if p2 == player:
            lossList.append(p1)
    return(lossList)

def entrantList(setTuple):
    EntrantList = []
    for p1,p2 in setTuple:
        if p1 not in EntrantList:
            EntrantList.append(p1)
        if p2 not in EntrantList:
            EntrantList.append(p2)
    return(EntrantList)


'''

Challonge

'''


def getTournamentSlug(url):
    L = url.split('/')
    p1 = L[2]
    p2 = L[3]
    if p1 == 'challonge.com':
        slug = p2
    else:
        p1 = p1.split('.')[0]
        slug = p1+'-'+p2
    return(slug)

def getTournamentInfo(slug,key):
    base_url = 'https://api.challonge.com/v1/tournaments/'
    url = base_url+slug+'.json?api_key='+key
    data = requests.get(url,verify='cacert.pem').json()
    Name = data['tournament']['name']
    ID = data['tournament']['id']
    EntrantCount = data['tournament']['participants_count']
    Date = data['tournament']['started_at'][:10]

    return([Name,ID,EntrantCount,Date])

def getParticipantIDs(slug,key):
    base_url = 'https://api.challonge.com/v1/tournaments/'
    url = base_url+slug+'/participants.json?api_key='+key
    data = requests.get(url,verify='cacert.pem').json()
    D = {}
    for entrant in data:
        if entrant['participant']['name']:                 
            name = entrant['participant']['name']
        else:
            name = entrant['participant']['username']
        if entrant['participant']['id']:
            entrant_id = entrant['participant']['id']
        else:
            entrant_id = entrant['participant']['group_player_ids']
        D[entrant_id] = name
    return(D)
    

def getTournamentSets(slug,key):
    base_url = 'https://api.challonge.com/v1/tournaments/'
    url = base_url+slug+'/matches.json?api_key='+key+"&state=complete"
    data = requests.get(url, verify='cacert.pem').json()
    nameIDDict = getParticipantIDs(slug,key)
    setTuple = []
    nonDQs = []
    for match in data:
        m = match['match']
        setStringsList = m['scores_csv'].split(',')
        s1T = 0
        s2T = 0
        for matchCount in setStringsList:
            s1,s2 = parse.parse("{:d}-{:d}", matchCount)
            s1T += s1
            s2T += s2
        if s1T == -1 or s2T == -1:
            continue
        else:
            nonDQs.append(match)
            
##        try:
##            s1,s2 = parse.parse("{:d}-{:d}", setCount)
##            if s1 < 0 or s2 < 0:
##                continue
##            else:
##                nonDQs.append(match)
##        except Exception as e:
##            continue
####            print('Invalid Set')
    
    for match in nonDQs:        
        p1ID = match["match"]["winner_id"]
        p2ID = match["match"]["loser_id"]
##        print(p1ID,p2ID)
##        print(sf.normalize_name(nameIDDict[p1ID]), sf.normalize_name(nameIDDict[p2ID]))
        p1 = sf.normalize_name(nameIDDict[p1ID])
        p2 = sf.normalize_name(nameIDDict[p2ID])
        setTuple.append([p1,p2])
    return(setTuple)

def challongeURL(url):
    slug = getTournamentSlug(url)
    key = #USE YOUR CHALLONGE API
    L = getTournamentInfo(slug,key)
    Name = L[0]
    ID = L[1]
    EntrantCount = L[2]
    Date = L[3]
    Data = getTournamentSets(slug,key)
    return({'Name':Name,'ID':ID,'Slug':slug,'Entrants':EntrantCount,'Date':Date,'Data':Data})



'''

Tournament Code

'''

class Tournament:
    def __init__(self, url,**kwargs):
        if url == "Loading":
            self.name = kwargs['Name']
            self.eventID = kwargs['ID']
            self.slug = kwargs['Slug']
            self.entrantcount = kwargs['Entrants']
            self.date = kwargs['Date']
            self.sets = kwargs['Data']
            self.raw = kwargs
        elif "challonge.com" in url:
            D = challongeURL(url)
            self.name = D['Name']
            self.eventID = D['ID']
            self.slug = D['Slug']
            self.entrantcount = D['Entrants']
            self.date = D['Date']
            self.sets = D['Data']
            self.raw = D    
        else:
            self.slug = get_tournament_slug_from_smashgg_urls(url)
            self.info = get_tournament_info(self.slug)
            self.name = self.info[0]
            self.eventID = self.info[1]
            self.entrantcount = self.info[2]
            self.date = self.info[3]
            self.sets = setTuple(write_txt_from_smashgg(self.slug))
            self.raw = {'Name':self.info[0],'ID':self.info[1],'Slug':self.slug,'Entrants':self.info[2],'Date':self.info[3],'Data':self.sets}
    
    def getEntrantList(self):
        return(entrantList(self.sets))
    def getPlayerLoss(self,player):
        return(playerLoss(player,self.sets))
    def getPlayerWins(self,player):
        return(playerWins(player,self.sets))
    def getTournamentName(self):
        return(self.name)
    def getTournamentEntrantcount(self):
        return(self.entrantcount)
    def getTournamentDate(self):
        return(self.date)
    def getTournamenteventID(self):
        return(self.eventID)
    def getTournamentSlug(self):
        return(self.slug)
    def getSetTuple(self):
        return(self.sets)


'''

MasterTournament Code Beings

'''



class MasterTournament:
    def __init__(self,tournamentList):
        self.tournamentList = tournamentList

    def addTournament(self, url,**kwargs):
        tournamentSlugs = []
        for tournament in self.tournamentList:
            tournamentSlugs.append(tournament.slug)

        placer = Tournament(url,**kwargs)
        if placer.slug not in tournamentSlugs:
            self.tournamentList.append(placer)
            return(self.tournamentsAdded())

    def addTournamentFromUrlList(self,urlList):
        for url in urlList:
            self.addTournament(url)

    def tournamentsAdded(self):
        tournamentNames = []
        for tournament in self.tournamentList:
            tournamentNames.append(tournament.getTournamentName())
        return(sorted(tournamentNames))
    
    def deleteTournament(self,tournamentID):
        for tournament in self.tournamentList:
            if tournament.eventID == tournamentID:
                self.tournamentList.remove(tournament)
        return(self.tournamentsAdded())
    
    def getEntrantList(self):
        entrantsRaw = []
        entrantsNormalized = []
        for tournament in self.tournamentList:
            entrantsRaw += tournament.getEntrantList()
        for player in entrantsRaw:
            if player not in entrantsNormalized:
                entrantsNormalized.append(player)
    
        return(sorted(entrantsNormalized,key=lambda x:(len,x[0]),reverse=False))

    def getUniqueEntrantsNumber(self):
        return(len(self.getEntrantList()))

    def getTotalEntrantsNumber(self):
        entrantsRaw = []
        for tournament in self.tournamentList:
            entrantsRaw += tournament.getEntrantList()
        return(len(entrantsRaw))

    def getPlayerTournaments(self,player):
        tournaments = []
        for tournament in self.tournamentList:
            if player in tournament.getEntrantList():
                tournaments.append(tournament.getTournamentName())
        return(sorted(tournaments))

#Player Activity Code
    def getPlayerActivityTournaments(self,player):
        tournaments = []
        for tournament in self.tournamentList:
            if player in tournament.getEntrantList() and tournament.getTournamentEntrantcount() > 60:
                tournaments.append(tournament.getTournamentName())
        return(len(tournaments))

    def getActivityTournaments(self):
        tournaments = []
        for tournament in self.tournamentList:
            if tournament.getTournamentEntrantcount() > 60:
                tournaments.append((tournament.getTournamentEntrantcount(),tournament.getTournamentName()))
        return(sorted(tournaments))
        
    def getAllPlayersActivity(self):
        D = {}
        players = []
        activitytournaments = []
        for tournament in self.tournamentList:
            if tournament.getTournamentEntrantcount() > 60:
                for player in tournament.getEntrantList():
                    if player not in D:
                        D[player] = [1,tournament.getTournamentName()]
                    else:
                        D[player][0] += 1
                        D[player][1] += ' '+tournament.getTournamentName()
        return(D)
                
    def getActivePlayers(self):
        D1 = {}
        D2 = self.getAllPlayersActivity()
        for key in D2:
            if D2[key][0] > 3:
                D1[key] = [D2[key][0],D2[key][1]]
        return(D1)
            
                
    def getPlayerWins(self,player):
        winsRaw = [] #List of players Player beat
        winsNormalized = []
        winChecked = []#List of players checked
        for tournament in self.tournamentList:
            winsRaw += tournament.getPlayerWins(player)
        for playerWinAgainst in winsRaw:
            if playerWinAgainst not in winChecked:
                winChecked.append(playerWinAgainst)
                count = winsRaw.count(playerWinAgainst)
                winsNormalized.append(playerWinAgainst + ' x{}'.format(count))
        return(sorted(winsNormalized,key=lambda x:(len,x[0]),reverse=False))

    def getPlayerLoss(self,player):
        lossRaw = []
        lossNormalized = []
        lossChecked = []
        for tournament in self.tournamentList:
            lossRaw += tournament.getPlayerLoss(player)
        for playerLossAgainst in lossRaw:
            if playerLossAgainst not in lossChecked:
                lossChecked.append(playerLossAgainst)
                count = lossRaw.count(playerLossAgainst)
                lossNormalized.append(playerLossAgainst + ' x{}'.format(count))
        return(sorted(lossNormalized,key=lambda x:(len,x[0]),reverse=False))

    def getPlayerWinsLossDict(self,player):
        D = {}
        
        winsRaw = []
        winChecked = []
        lossRaw = []
        lossChecked = []
        for tournament in self.tournamentList:
            winsRaw += tournament.getPlayerWins(player)
            lossRaw += tournament.getPlayerLoss(player)
        for playerWinAgainst in winsRaw:
            if playerWinAgainst not in winChecked:
                winChecked.append(playerWinAgainst)
                count = winsRaw.count(playerWinAgainst)
                if playerWinAgainst not in D:
                    D[playerWinAgainst] = [0,0]
                D[playerWinAgainst][0] += count

        for playerLossAgainst in lossRaw:
            if playerLossAgainst not in lossChecked:
                lossChecked.append(playerLossAgainst)
                count = lossRaw.count(playerLossAgainst)
                if playerLossAgainst not in D:
                    D[playerLossAgainst] = [0,0]
                D[playerLossAgainst][1] += count

        return(D)
        

    def getPlayerTotalSets(self,player):
        count = 0
        D = self.getPlayerWinsLossDict(player)
        for opponent in D:
            W,L = D[opponent]
            count += W
            count += L
        return(count)
     
    def getPlayerWinsLoss(self,player):
        print('Wins:{}\nLosses:{}'.format(self.getPlayerWins(player),self.getPlayerLoss(player)))
      
    def saveToFile(self,filename):
        Final = ''
        L = []
        for tournament in self.tournamentList:
            L.append(tournament.raw)
        file = open(filename,'w',encoding='utf-8')
        for data in L:
            Final += str(data) + '\n'
        file.write(Final)
        file.close()

    def loadFromFile(self,filename,encoding='utf-8'):
        file = open(filename,'r',encoding='utf-8')
        L = file.readlines()
        for tournamentDict in L:
            self.addTournament('Loading',**eval(tournamentDict))
        print("Done")
        return(self.tournamentsAdded())

    def addFromUrlFile(self,filename,encoding='utf-8'):
        file = open(filename,'r',encoding='utf-8')
        
        L = file.readlines()
        for url in L:
            print(url.strip('\n'))
            self.addTournament(url.strip('\n'))
            print('OK')
        print('Done')
        return(self.tournamentsAdded())

    def normalizeNamesAgain(self):
        for tournament in self.tournamentList:
            newsetTuple =[]
            for p1,p2 in tournament.sets:
                newsetTuple.append([sf.normalize_name(p1),sf.normalize_name(p2)])
            tournament.setTuple = newsetTuple
            tournament.raw['Data'] = newsetTuple
        print('Done')
    def clearAll(self):
        self.tournamentList = []

##if '__name__' != '__init__':
##    M = MasterTournament([])
##    M.loadFromFile('LoadIn.txt')
##    M.normalizeNamesAgain()

