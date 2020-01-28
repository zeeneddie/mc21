#!/usr/bin/env python3
import os, random
from enum import IntEnum

VALS = ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'King',
    'Queen', 'Jack']
SUITS = ['Clubs', 'Heart', 'Diamond', 'Spades']

class Card(object):
    def __init__(self, suit, val):
        self.suit = suit
        self.val = val
    def __str__(self):
        return str(self.val) + ' of ' + str(self.suit)

deck = []
for decks in range(1): # FIXME: should be 8 decks
    for val in VALS:
        for suit in SUITS:
            deck.append(Card(suit, val))
random.shuffle(deck)
blank_card = Card('Plastic', 'Blank')
rand_index = 20 + random.randint(-10,10)
deck.insert(rand_index, blank_card)

used_cards = []
cards_showing = []

def reset(players):
    for player in players:
        while len(player.hand):
            used_cards.append(player.hand.pop())
        player.status = Status.PASS
    cards_showing = []
    
def reshuffle():
    deck.extend(used_cards)
    random.shuffle(deck)
    rand_index = 20 + random.randint(-10,10)
    deck.insert(rand_index, blank_card)
    
def hand_val(hand, hard=False):
    val = 0
    for card in hand:
        if card.val == 'King' or card.val == 'Queen' or card.val == 'Jack':
            val += 10
        elif card.val == 'Ace' and not hard:
            val += 11
        elif card.val == 'Ace' and hard:
            val += 1
        else:
            val += int(card.val)
    return val

def better_hand(hand1, hand2):
    if hand_val(hand1) > 21:
        h1 = hand_val(hand1, hard=True)
    else:
        h1 = hand_val(hand1)
    if hand_val(hand2) > 21:
        h2 = hand_val(hand2, hard=True)
    else:
        h2 = hand_val(hand2)
    if h1 > h2 and h1 <= 21:
        return True
    else:
        return False

class Status(IntEnum):
    STAND = 0
    PASS = 1

class Player(object):
    def __init__(self):
        self.hand = []
        self.status = Status.PASS
    def hit(self):
        card = deck.pop()
        if card is blank_card:
            reshuffle()
            card = deck.pop()
        self.hand.append(card)
        if not (isinstance(self, Dealer) and len(self.hand) == 2):
            cards_showing.append(card)
    def move(self):
        raise NotImplementedError

class Dealer(Player):
    def __init__(self):
        super().__init__()
    def move(self):
        if hand_val(self.hand) >= 17:
            self.status = Status.STAND
        else:
            self.hit()

class UIPlayer(Player):
    def __init__(self, balence):
        super().__init__()
        self.balence = balence
        self.wager = 0
    def set_wager(self,wager):
        self.wager = wager
    def move(self):
        s = input('S to stand, H to hit: ').lower()
        if s == 's':
            self.status = Status.STAND
        elif s == 'h':
            self.hit()
        else:
            print('Must enter S or H')

def deal_cards(players):
    for i in range(2):
        for player in players:
            player.hit()

def clear_table(players):
    for player in players:
        while len(player.hand):
            used_cards.append(player.hand.pop())
def main():
    player1 = UIPlayer(1000)
    dealer = Dealer()
    while player1.balence > 0:
        os.system('cls' if os.name == 'nt' else 'clear')
        print('Balence:', player1.balence)
        s = int(input('Place wager amount: '))
        player1.set_wager(s)
        deal_cards([dealer, player1])
        while player1.status != Status.STAND:
            if isinstance(player1, UIPlayer):
                os.system('cls' if os.name == 'nt' else 'clear')
                print('Balence:', player1.balence)
                print('Wager:', player1.wager, '\n')
                print('Dealer showing:\n'+str(dealer.hand[0]), '\n')
                print('Your hand:')
                for card in player1.hand:
                    print(card)
                print('\nCards on table:')
                for card in cards_showing:
                    print(card)
                print('\nUsed cards:')
                for card in used_cards:
                    print(card)
            player1.move()
        while dealer.status != Status.STAND:
            dealer.move()
        print('\nDealers hand:')
        for card in dealer.hand:
            print(card)
        if better_hand(dealer.hand, player1.hand):
            print('You lost', player1.wager)
            player1.balence -= player1.wager
        if better_hand(player1.hand, dealer.hand):
            print('You won', player1.wager)
            player1.balence += player1.wager
        input('\nhit any key to continue ')
        reset([dealer, player1])

if __name__ == '__main__':
    main()
