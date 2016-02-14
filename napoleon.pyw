# napoleon.pyw

from model import Model
from view import View
import tkinter as tk
#from tkinter.messagebox import showerror, showinfo, askokcancel
from datetime import datetime
import sys, os

FMT  = '%Y_%m_%d_%H_%M_%S'      # format strings for datetime objects
FMT2 = '%x %X'

helpText = '''
OBJECTIVE
Napoleon at St. Helena is played with two decks of 52 cards each.  The objective is to arrange each of the eight suits in sequence from the Ace up to the King on the foundation piles.

SETUP
There are ten tableau piles, initially with. cards each.  The remaining 64 cards are placed in the stock.  There are also eight foundation piles.  

MOVING CARDS
Cards can only be moved one at a time, on top of other cards of the same suit. in sequnce.  On the tableau piles, suits are built down from King to Ace.  On the foundation piles, suits are built up from Ace to King.  The top card of the stock, and the top card of the waste pile are available to be moved. 

If you have an empty tableau pile, you can move any card available for play onto the empty pile.  Only an Ace can be moved onto an empty foundation pile.

You can run through the stock at most twice.
'''

class Napoleon:
    def __init__(self):
        try:
            with open('napoleon.ini') as infile:
                text = infile.readlines()
                games = int(text[0].strip())
                wins = int(text[1].strip())
        except IOError:
            games, wins = 0,0
        self.model = Model(games, wins)
        self.view = View(self, self.quit, width=950, height=1000)
        self.makeHelp()
        self.makeMenu()
        self.view.start()      #  start the event loop

    def makeHelp(self):
        top = self.helpText = tk.Toplevel()
        top.transient(self.view.root)
        top.protocol("WM_DELETE_WINDOW", top.withdraw)
        top.withdraw()
        top.resizable(False, True)
        top.title("Napoleon at St. Helena Help")
        f = tk.Frame(top)
        self.helpText.text = text = tk.Text(f, height=30, width=80, wrap=tk.WORD)
        text['font'] = ('helevetica', 12, 'normal')
        text['bg'] = '#ffef85'
        text['fg'] = '#8e773f'
        scrollY = tk.Scrollbar(f, orient=tk.VERTICAL, command=text.yview)
        text['yscrollcommand'] = scrollY.set
        text.grid(row=0, column=0, sticky='NS')
        f.rowconfigure(0, weight=1)
        scrollY.grid(row=0, column=1, sticky='NS')
        tk.Button(f, text='Dismiss', command=top.withdraw).grid(row=1, column=0)
        f.grid(sticky='NS')
        top.rowconfigure(0, weight=1)
        text.insert(tk.INSERT,helpText)

    def makeMenu(self):
        top = self.view.menu
        top.add_command(label='Help', command = self.showHelp)  

    def showHelp(self):
        self.helpText.deiconify()
        self.helpText.text.see('1.0')  
        
    def saveStats(self):
        model = self.model
        games, wins = model.games, model.wins
        with open('napoleon.ini', 'w') as outfile:
            outfile.write('%d\n%d\n'%(games, wins))

    def quit(self):
        self.saveStats()
        self.view.root.quit()

if __name__ == "__main__":
    Napoleon()
