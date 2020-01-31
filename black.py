#!/usr/bin/env python3
import os, random, time
from enum import IntEnum

VALS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Q', 'J', 'K']
SUITS = ['Clubs', 'Heart', 'Diamond', 'Spades']

class Card(object):
    def __init__(self, suit, val):
        self.suit = suit
        self.val = val
    def __str__(self):
        if self.val == 'Blank':
            return 'BLANK'
        if self.suit == 'Clubs':
            suit = '♣'
        elif self.suit == 'Heart':
            suit = '♥'
        elif self.suit == 'Diamond':
            suit = '♦'
        elif self.suit == 'Spades':
            suit = '♠'
        return str(self.val) + ' ' + suit

deck = []
for decks in range(1): # FIXME: should be 8 decks
    for val in VALS:
        for suit in SUITS:
            deck.append(Card(suit, val))
random.shuffle(deck)
blank_card = Card('Plastic', 'Blank')
rand_index = 7 + random.randint(-5,5)
deck.insert(rand_index, blank_card)

used_cards = []
cards_showing = []

def reshuffle():
    deck.extend(used_cards)
    random.shuffle(deck)
    rand_index = 20 + random.randint(-10,10)
    deck.insert(rand_index, blank_card)
    
def hand_val(hand, hard=False):
    val = 0
    for card in hand:
        if card.val == 'K' or card.val == 'Q' or card.val == 'J':
            val += 10
        elif card.val == 'A' and not hard:
            val += 11
        elif card.val == 'A' and hard:
            val += 1
        else:
            val += int(card.val)
    return val

def best_hand_val(hand):
    if hand_val(hand, hard=True) > 21:
        return 0
    if hand_val(hand) <= 21:
        return hand_val(hand) 
    return hand_val(hand, hard=True)

class Status(IntEnum):
    STAND = 0
    PASS = 1

class Player(object):
    def __init__(self):
        self.hand = []
        self.status = Status.PASS
    def hit(self):
        card = deck.pop()
        if card.val is 'Blank':
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
        if best_hand_val(self.hand) >= 17 or best_hand_val(self.hand) == 0:
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
    cards_showing = []
    for player in players:
        player.status = Status.PASS
        while len(player.hand):
            used_cards.append(player.hand.pop())

def print_UI(dealer, player1, dealer_move=False):
    os.system('cls' if os.name == 'nt' else 'clear')
    # for card in deck:
    #     print(card)
    print('Balence:', player1.balence)
    print('Wager:', player1.wager, '\n')
    if dealer_move:
        print('Dealer showing:', best_hand_val(dealer.hand))
        for card in dealer.hand:
            print(card)
        print()
    else:
        print('Dealer showing:\n'+str(dealer.hand[0]), '\n')
    print('Your hand:', best_hand_val(player1.hand))
    for card in player1.hand:
        print(card)

def main():
    player1 = UIPlayer(200)
    dealer = Dealer()
    while player1.balence > 0:
        os.system('cls' if os.name == 'nt' else 'clear')
        print('Balence:', player1.balence)
        s = int(input('Place wager amount: '))
        player1.set_wager(s)
        deal_cards([dealer, player1])

        # UI player loop
        if isinstance(player1, UIPlayer):
            while (player1.status != Status.STAND and
                    hand_val(player1.hand, hard=True) < 21):
                print_UI(dealer, player1)
                player1.move()

        # automated player loop TODO

        # dealer plays loop
        while dealer.status != Status.STAND:
            print_UI(dealer, player1, dealer_move=True)
            time.sleep(1)
            dealer.move()
        dealer_hand_val = best_hand_val(dealer.hand)
        player1_hand_val = best_hand_val(player1.hand)
        if dealer_hand_val > player1_hand_val:
            print('You lose', player1.wager)
            player1.balence -= player1.wager
        if dealer_hand_val < player1_hand_val:
            print('You win', player1.wager)
            player1.balence += player1.wager
        input('\nhit any key to continue ')
        clear_table([dealer, player1])

if __name__ == '__main__':
    main()
