# model.py Model for Napoleon at St. Helena (Forty Thieves) solitaire

import random, itertools

ACE = 1
JACK = 11
QUEEN = 12
KING = 13
ALLRANKS = range(1, 14)      # one more than the highest value

# RANKNAMES is a list that maps a rank to a string.  It contains a
# dummy element at index 0 so it can be indexed directly with the card
# value.

SUITNAMES = ('club', 'diamond', 'heart', 'spade')
RANKNAMES = ["", "Ace"] + list(map(str, range(2, 11))) + ["Jack", "Queen", "King"]
COLORNAMES = ("red", "blue")     # back colors

STOCK = 18
WASTE = 19

class Stack(list):
    '''
    A pile of cards.
    The base class deals with the essential facilities of a stack, and the derived 
    classes deal with presentation.

    The stack knows what cards it contains, but the card does not know which stack it is in.

    In reading the code you should realize that > and < for cards indicate successor and
    predecessor, so that Ace of Hearts < Two of Hearts, but no other card.
    '''
    def __init__(self):
        # Bottom card is self[0]; top is self[-1]
        super().__init__()

    def add(self, card, faceUp):
        self.append(card)
        if faceUp:
            self[-1].showFace()

    def isEmpty(self):
        return not self

    def clear(self):
        self[:] = []  
        
    def replace(self, cards):
        '''
        Move aborted.  Replace these cards on the stack.
        '''
        self.extend(cards)
        self.moving = None
        
    def find(self, code):
        '''
        If the card with the given code is in the stack,
        return its index.  If not, return -1.
        '''
        for idx, card in enumerate(self):
            if card.code == code:
                return idx
        return -1

class TableauPile(Stack):
    '''
    Cards can be chosen, if they are face up and in sequence, from the top of the pile.
    Cards can be dropped on the pile if the pile is empty, or is the top card of the pile
    is the successor of the bottom dropped card.
    All cards are face up.
    '''
    def __init__(self):
        super().__init__()

    def add(self, card):
        Stack.add(self, card, True)

    def canSelect(self, idx):
        if idx >= len(self):
            return False
        if not Card.isDescending(self[idx:]):
            return False 
        return True
    
    def drop(self, cards, limit):
        '''
        If legal, drop the cards on the pile.
        Return True if legal, else False
        '''
        if self.isEmpty():
            if len(cards) > limit//2:
                return False
        else:
            if len(cards) > limit or not (self[-1] > cards[0]):
                return False
        self.extend(cards)
        return True
        
class FoundationPile(Stack):
    '''
    No cards can be chosen.
    Cards can be dropped if the pile is empty and the top card is an Ace,
    '''    
    def __init__(self):
        super().__init__()
        
    def add(self, card):
        Stack.add(self, card, True)   

    def canSelect(self, idx):
        return False
    
    def drop(self, cards, _):
        '''
        If legal, drop the cards on the pile.
        Return True if legal, else False
        '''
        if self.isEmpty():
            if cards[-1].rank != ACE:
                return False
        else:
            if not (self[-1] < cards[-1]):
                return False
        self.extend(reversed(cards))
        return True    
        
class WastePile(Stack):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent # the model
        
    def add(self, card):
        Stack.add(self, card, True)      
        
    def canSelect(self, idx):
        return not self.isEmpty() and idx == len(self)-1   
    
    def drop(self, cards, _):
        model = self.parent
        if model.moveOrigin != model.stock:
            return False
        self.extend(cards)
        return True
            
class StockPile(Stack):
    def __init__(self):
        super().__init__()
        
    def add(self, card):
        Stack.add(self, card, False)      
        
    def canSelect(self, idx):
        return not self.isEmpty() and idx == len(self)-1   
    
    def drop(self, _a, _b):
        return False
    
class Card:
    '''
    A card is identified by its rank, suit, and back color.
    A card knows whether it is face up or own, but does not know 
    which stack it is in.
    '''
    def __init__(self, rank, suit, back):
        self.rank = rank
        self.suit = suit
        self.back = back
        self.up = False   # all cards are initially face down
        self.code = 52*COLORNAMES.index(back)+13*SUITNAMES.index(suit)+rank-1  

    def showFace(self):
        self.up = True

    def showBack(self):
        self.up = False

    def faceUp(self):
        return self.up

    def faceDown(self):
        return not self.faceUp()

    # Overloaded operators for predecessor and successor

    def __lt__(self, other):
        if self.suit != other.suit:
            return False
        answer = self.rank == other.rank-1 
        return answer 

    def __gt__(self, other):
        return other < self

    def __repr__(self):
        return '%s %s %s'%(self.suit, RANKNAMES[self.rank], self.back)

    def __str__(self):
        return __repr__(self)

    @staticmethod
    def isDescending(seq):
        '''
        Are the cards in a descending sequence of the same suit?
        '''
        return all(map(lambda x, y: x > y, seq, seq[1:]))  

class Model:
    '''
    The cards are all in self.deck, and are copied into the appropriate stacks:
        the stock
        the waste pile
        10 tableau piles, where all the action is
        8 foundation piles for completed suits
    The top card of the stock is face-up and available for play.  

      '''
    def __init__(self):
        random.seed()
        self.deck = []
        self.selection = []
        self.createCards()
        self.stock = StockPile()
        self.waste = WastePile(self)
        self.foundations = []
        for k in range(8):
            self.foundations.append(FoundationPile())
        self.tableau = []
        for k in range(10):
            self.tableau.append(TableauPile()) 
        self.grabPiles = [self.waste, self.stock]  # piles from which cards can be moved 
        self.grabPiles.extend(self.tableau)
        self.dropPiles = [self.waste] + self.tableau + self.foundations # drop on these piles
        self.deal()

    def shuffle(self):
        self.stock.clear()
        self.waste.clear()
        for f in self.foundations:
            f.clear()
        for w in self.tableau:
            w.clear()
        random.shuffle(self.deck)
        for card in self.deck:
            card.showBack()
        self.stock.extend(self.deck)

    def createCards(self):
        for rank, suit, back in itertools.product(ALLRANKS, SUITNAMES, COLORNAMES):
            self.deck.append(Card(rank, suit, back))
            
    def deal(self):
        '''
        Deal the cards into the initial layout
        '''
        self.shuffle()
        for n in range(40):
            card = self.stock.pop()
            self.tableau[n%10].add(card)
        self.flipTop()   # turn top card of stock face up

    def grab(self, pile, idx):
        '''
        Initiate a move to a tableau or foundation pile
        Return code numbers of the selected cards.
        We need to remember the data, since the move may fail.
        '''
        if not pile.canSelect(idx):
            return []
        self.moveOrigin = pile
        self.moveIndex = idx
        self.selection = pile[idx:]
        return self.selection

    def abortMove(self):
        self.selection = []

    def moving(self):
        return self.selection != [] 

    def getSelected(self):
        return self.selection

    def canDrop(self, pile):
        '''
        Can the moving cards be dropped on pile? 
        Here we implement "supermoves."  If the target tableau pile is not empty, 
        the number of cards moved must not exceed the 2 to the number
        of empty piles.  If the target tableau pile is empty, the maximum is half
        that limit.
        If the target is a foundation pile, there is no limit.
        '''
        if not self.selection:
            return False 
        if isinstance(pile, StockPile):
            return False
        if pile in self.tableau:
            limit = 2 ** len([t for t in self.tableau if not t])
        else:
            limit = 13
        return pile.drop(self.selection, limit)

    def completeMove(self, dest):
        '''
        Compete a legal move.
        Transfer the moving cards to the destination stack.
        Turn the top card of the stock face up, if need be.
        '''
        source = self.moveOrigin
        source[:] = source[:self.moveIndex]
        self.flipTop()
        self.selection = []

    def flipTop(self):
        '''
        Turn the top card of stock face up
        '''
        w = self.stock
        try:
            if w[-1].faceDown():
                w[-1].showFace()
        except IndexError:
            pass

    def win(self):
        return all((len(f) == 13 for f in self.foundations)) 



  

