# napoleon.pyw

from model import Model
from view import View
import tkinter as tk
import os, sys

helpText = '''
OBJECTIVE

Napoleon at St. Helena is played with two decks of 52 cards each.  \
The objective is to arrange each of the eight suits in sequence from the Ace up \
to the King on the foundation piles.

SETUP

There are ten tableau piles, initially with four cards each.  \
The remaining 64 cards are placed in the stock.  \
There are also eight foundation piles.  

MOVING CARDS

Cards can only be moved one at a time, on top of other cards of the same suit, \
in sequnce.  On the tableau piles, suits are built down from King to Ace.  \
On the foundation piles, suits are built up from Ace to King.  \
The top card of the stock, and the top card of the waste pile are available \
to be moved. 

If you have an empty tableau pile, you can move any card available for play \
onto the empty pile.  Only an Ace can be moved onto an empty foundation pile.

You can run through the stock at most twice.  To see the next card in the stock, \
you must play the top card to a foundation or tableau pile, or drag it to the \
waste pile.

SUPERMOVES

This app implements "supermoves" whereby more than one card can be moved at \
once.  For example, if the 5, 6, 7 and 8 of Diamonds are in sequence at the top of \
a tableau pile, they can all be dropped on the 4 of Diamonds at the top of a \
foundation pile.  Clicking on the 8 will allow you to drag all four cards at once.  \
Or, if there were three empty tableau piles, you could move the four cards onto one \
of the empty piles, but it would take nine moves: first move the top three cards \
to empty piles, then play the 5 onto the 6 and the 8 onto and empty pile.  \
Four more moves get the 5, 6 and 7 on top of the 8. This app allows you to move \
all four cards at once, if there are sufficient empty piles.  If there were only two \
empty tableau piles, the app would allow you to move all four cards onto the \
9 of Diamonds at the top of another tableau pile.
'''

CARD_DIR = os.path.join(os.path.dirname(sys.argv[0]), 'decks')
DEFAULT_DECK = os.path.join(CARD_DIR, 'small')
class Napoleon:
    def __init__(self):
        try:
            with open('napoleon.ini') as infile:
                text = infile.readlines()
                games = int(text[0].strip())
                wins = int(text[1].strip())
                deck = text[2].strip()
        except IOError:
            games,wins,deck = 0,0, DEFAULT_DECK
        self.model = Model(games, wins)
        self.view = View(self, self.quit, deck, width=950, height=1000)
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
        text['font'] = ('helevetica', 14, 'normal')
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

    def showHelp(self, event):
        self.helpText.deiconify()
        self.helpText.text.see('1.0')  
        
    def saveStats(self):
        model = self.model
        games, wins = model.games, model.wins
        with open('napoleon.ini', 'w') as outfile:
            outfile.write('%d\n%d\n'%(games, wins))
            outfile.write('%s\n'%self.view.deck.get())
            
    def makeMenu(self):
        top = self.view.menu
        options = tk.Menu(top, tearoff=False)    
        for deck in os.listdir(CARD_DIR):
            if deck.startswith('.'): continue
            options.add_radiobutton(
                label=deck,
                value=os.path.join(CARD_DIR,deck),
                variable=self.view.deck)
        top.add_cascade(label='Deck', menu=options)

    def quit(self):
        self.saveStats()
        self.view.root.quit()

if __name__ == "__main__":
    Napoleon()
