# view.py
'''
The visual interface for Napoleon at St. Helelna solitaire.
The view knows about the model, but not vice versa
Thce canvas widget is used for both view and controller.
'''
import sys, os, itertools
import tkinter as tk
from model import SUITNAMES, RANKNAMES, ALLRANKS, Card
#from tkinter.messagebox import showerror
#from utils import ScrolledCanvas
#from tkinter.simpledialog import SimpleDialog

# Constants determining the size and layout of cards piles.
# Adjacent stacks are separated by MARGIN pixels
# OFFSET is the offset used for displaying the
# a card to the right of another in the tableau.

CARDWIDTH = 71
CARDHEIGHT = 96
MARGIN = 10
OFFSET = 15

BACKGROUND = '#070'
OUTLINE = '#060'        # outline color of foundation files
CELEBRATE = 'yellow'     # Color of "you won" message

# Cursors
DEFAULT_CURSOR = 'arrow'
SELECT_CURSOR = 'hand2'

STATUS_FONT = ('Helvetica', '12', 'normal')
STATS_FONT = ('Courier', '12', 'normal')   # fixed-width font
STATUS_BG = 'gray'

imageDict = {}   # hang on to images, or they may disappear!

class View: 
    '''
    Cards are represented as canvas image items,  displaying either the face
    or the back as appropriate.  Each card has the tag "card".  This is 
    crucial, since only canvas items tagged "card" will respond to mouse
    clicks.
    '''
    def __init__(self, parent, quit, **kwargs):
        # kwargs passed to Canvas
        # quit is function to call when main window is closed
        self.parent = parent          # parent is the Napoleon application
        self.model =  parent.model
        self.root = root = tk.Tk()
        root.protocol('WM_DELETE_WINDOW', quit)
        root.resizable(height=False, width=False)
        width = kwargs['width']
        height = kwargs['height']
        self.root.wm_geometry('%dx%d-10+10'%(width,height))
        root.title("Napoleon at St. Helena Solitaire")
        self.menu = tk.Menu(root)         # parent constructs actual menu         
        root.config(menu=self.menu)   
        self.tableau = []           # NW corners of the tableau piles
        self.foundations = []   # NW corners of the foundation piles
        x = MARGIN
        y = 5* MARGIN        
        for k in range(8):
            x += MARGIN + CARDWIDTH
            self.foundations.append((x, y)) 
        y = 7*MARGIN + CARDHEIGHT
        x = MARGIN
        for k in range(5):
            self.tableau.append((x, y)) 
            y += 2*MARGIN + CARDHEIGHT
        x = (width - CARDWIDTH)//2 - MARGIN
        y = 7*MARGIN + CARDHEIGHT
        for k in range(5):
            self.tableau.append((x, y)) 
            y += 2*MARGIN + CARDHEIGHT 
        x = width - 2*MARGIN - CARDWIDTH
        self.stock = (x,y)   # NW corner of stock
        y -= 2*MARGIN - CARDHEIGHT
        self.waste = (x, y) #NW corner of waste

        status = tk.Frame(root, bg = STATUS_BG)       
        self.tableauCards =  tk.Label(status, 
                                      relief = tk.RIDGE, font = STATUS_FONT, bg = STATUS_BG, fg = 'Black', bd = 2)
        self.foundationCards =  tk.Label(status, 
                                         relief = tk.RIDGE, font = STATUS_FONT, bg = STATUS_BG, fg = 'Black', bd = 2)
        self.wasteCards = tk.Label(status, 
                                   relief = tk.RIDGE, font = STATUS_FONT, bg = STATUS_BG, fg = 'Black', bd = 2)
        self.stockCards = tk.Label(status, 
                                   relief = tk.RIDGE, font = STATUS_FONT, bg = STATUS_BG, fg = 'Black', bd = 2)
        self.tableauCards.pack(expand=tk.NO, fill = tk.NONE, side = tk.RIGHT)
        self.foundationCards.pack(expand=tk.NO, fill = tk.NONE, side = tk.RIGHT)
        self.wasteCards.pack(expand=tk.NO, fill = tk.NONE, side = tk.RIGHT)
        self.stockCards.pack(expand=tk.NO, fill = tk.NONE, side = tk.RIGHT)
        canvas = self.canvas = tk.Canvas(root, bg=BACKGROUND, cursor=DEFAULT_CURSOR, **kwargs)
        status.pack(expand=tk.NO, fill = tk.X, side=tk.BOTTOM)
        canvas.pack()
        self.loadImages()
        self.createCards()
        canvas.tag_bind("card", '<ButtonPress-1>', self.onClick)
        canvas.tag_bind("card", '<Double-Button-1>', self.onDoubleClick)
        canvas.bind('<B1-Motion>', self.drag)
        canvas.bind('<ButtonRelease-1>', self.onDrop)
        for w in self.tableau:
            canvas.create_rectangle(w[0], w[1], w[0]+CARDWIDTH, w[1]+CARDHEIGHT, outline = OUTLINE)    
        for f in self.foundations:
            canvas.create_rectangle(f[0], f[1], f[0]+CARDWIDTH, f[1]+CARDHEIGHT, outline = OUTLINE)
        canvas.create_text(self.foundations[0][0], self.foundations[0][1]+CARDHEIGHT, 
                            text = "'The game is done! I've won! I've won!'\nQuoth she, and whistles thrice.",
                            fill = BACKGROUND, font=("Times", "32", "bold"), tag = 'winText', anchor=tk.NW)
        self.show()

    def start(self):
        self.root.mainloop()

    def loadImages(self):
        PhotoImage = tk.PhotoImage
        cardDir = os.path.join(os.path.dirname(sys.argv[0]), 'cards') 
        blue = PhotoImage(file=os.path.join(cardDir,'blueBackVert.gif'))
        red = PhotoImage(file=os.path.join(cardDir,'redBackVert.gif'))
        imageDict['blue'] = blue
        imageDict['red'] = red    
        for rank, suit in itertools.product(ALLRANKS, SUITNAMES):
            face = PhotoImage(file = os.path.join(cardDir, suit+RANKNAMES[rank]+'.gif'))               
            imageDict[rank, suit] = face

    def createCards(self):
        model = self.model
        canvas = self.canvas   
        for card in model.deck:
            c = canvas.create_image(-200, -200, image = None, anchor = tk.NW, tag = "card")
            canvas.addtag_withtag('code%d'%card.code, c)

    def showtableau(self, k):
        '''
        Display tableau pile number k
        '''
        x, y = self.tableau[k]
        canvas = self.canvas
        for card in self.model.tableau[k]:
            tag = 'code%d'%card.code
            canvas.coords(tag, x, y)
            if card.faceUp():
                foto = imageDict[card.rank, card.suit]
                x += OFFSET
            else:
                foto = imageDict[card.back]
                x += OFFSET
            canvas.itemconfigure(tag, image = foto)
            canvas.tag_raise(tag) 

    def show(self):
        model = self.model
        canvas = self.canvas
        self.showStock()
        for k in range(10):
            self.showtableau(k)
        for k in range(8):
            self.showFoundation(k)    
        color = CELEBRATE if model.win() else BACKGROUND
        canvas.itemconfigure('winText', fill=color)
        self.wasteCards.configure(text='Waste %d'%len(model.waste))
        self.tableauCards.configure(text='Tableau %d'%sum(len(t) for t in model.tableau))
        self.stockCards.configure(text='Stock %d'%len(model.stock))
        self.foundationCards.configure(text='Foundation %d'%sum(len(f) for f in model.foundations))

    def dealUp(self):
        self.model.dealUp()
        self.show()

    def showFoundation(self, k):
        model = self.model
        canvas = self.canvas
        x, y = self.foundations[k]
        for card in model.foundations[k]:
            tag = 'code%d'%card.code
            canvas.itemconfigure(tag, image = imageDict[card.rank, card.suit])
            canvas.coords(tag,x,y)
            canvas.tag_raise(tag)

    def showStock(self):
        model = self.model
        canvas = self.canvas
        x, y = self.stock
        for card in model.stock:
            tag = 'code%d'%card.code
            canvas.itemconfigure(tag, image = imageDict[card.back])
            canvas.coords(tag,x,y)
            canvas.tag_raise(tag)    

    def grab(self, selection, k, mouseX, mouseY):
        '''
        Grab the cards in selection.
        k is the index of the source tableau pile.
        Note that all the cards are face up.
        '''
        canvas = self.canvas
        if not selection:
            return
        self.mouseX, self.mouseY = mouseX, mouseY
        west = self.tableau[k][0]
        for card in selection:
            tag = 'code%s'%card.code
            canvas.tag_raise(tag)
            canvas.addtag_withtag("floating", tag)
        canvas.configure(cursor=SELECT_CURSOR)
        dx = 5 if mouseX - west > 10 else -5
        canvas.move('floating', dx, 0)

    def drag(self, event):
        try:
            x, y = event.x, event.y
            dx, dy = x - self.mouseX, y - self.mouseY
            self.mouseX, self.mouseY = x, y
            self.canvas.move('floating', dx, dy)
        except AttributeError:
            pass

    def onClick(self, event):
        '''
        Respond to click on stock, waste or tableau pile.  
        Clicks on foundation piles are ignored.
        '''
        model = self.model
        canvas = self.canvas
        tag = [t for t in canvas.gettags('current') if t.startswith('code')][0]
        code = int(tag[4:])             # code of the card clicked
        if model.stock.find(code) != -1:
            if model.canDeal():
                self.dealUp()
                return
            else:
                self.cannotDeal()
        for k, w in enumerate(model.tableau):
            idx = w.find(code)
            if idx != -1:
                break
        else:       # loop else
            return
        selection = model.grab(k, idx)
        self.grab(selection, k, event.x, event.y)  

    def onDoubleClick(self, event):
        '''
        If the user double clicks a card that is part of a complete suit,
        the suit will be moved to the first available foundation pile.
        '''
        model = self.model
        canvas = self.canvas
        tag = [t for t in canvas.gettags('current') if t.startswith('code')][0]
        code = int(tag[4:])             # code of the card clicked
        for k, w in enumerate(model.tableau):
            idx = w.find(code)
            if idx != -1:
                break
        else:       # loop else
            return 
        model.completeSuit(k, idx)
        self.show()

    def scroll(self, event):
        '''
        Use the mouse wheel to scroll the canvas.
        If we are dragging cards, they must be moved in the same direction
        as the canvas scrolls, or the cursor will become separated from the
        cards being dragged.  
        '''
        canvas = self.canvas
        lo, hi = canvas.yview()
        height = int(canvas['scrollregion'].split()[3])
        if event.num == 5 or event.delta < 0:       
            n = 1
        elif event.num == 4 or event.delta > 0:     
            n = -1
        canvas.yview_scroll(n, tk.UNITS)
        lo2, hi2 = canvas.yview()
        canvas.move('floating', 0, (hi2-hi) * height)


    def onDrop(self, event):
        '''
        Drop the selected cards.  In order to recognize the destination tableau pile,
        the top of the cards being dragged must be below the bottom edge of
        the foundation piles, and the cards being dragged must overlap a tableau pile.
        If they overlap two tableau piles, both are considered, the one with more
        overlap first.  If that is not a legal drop target then the other tableau pile 
        is considered.
        '''
        model = self.model
        if not model.moving():
            return
        canvas = self.canvas
        canvas.configure(cursor=DEFAULT_CURSOR)

        try:    
            west, north, east, south = canvas.bbox(tk.CURRENT)
        except TypeError:
            pass                      # how can bbox(tk.CURRENT) give None?

        def findDestInArray(seq):   
            for k, w in enumerate(seq):
                left = w[0]       
                right = left + CARDWIDTH - 1
                if not (left <= west <= right or left <= east <= right ):
                    continue
                overlap1 = min(right, east) - max(left, west)
                try:
                    left = seq[k+1][0]
                except IndexError:
                    return (k, )
                right = left + CARDWIDTH - 1
                overlap2 = min(right, east) - max(left, west)
                if overlap2 <= 0:
                    return (k, )
                if overlap1 > overlap2:
                    return (k, k+1)
                return (k+1, k)
            return tuple() 

        if north > self.foundations[0][1]+CARDHEIGHT:
            for pile in findDestInArray(self.tableau):
                if pile == model.moveOrigin or not model.canDrop(pile):
                    continue
                self.completeMove(pile)
                break
            else:   # loop else
                self.abortMove()
        else:
            #check for drop on foundation pile
            for pile in findDestInArray(self.foundations):
                if model.canDrop(pile):
                    self.suitToFoundation(pile)
                    break
            else:     # loop else
                self.abortMove()

        self.show()

    def abortMove(self):
        self.model.abortMove()
        self.showtableau(self.model.moveOrigin)
        self.canvas.dtag('floating', 'floating')

    def completeMove(self, dest):
        model = self.model
        source = model.moveOrigin
        model.selectionTotableau(dest)
        self.show()
        self.dtag('floating', 'floating')

    def suitToFoundation(self, dest):
        model = self.model
        source = model.moveOrigin
        model.selectionToFoundation(dest)
        self.show()
        self.canvas.dtag('floating', 'floating')    





