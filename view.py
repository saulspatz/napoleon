# view.py
'''
The visual interface for Napoleon at St. Helelna solitaire.
The view knows about the model, but not vice versa
Thce canvas widget is used for both view and controller.
'''
import sys, os, itertools
import tkinter as tk
import tkinter.messagebox as tkmb
from model import SUITNAMES, RANKNAMES, ALLRANKS, Card

# Constants determining the size and layout of cards piles.
# Adjacent stacks are separated by MARGIN pixels
# OFFSET is the offset used for displaying the
# a card to the right of another in the tableau.

CARDWIDTH = 71
CARDHEIGHT = 96
MARGIN = 10
OFFSET = 15

BACKGROUND = '#070'
OUTLINE = 'orange'        # outline color of piles
CELEBRATE = 'yellow'     # Color of "you won" message

# Cursors
DEFAULT_CURSOR = 'arrow'
SELECT_CURSOR = 'hand2'

STATUS_FONT = ('Helvetica', '14', 'normal')
STATUS_BG = 'gray'

imageDict = {}   # hang on to images, or they may disappear!

class View: 
    '''
    Cards are represented as canvas image items,  displaying either the face
    or the back as appropriate.  Each card has the tag "card".  This is 
    crucial, since only canvas items tagged "card" will respond to mouse
    clicks.
    '''
    def __init__(self, parent, quit, deck, **kwargs):
        # kwargs passed to Canvas
        # quit is function to call when main window is closed
        # deck is directory with card images
        self.parent = parent          # parent is the Napoleon application
        self.model =  parent.model
        self.root = root = tk.Tk()
        self.deck = tk.StringVar(value=deck)
        root.protocol('WM_DELETE_WINDOW', quit)
        root.resizable(height=False, width=False)
        width = kwargs['width']
        height = kwargs['height']
        self.root.wm_geometry('%dx%d-10+10'%(width,height))
        root.title("Napoleon at St. Helena Solitaire")
        self.menu = tk.Menu(root)         # parent constructs actual menu         
        root.config(menu=self.menu)                         
        status = self.makeStatus()
        canvas = self.canvas = tk.Canvas(root, bg=BACKGROUND, cursor=DEFAULT_CURSOR, **kwargs)
        status.pack(expand=tk.NO, fill = tk.X, side=tk.BOTTOM)
        canvas.pack()
        self.loadImages()
        self.createCards()      
        self.makePiles(width, height)
        self.makeMessages(width, height)
        canvas.tag_bind("card", '<ButtonPress-1>', self.onClick)
        canvas.bind('<B1-Motion>', self.drag)
        canvas.bind('<ButtonRelease-1>', self.onDrop)
        self.makeButtons()
        self.hideMessages()
        self.show()
        
    def makeButtons(self):
        canvas = self.canvas
        BUTTON = 'Forest Green'
        x = MARGIN
        y = self.waste[1]
        canvas.create_oval(x, y, x+6*MARGIN, y+3*MARGIN, 
                        fill = BUTTON, outline = BUTTON, tag = 'newDeal')        
        canvas.create_text(x+3*MARGIN, y + 3*MARGIN/2, text = 'New Deal', 
                           fill = CELEBRATE, tag='newDeal', anchor=tk.CENTER)
        canvas.tag_bind('newDeal', '<ButtonRelease-1>', self.newDeal)
        x= 9*MARGIN
        canvas.create_oval(x, y, x+6*MARGIN, y+3*MARGIN, 
                        fill = BUTTON, outline = BUTTON, tag = 'help')        
        canvas.create_text(x+3*MARGIN, y + 3*MARGIN/2, text = 'Help', 
                           fill = CELEBRATE, tag='help', anchor=tk.CENTER)
        canvas.tag_bind('help', '<ButtonRelease-1>', self.parent.showHelp)        
        
    def makePiles(self, width, height):
        self.tableau = []           # NW corners of the tableau piles
        self.foundations = []   # NW corners of the foundation piles
        x = MARGIN
        y = 3* MARGIN        
        for k in range(8):
            x += MARGIN + CARDWIDTH
            self.foundations.append((x, y)) 
        y = 5*MARGIN + CARDHEIGHT
        x = MARGIN
        for k in range(5):
            self.tableau.append((x, y)) 
            y += 2*MARGIN + CARDHEIGHT
        x = width//2 - MARGIN
        y = 5*MARGIN + CARDHEIGHT
        for k in range(5):
            self.tableau.append((x, y)) 
            y += 2*MARGIN + CARDHEIGHT 
        x = width - 4*MARGIN - 2*CARDWIDTH
        self.stock = (x,y)   # NW corner of stock
        x += 2*MARGIN + CARDWIDTH
        self.waste = (x, y) #NW corner of waste
        self.grabPiles = [self.waste, self.stock]  # reflects model.grabPiles
        self.grabPiles.extend(self.tableau)
        self.dropPiles = [self.waste] + self.tableau + self.foundations
        canvas = self.canvas
        for w in self.tableau:
            canvas.create_rectangle(w[0]+2, w[1]+2, w[0]+CARDWIDTH-2, w[1]+CARDHEIGHT-2, outline = OUTLINE)    
        for f in self.foundations:
            canvas.create_rectangle(f[0]+2, f[1]+2, f[0]+CARDWIDTH-2, f[1]+CARDHEIGHT-2, outline = OUTLINE)
        w = self.waste
        canvas.create_rectangle(w[0]+2, w[1]+2, w[0]+CARDWIDTH-2, w[1]+CARDHEIGHT-2, outline = OUTLINE) 
        w = self.stock
        canvas.create_rectangle(w[0]+2, w[1]+2, w[0]+CARDWIDTH-2, w[1]+CARDHEIGHT-2, 
                                outline = OUTLINE, fill = 'orange', tag = 'stock')         
        canvas.create_text(w[0]+CARDWIDTH//2, w[1]+CARDHEIGHT//2,
                           text='Next\nPass', fill = 'Black', anchor=tk.CENTER, font = ('Helvetica', '20', 'normal'),
                           tags = ('stock', 'pass2Text'))
        canvas.tag_bind('stock', '<ButtonRelease-1>', self.turnStock)
        
        
    def makeStatus(self):
        status = tk.Frame(self.root, bg = STATUS_BG) 
        self.games = tk.Label(status, 
                                     relief = tk.RIDGE, font = STATUS_FONT, bg = STATUS_BG, fg = 'Black', bd = 2)
        self.wins = tk.Label(status, 
                                     relief = tk.RIDGE, font = STATUS_FONT, bg = STATUS_BG, fg = 'Black', bd = 2)
        self.passNumber =   tk.Label(status, 
                                     relief = tk.RIDGE, font = STATUS_FONT, bg = STATUS_BG, fg = 'Black', bd = 2)
        self.tableauCards =  tk.Label(status, 
                                      relief = tk.RIDGE, font = STATUS_FONT, bg = STATUS_BG, fg = 'Black', bd = 2)
        self.foundationCards =  tk.Label(status, 
                                         relief = tk.RIDGE, font = STATUS_FONT, bg = STATUS_BG, fg = 'Black', bd = 2)
        self.wasteCards = tk.Label(status, 
                                   relief = tk.RIDGE, font = STATUS_FONT, bg = STATUS_BG, fg = 'Black', bd = 2)
        self.stockCards = tk.Label(status, 
                                   relief = tk.RIDGE, font = STATUS_FONT, bg = STATUS_BG, fg = 'Black', bd = 2)
        self.games.pack(expand=tk.NO, fill = tk.NONE, side = tk.LEFT) 
        self.wins.pack(expand=tk.NO, fill = tk.NONE, side = tk.LEFT)  
        self.passNumber.pack(expand=tk.NO, fill = tk.NONE, side = tk.RIGHT)
        self.tableauCards.pack(expand=tk.NO, fill = tk.NONE, side = tk.RIGHT)
        self.foundationCards.pack(expand=tk.NO, fill = tk.NONE, side = tk.RIGHT)
        self.wasteCards.pack(expand=tk.NO, fill = tk.NONE, side = tk.RIGHT)
        self.stockCards.pack(expand=tk.NO, fill = tk.NONE, side = tk.RIGHT) 
        return status
   
    def start(self):
        self.root.mainloop()
        
    def activateStock(self, active = True):
        canvas = self.canvas
        if active:
            canvas.tag_bind('stock', '<ButtonRelease-1>', self.turnStock)
            canvas.itemconfigure('pass2Text', fill='black') 
        else:
            canvas.tag_unbind('stock', '<ButtonRelease-1>')
            canvas.itemconfigure('pass2Text', fill='orange')             
                
    def newDeal(self, event):
        if not self.model.gameOver():
            answer = tkmb.askokcancel(title='Abandon Game?', 
                                              message= 'Game is not over.  You still have moves.',
                                              icon = tkmb.QUESTION, 
                                              default = tkmb.CANCEL )
            if not answer: return   # user chose 'Cancel'
        canvas = self.canvas
        self.activateStock()
        self.hideMessages()
        self.model.deal()
        self.show()
        
    def makeMessages(self, width, height):
        canvas = self.canvas
        canvas.create_text(width//2, height//2, text = "YOU WIN",
                           fill = BACKGROUND, font=("Helvetica", "64", "bold"), 
                           tag = 'winText', anchor=tk.CENTER)
        canvas.create_text(width//2 , self.waste[1] + MARGIN,
                           text = 'No More Moves.  Game Over.',
                           fill = BACKGROUND, font = ('Helvetica', '32', 'bold'),
                           tag = 'gameOver', anchor = tk.CENTER)        
        
    def hideMessages(self):
        canvas =self.canvas
        for tag in ('winText','gameOver'):
            canvas.itemconfigure(tag, fill = BACKGROUND)
            canvas.tag_lower(tag, 'all')
    
    def showMessage(self, tag):
        canvas = self.canvas
        canvas.itemconfigure(tag, fill=CELEBRATE)
        canvas.tag_raise(tag, 'all')        
        

    def loadImages(self):
        PhotoImage = tk.PhotoImage
        deck = self.deck.get()
        blue = PhotoImage(file=os.path.join(deck,'blueBackVert.gif'))
        red = PhotoImage(file=os.path.join(deck,'redBackVert.gif'))
        imageDict['blue'] = blue
        imageDict['red'] = red    
        for rank, suit in itertools.product(ALLRANKS, SUITNAMES):
            face = PhotoImage(file = os.path.join(deck, suit+RANKNAMES[rank]+'.gif'))               
            imageDict[rank, suit] = face

    def createCards(self):
        model = self.model
        canvas = self.canvas   
        for card in model.deck:
            c = canvas.create_image(-200, -200, image = None, anchor = tk.NW, tag = "card")
            canvas.addtag_withtag('code%d'%card.code, c)
            
    def showPile(self, pileView, pileModel, xOffset, yOffset):
        x,y = pileView
        canvas = self.canvas
        for card in pileModel:
            tag = 'code%d'%card.code
            canvas.coords(tag, x, y)
            if card.faceUp():
                foto = imageDict[card.rank, card.suit]
                x += xOffset
                y += yOffset
            else:
                foto = imageDict[card.back]
                x += xOffset
                y += yOffset
            canvas.itemconfigure(tag, image = foto)
            canvas.tag_raise(tag)
            
    def showSquaredPile(self, pileView, pileModel):
        self.showPile(pileView, pileModel, 0, 0)
        
    def showStatus(self):
        model = self.model
        self.games.configure(text='Games %d'%model.games)
        self.wins.configure(text='Wins %d'%model.wins)
        self.passNumber.configure(text='Pass %d'%model.passNumber)
        self.wasteCards.configure(text='Waste %d'%len(model.waste))
        self.tableauCards.configure(text='Tableau %d'%sum(len(t) for t in model.tableau))
        self.stockCards.configure(text='Stock %d'%len(model.stock))
        self.foundationCards.configure(text='Foundation %d'%sum(len(f) for f in model.foundations))                

    def show(self):
        self.showStock()
        self.showTableaux()
        self.showFoundations()
        self.showWaste()
        if self.model.win():
            self.showMessage('winText')
        elif self.model.gameOver():
            self.showMessage('gameOver')
        self.showStatus()

    def dealUp(self):
        self.model.dealUp()
        self.show()

    def showTableaux(self):
        for v, m in zip(self.tableau, self.model.tableau):
            self.showPile(v, m, OFFSET, 0)
            
    def showFoundations(self):
        for v,m in zip(self.foundations, self.model.foundations):
            self.showSquaredPile(v,m)
            
    def showStock(self):
        self.showSquaredPile(self.stock, self.model.stock)
        
    def showWaste(self):
        self.showSquaredPile(self.waste, self.model.waste)

    def grab(self, selection, pile, mouseX, mouseY):
        '''
        Grab the cards in selection.
        '''
        canvas = self.canvas
        if not selection:
            return
        self.mouseX, self.mouseY = mouseX, mouseY
        west = pile[0]
        for card in selection:
            tag = 'code%s'%card.code
            canvas.tag_raise(tag)
            canvas.addtag_withtag("floating", tag)
        canvas.configure(cursor=SELECT_CURSOR)
        dx = 5 if mouseX - west > 10 else -5
        canvas.move('floating', dx, 5)

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
        for mgp, vgp in zip(model.grabPiles, self.grabPiles):
            idx = mgp.find(code)
            if idx != -1:
                break
        else:       # loop else
            return
        selection = model.grab(mgp, idx)
        if selection:
            canvas.addtag_withtag('moveBase', tag)
            self.grab(selection, vgp, event.x, event.y)  

    def onDrop(self, event):
        '''
        Drop the selected cards.  In order to recognize the destination pile,
        the cards being dragged must overlap the pile.
        If they overlap more than one pile, all are considered in decreasing order
        of overlap.  The first legal drop target encountered is accepted.
        '''
        model = self.model
        if not model.moving():
            return
        canvas = self.canvas
        canvas.configure(cursor=DEFAULT_CURSOR)

        try:    
            west, north, east, south = canvas.bbox('moveBase')
        except TypeError:
            self.abortMove()                 
        
        def findDest(): 
            overlaps = []
            tableau = model.tableau
            for vdp, mdp in zip(self.dropPiles, model.dropPiles):
                left = vdp[0] 
                top = vdp[1]
                if mdp not in tableau:
                    cards = 1
                else:
                    cards = max(len(mdp), 1)
                right = left + (cards-1)*OFFSET + CARDWIDTH - 1
                bottom = top + CARDHEIGHT - 1
                if not (left <= west <= right or left <= east <= right ):
                    continue
                if not (top <= north <= bottom or top <= south <= bottom):
                    continue
                overlapX = min(right, east) - max(left, west)
                overlapY = min(south, bottom) - max(north, top)
                overlap = overlapX * overlapY
                overlaps.append((overlap, mdp))
            answer =  [s[1] for s in sorted(overlaps, reverse=True)]  
            return answer
        
        for pile in findDest():
            if model.canDrop(pile):
                model.completeMove(pile)
                self.completeMove()
                break
        else:           # loop else
            self.abortMove()
        self.show()

    def abortMove(self):
        self.model.abortMove()
        self.show()
        self.canvas.dtag('floating', 'floating')
        self.canvas.dtag('moveBase', 'moveBase')

    def completeMove(self):
        self.show()
        self.canvas.dtag('floating', 'floating')
        self.canvas.dtag('moveBase', 'moveBase')
        
    def turnStock(self, event):
        canvas = self.canvas
        self.model.nextPass()
        self.activateStock(False)
        self.show()
        
                
        
 