import untangle
import TournamentClass
import scraping_functions as sf
#Ex. i is an index
#obj.SK92.P5layers.Player[i]['Name']
#{'ID':,'Name':,'Slug:','Date:','Entrants:','Data:'}

'''
Instructions:
0. Enable #Remove Pools in scraping_functions.py
1. Go into bcn file and add into Settings a File element
Ex.<Settings Multiplier="200" MinMatches="1" Decay="0" DecayValue="1" File = "2017-Q1" />
2. create obj with bcn file name
3. create obj List from your objs
4. run saveToTxt


Optional:
If you see a lot of different names compared to smash.gg
1. runNamesTxt
2. You will add the first name to Names.txt
Ex.
From NamesBNC.txt
Stdaddy: Zack
In Names.txt
Satdaddy: Zack
add new
Satdaddy: Zack, Stdaddy
3. Rerun saveToTxt


'''
obj1 = untangle.parse('2016-Q4.bcn')
obj2 = untangle.parse('2017-Q1.bcn')
obj3 = untangle.parse('2017-Q2.bcn')
objList = [obj1, obj2, obj3]
def createNamesTxt(objList, altNamesD, filename):
    final = ''
    L = []
    for obj in objList:
        for player in obj.SK92.Players.Player:
            name = sf.normalize_name(player['Name'])
            alts = player['Alts'].replace(';',',')
            L.append((name,alts))
        L.sort()
        for tup in L:
            final += tup[0] + ": " + tup[1] +"\n"

    file = open('NamesBCN.txt','w')
    file.write(final)
    file.close()
    print('done')

def createAltNames(objList):
    D = {}
    for obj in objList:
        replacementList = {}
        for player in obj.SK92.Players.Player:
            name = player['Name']
            alts = player['Alts'].split(';')
            for alt in alts:
                replacementList[alt.strip()] = name
        D[obj.SK92.Settings['File']] = replacementList
    return(D)

altNamesD = createAltNames(objList)


def replaceBNCAlts(obj,D,name):
    file = obj.SK92.Settings['File']
    replacementList = D[file]
    for replacement in replacementList:
        if name == replacement:
            name = replacementList[replacement]
    return(name)
        
def createTournament(obj):
    d = {}
    ID = 0
    for match in obj.SK92.Matches.Match:
        if match['Description'] not in d:
            ID += 1
            date = match['Timestamp'].split()[0].split('/')
            year = date[2]
            month = date[0]
            day = date[1]

            if len(month) < 2:
                month = '0'+ month
            if len(day) < 2:
                day = '0' + day
                
            datefinal = year+'-'+ month+'-'+day
            d[match['Description']] = {'Name':match['Description'],
                                       'Date':datefinal,
                                       'ID':ID,
                                       'Slug':match['Description'],
                                       'Entrants': 0,
                                       'Data':[]}
        player1 = replaceBNCAlts(obj,altNamesD,match['Player1'])
        player2 = replaceBNCAlts(obj,altNamesD,match['Player2'])
        player1 = sf.normalize_name(player1)
        player2 = sf.normalize_name(player2)
        winner = match['Winner']
        if winner == '1':
            d[match['Description']]['Data'].append([player1,player2])
        else:
            d[match['Description']]['Data'].append([player2,player1])
            
    return(d)

def getEntrantNumber(D):
    for key in D:
        setTuple = D[key]['Data']
        EntrantList = []
        for p1,p2 in setTuple:
            if p1 not in EntrantList:
                EntrantList.append(p1)
            if p2 not in EntrantList:
                EntrantList.append(p2)
        D[key]['Entrants'] = len(EntrantList)
    return(D)

def saveToTxt(objList,filename):
    final = ''
    count = 1
    for obj in objList:
        D = createTournament(obj)
        D = getEntrantNumber(D)
        for key in D:
            D[key]['ID'] = count
            final += str(D[key]) + '\n'
            count += 1
    file = open(filename,'w')
    file.write(final)
    file.close()
    print('done')

    


                

        
            
            
    
    
    
        
        
