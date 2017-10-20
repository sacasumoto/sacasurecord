import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import TournamentClass as TC
import TrueSkillStart as TSS
import os
import sys
import matplotlib
import traceback

matplotlib.use("TKAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib import style
style.use("ggplot")

LARGE_FONT = ("Veranda", 12)
NORM_FONT = ("Veranda",10)
SMALL_FONT = ("Veranda",8)

Helptxt = '''By default, file name 'LoadIn.txt' is loaded.\n
Entrant names are normalized to be of the format: 'Sacasumoto','Mike Haze', and 'S2J' (A capital after non-alphabet characters if possible).\n
Sponsors are taken out and every new word is capitalized.\n
Currently only smashgg tournaments can be added.\n
This is done by by linking a smash.gg url \n
For example: 'https://smash.gg/tournament/super-smash-sundays-41/brackets/11439/7448/30092'\n
You can also challonge brackets.
'''
Thankstxt = "Special thanks to Andrew 'PracticalTAS' Nestico' for his code, without it this wouldn't be possible.\nThank you to Sentdex for his tutorials. www.sentdex.com"



def popupmsg(msg):

    popup = tk.Tk()
    popup.wm_title("!")
    popup.iconbitmap('ngcc.ico')
    label = ttk.Label(popup, text=msg,font=NORM_FONT)
    label.pack(side="top",fill="x",pady=10)
    B1 = ttk.Button(popup,text ="Okay", command=popup.destroy)
    B1.pack()
    popup.mainloop()

def popupmsg2(title,msg):

    popup = tk.Tk()
    popup.wm_title(title)
    popup.iconbitmap('ngcc.ico')
    label = tk.Label(popup, text=msg,font=NORM_FONT,wraplength=300)
    label.pack(side="top",fill="x",pady=10)
    B1 = ttk.Button(popup,text ="Okay", command=popup.destroy)
    B1.pack()
    popup.mainloop()
    

def popupmsg3(title,msg,var):
    popup = tk.Tk()
    popup.wm_title(title)
    popup.iconbitmap('ngcc.ico')

    scrollbar = ttk.Scrollbar(popup)
    scrollbar.pack(side='right',fill='y')

    listbox = tk.Listbox(popup, yscrollcommand=scrollbar.set,height = 40, width = 50)
    Lust = sorted(msg)
    for i in Lust:
        listbox.insert('end',i)
    listbox.pack(side='left',fill='both')
    scrollbar.config(command=listbox.yview)

    def setVarFromClickOrEnter(var):
        tup = listbox.curselection()
        index = tup[0]
        var.set(Lust[index])

    popup.bind('<Double-Button-1>', lambda command: setVarFromClickOrEnter(var))
    popup.mainloop()


def popupmsg4(title,msg):
    popup = tk.Tk()
    popup.wm_title(title)
    popup.iconbitmap('ngcc.ico')

    menubar = tk.Menu(popup)

    def saveFileHandler2(msg):
        file = filedialog.asksaveasfilename(parent=popup,
                                           initialdir='.',title='Choose a file name')
        if file != None:
            try:
                filename = file
                file = open(filename,'w')
                file.write(msg)
                file.close()
                popupmsg('File saved!')
            except IOError as e:
                popupmsg('Error')


    filemenu = tk.Menu(menubar,tearoff=0)
    filemenu.add_command(label="Save File",command= lambda: saveFileHandler2(msg))
    menubar.add_cascade(label="File", menu=filemenu)

    Helptxt2 = 'Save as either .txt or .tsv'
    Helptxt3 = "Mu follows on your wins and losses, it's the raw score.\n\
Sigma follows matches number, the lower the number the more consistently you've been performing or the more accurate your score is.\n\
Score takes into account sigma into your Mu, so people with low MU and a high sigma will suffer more.\n\
Score = Mu - 3*Sigma. I didn't come up with this so i am not sure if 3 is a good fit.\n\
If you wanted a more general ranking, then ordering by Mu instead of Score is better, but if you want a ranking with context Score is better."

    helpmenu = tk.Menu(menubar,tearoff=0)
    helpmenu.add_command(label="How to save",command=lambda: popupmsg2("Save Options",Helptxt2))
    helpmenu.add_command(label="What do these values mean?",command=lambda: popupmsg2("Values Help",Helptxt3))
    menubar.add_cascade(label="Help",menu=helpmenu)

    
    tk.Tk.config(popup,menu=menubar)
    

    scrollbar = tk.Scrollbar(popup,jump='0')
    scrollbar.pack(side='right',fill='y',expand='True')

    text = tk.Text(popup,yscrollcommand=scrollbar.set,width=105)
    scrollbar.config(command=text.yview)
    text.insert('end',msg)
    text.pack(expand='True',fill='both')
    
    
    popup.mainloop()

def popupmsg5(title,msg,size):
    popup = tk.Tk()
    popup.wm_title(title)
    popup.iconbitmap('ngcc.ico')
    
    scrollbarY = tk.Scrollbar(popup,jump='0')
    scrollbarY.pack(side='right',fill='y',expand='True')

    text = tk.Text(popup,yscrollcommand=scrollbarY.set,width=size)
    scrollbarY.config(command=text.yview)
    text.insert('end',msg)
    text.pack(expand='True',fill='both')
    
    
    popup.mainloop()

    
    


def openFileHandler(masterTournament,container):
    file = filedialog.askopenfile(parent=container,
                                     mode='rb',initialdir='.',title='Choose a file')
    if file != None:
        try:
            filename = file.name
            file.close()
            masterTournament.loadFromFile(filename)
            popupmsg('File loaded!')
        except:
            popupmsg('No file chosen')

def saveFileHandler(masterTournament,container):
    file = filedialog.asksaveasfilename(parent=container,
                                           initialdir='.',title='Choose a file name')
    if file != None:
        try:
            filename = file
            masterTournament.saveToFile(filename)
            popupmsg('File saved!')
        except IOError as e:
            popupmsg('Error')

def openURLFileHandler(masterTournament,container):
    file = filedialog.askopenfile(parent=container,
                                     mode='rb',initialdir='.',title='Choose a file')
    if file != None:
        try:
            filename = file.name
            file.close()
            masterTournament.addFromUrlFile(filename)
            popupmsg('File loaded!')
        except:
            popupmsg('No file chosen')


def Quit(root):
    os._exit(1)
    
    
class Main(tk.Tk):
    def __init__(self,*args,**kwargs):
        tk.Tk.__init__(self,*args,**kwargs)
        container = tk.Frame(self)
        container.pack(side="top",fill="both", expand=True)
        container.grid_rowconfigure(0,weight=1)
        container.grid_columnconfigure(0,weight=1)
        self.wm_title('SACASURECORDS')
        self.iconbitmap('ngcc.ico')

        menubar =tk.Menu(container)
        filemenu = tk.Menu(menubar,tearoff=0)
        filemenu.add_command(label="Save File",command= lambda: saveFileHandler(Main.master,container))
        filemenu.add_command(label="Load File",command= lambda: openFileHandler(Main.master,container))
        filemenu.add_separator()
        filemenu.add_command(label="Load URL File",command= lambda: openURLFileHandler(Main.master,container))
        filemenu.add_separator()

        
        filemenu.add_command(label="Exit",command=lambda: Quit(container))
        menubar.add_cascade(label="File", menu=filemenu)

        helpmenu = tk.Menu(menubar,tearoff=0)
        helpmenu.add_command(label="How to use",command=lambda: popupmsg2("How to use",Helptxt))
        menubar.add_cascade(label="Help",menu=helpmenu)
                             
        thanksmenu = tk.Menu(menubar,tearoff=0)
        thanksmenu.add_command(label="Special Thanks",command=lambda: popupmsg2("Special Thanks",Thankstxt))
                               
        
        menubar.add_cascade(label="Thanks",menu=thanksmenu)
        

        tk.Tk.config(self,menu=menubar)
        
        self.frames = {}
        
        for F in (StartPage,PageOne,PageTwo,PageThree):
            
            frame = F(container,self)
            self.frames[F] = frame
            frame.grid(row=0,column=0, sticky ="nsew")

        self.show_frame(PageOne)
        
        Main.master = TC.MasterTournament([])
        Main.master.loadFromFile('LoadIn.txt')
        
        
    def show_frame(self,cont):
        frame = self.frames[cont]
        frame.tkraise()       

def addTourney(url,masterTournament):
    try:    
        masterTournament.addTournament(url)
        popupmsg('Tournament Added')
    except Exception:
        popupmsg('Error, use smash.gg url, challonge.com url \n or lul tournament can not be added')
##        popupmsg5("!",str(traceback.format_exc()),150)
        raise


def addedTourneys(container,masterTournament):
    final = ''
    L = []
    for tournament in masterTournament.tournamentList:
        L.append((tournament.date,tournament))
    L.sort(key=lambda tup: tup[0])
    fermat = '{:<10}\t{:<15}\t{:<80}\t{:<10}\t{:<60}\n'
    title = fermat.format('ID:','Date:','Name:','Entrants:','Slug:')
    final += title
    for tup in L:
        final += fermat.format(tup[1].eventID,tup[1].date,tup[1].name,tup[1].entrantcount,tup[1].slug.strip('\n'))
    popupmsg5('Tournaments',final,190)


class StartPage(tk.Frame,Main):
    def __init__(self,parent,controller):
        ttk.Frame.__init__(self,parent)
        label2 = tk.Label(self,text="Tournament Menu", font=LARGE_FONT)
        label2.grid(row=0,column=1)


        L2 = ttk.Label(self,text="TournamentURL")
        L2.grid(row=1,column=0)
        
        L1 = ttk.Label(self,text="TournamentID")
        L1.grid(row=2,column=0)


        ID = tk.IntVar()
        TourneyURL = tk.StringVar()
        
        E1 = ttk.Entry(self,textvariable=ID)
        E1.grid(row=2,column=1)
        E2 = ttk.Entry(self,textvariable=TourneyURL)
        E2.grid(row=1,column=1)
        E1.focus()
        E2.focus()
        
        button1 = ttk.Button(self,text="<<Go Back",
                            command=lambda: controller.show_frame(PageOne))
        button1.grid(row=0,column=0)


        button2 = ttk.Button(self,text="AddTournament",
                             command=lambda: addTourney(TourneyURL.get(),Main.master))
        button2.grid(row=3,column=1)

        button3 = ttk.Button(self,text="Tournaments Added",
                             command=lambda: addedTourneys(self,Main.master))
        button3.grid(row=3,column=0)

        button4 = ttk.Button(self,text="Clear All",
                             command=lambda:Main.master.clearAll())
        button4.grid(row=4,column=0)

        button5 = ttk.Button(self,text='Delete Tournament, using ID',
                             command=lambda:Main.master.deleteTournament(ID.get()))
        button5.grid(row=4,column=1)

        self.tourneylist = tk.StringVar()


def playerWinsLoss(container,playerVar,masterTournament):
    A = masterTournament
    D = A.getPlayerWinsLossDict(playerVar)
    T = A.getPlayerTournaments(playerVar)
    L = sorted(D,key=lambda x:(len,x[0]),reverse=False)

    title = '{:<30}\t{:<2.2f}'

    final = ''


    W = 0
    L1 = 0
    for w,l in D.values():
        W += w
        L1 += l        
##    Wpct = float((W/(W+L1))*100)
    N = A.getPlayerActivityTournaments(playerVar)
    
    title = "{:<42}\t\tActivityTournaments: {}\n".format(playerVar+"'s Record\t",N)
    subtitle = '{:<30}\t{:<12}\t{}\n'.format('Opponents:','Record:','Tournaments Entered:')

    final += title
    final += subtitle

    K = [x[1] for x in A.getActivityTournaments()]
    i=0
    for name in L:
        w,l = D[name]
        try:
            if T[i] in K:
                final += '{:<30}\t{:>4}-{:<7}\t{}\n'.format(name,w,l,(T[i]+' *'))
            else:
                final += '{:<30}\t{:>4}-{:<7}\t{}\n'.format(name,w,l,T[i])

            
        except:
            final += '{:<30}\t{:>4}-{:<7}\t{}\n'.format(name,w,l,'')
        i += 1
    final += "\n\n\n\n"

    for tournament in A.tournamentList:
        if playerVar in tournament.getEntrantList():
            L = tournament.getPlayerLoss(playerVar)
            W = tournament.getPlayerWins(playerVar)
            
            final += '{}\n'.format(tournament.getTournamentName())
            
            final += 'Wins:\n'
            for i in W:
                final += '\t{}\n'.format(i)
##            final += '\n'
            final += "Loss:\n"
            for i in L:
                final += '\t{}\n'.format(i)
            final += '\n\n'
        
            
    



    




    popupmsg5(playerVar+"'s Record",final,150)

##def playerWinsLossList(container,playerList,masterTournament):
##    playerList = playerList.split(',')
##    final2 = ''
##    for playerVar in playerList:
##        print(playerVar)
##        A = masterTournament
##        D = A.getPlayerWinsLossDict(playerVar)
##        T = A.getPlayerTournaments(playerVar)
##        L = sorted(D,key=lambda x:(len,x[0]),reverse=False)
##
##        title = '{:<30}\t{:<2.2f}'
##
##        final = ''
##
##
##        W = 0
##        L1 = 0
##        for w,l in D.values():
##            W += w
##            L1 += l        
##        Wpct = float((W/(W+L1))*100)
##        title = "{:<42}\t\tWin%: {:<2.2f}\n".format(playerVar+"'s Record\t",Wpct)
##        subtitle = '{:<30}\t{:<12}\t{}\n'.format('Opponents:','Record:','Tournaments Entered:')
##
##        final += title
##        final += subtitle
##
##        
##        i=0
##        for name in L:
##            w,l = D[name]
##            try:
##                final += '{:<30}\t{}-{:<10}\t{}\n'.format(name,w,l,T[i])
##            except:
##                final += '{:<30}\t{}-{:<10}\t{}\n'.format(name,w,l,'')
##            i += 1
##        final2 += final + '\n\n\n'
##
##        
##    popupmsg5('Player List Record',final2,150)
        

def displayEntrantList(container,masterTournament,playerName):
    List = masterTournament.getEntrantList()
    popupmsg3("Entrant List",List,playerName)




class PageOne(tk.Frame,Main):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self,text="Main Menu", font=LARGE_FONT)
        label.grid(column=0,row=0,pady=10,padx=10)

        
        self.playerName = tk.StringVar()
        L1 = ttk.Label(self,text='Enter Player Name:',font=NORM_FONT)
        L1.grid(row=1,column=0)
        E1 = ttk.Entry(self,textvariable=self.playerName)
        E1.grid(row=1,column=1)
        B1 = ttk.Button(self,text='Get Player Record',
                        command=lambda: playerWinsLoss(self,self.playerName.get(),Main.master))
        B1.grid(row=2,column=1)
        
##        self.playerNameList = tk.StringVar()
##        L2 = ttk.Label(self,text='Enter Player List:',font=NORM_FONT)
##        L2.grid(row=4,column=0)
##        E2 = ttk.Entry(self,textvariable=self.playerNameList)
##        E2.grid(row=4,column=1)
##        B2 = ttk.Button(self,text='List of Player Records',
##                        command=lambda: playerWinsLossList(self,self.playerNameList.get(),Main.master))
##        B2.grid(row=5,column=1)
##        
        

        button1 = ttk.Button(self,text="Tournaments Menu>>",
                            command=lambda: controller.show_frame(StartPage))
        button1.grid(row=0,column=1)

        button2 = ttk.Button(self,text="Get Entrants",
                             command=lambda: displayEntrantList(self,Main.master,self.playerName))
        button2.grid(row=2,column=0)

        button3 = ttk.Button(self,text="TrueSkill Menu",
                             command=lambda: controller.show_frame(PageTwo))
        button3.grid(row=3,column=1)

##        button4 = ttk.Button(self,text="TrueSkill Plots",
##                             command=lambda: controller.show_frame(PageThree))
##        button4.grid(row=3,column=1)

        E1.bind('<Return>', lambda command: B1.invoke())

def displayTrueSkillList(container,masterTournament,mu,minmatches):
    L = masterTournament.tournamentList
    msg = TSS.createRankingSTR(L,mu,minmatches)
    popupmsg4("True Skill Rankings",msg)

class PageTwo(tk.Frame,Main):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self,text="True Skill Menu", font=LARGE_FONT)
        label.grid(column=0,row=0,pady=10,padx=10)

        self.muConstant = tk.IntVar()
        self.minMatches = tk.IntVar()
        L1 = ttk.Label(self,text='Enter MU Constant',font=NORM_FONT)
        L1.grid(row=1,column=0)
        L2 = ttk.Label(self,text='Enter Min. Matches',font=NORM_FONT)
        L2.grid(row=2,column=0)
        E1 = ttk.Entry(self,textvariable=self.muConstant)
        E1.grid(row=1,column=1)
        E2 = ttk.Entry(self,textvariable=self.minMatches)
        E2.grid(row=2,column=1)

        B1 = ttk.Button(self,text='Get Ranking',
                        command=lambda: displayTrueSkillList(self,Main.master,self.muConstant.get(),self.minMatches.get()))
        B1.grid(row=3,column=1)

        button1 = ttk.Button(self,text="<<Go Back",
                            command=lambda: controller.show_frame(PageOne))
        button1.grid(row=0,column=1)

        button4 = ttk.Button(self,text="TrueSkill Plots Menu",
                             command=lambda: controller.show_frame(PageThree))
        button4.grid(row=3,column=0)




def historyPlot(masterTournament,player):
    try:
        popup = tk.Tk()
        popup.wm_title(player+"'s History Plot")
        popup.iconbitmap('ngcc.ico')

        own,win,loss = TSS.createTrueSkillPlayerHistoryFromTournament(masterTournament,player)


        x1,y1,z1 = own[2],own[0],own[1]
        x2,y2,z2 = win[2],win[0],win[1]
        x3,y3,z3 = loss[2],loss[0],loss[1]

        F = Figure()
        A = F.add_subplot(111)

        
        p = A.errorbar(x1,y1,yerr=z1,fmt='yo')
        z = A.plot(x1,y1,'k--')
        w = A.errorbar(x2,y2,fmt='go',yerr=z2)
        l = A.errorbar(x3,y3,fmt='ro',yerr=z3)

        A.set_xlabel('Match #')
        A.set_ylabel('Score/Mu')
        A.set_title(player +"'s History")

        A.legend((p,w,l),(player,player+"'s wins",player+"'s losses"),
                   numpoints=1,loc='upper left')

        canvas = FigureCanvasTkAgg(F,popup)
        canvas.show()
        canvas.get_tk_widget().pack(fill=tk.BOTH,expand=True)

        toolbar = NavigationToolbar2TkAgg(canvas,popup)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP,fill=tk.BOTH,expand=True)
    except Exception:
##        popupmsg('Error,try again')
        popupmsg5("!",str(traceback.format_exc()),150)

        

class PageThree(tk.Frame,Main):
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self,text="True Skill Plots Menu", font=LARGE_FONT)
        label.grid(column=0,row=0,pady=10,padx=10)

        self.playerName = tk.StringVar()
        L1 = ttk.Label(self,text='Enter Player Name:',font=NORM_FONT)
        L1.grid(row=1,column=0)
        E1 = ttk.Entry(self,textvariable=self.playerName)
        E1.grid(row=1,column=1)

        B1 = ttk.Button(self,text='Get History Plot',
                        command=lambda: historyPlot(Main.master,self.playerName.get()))
        B1.grid(row=2,column=1)
        button1 = ttk.Button(self,text="<<Go Back",
                            command=lambda: controller.show_frame(PageTwo))
        button1.grid(row=0,column=1)

        E1.bind('<Return>', lambda command: B1.invoke())
 
        
                                                                            

app = Main()
app.mainloop()
        
