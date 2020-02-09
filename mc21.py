#!/usr/bin/env python3
import os, random, time, statistics, matplotlib
import matplotlib.pyplot as plt
import numpy as np
from multiprocessing import Process, Pool
from enum import IntEnum
from tqdm import tqdm


VALS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10','J', 'Q', 'K']
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

class Status(IntEnum):
    STAND = 0
    PLAY = 1

class Player(object):
    def __init__(self, balence, deck, used_cards, cards_showing):
        self.hand = []
        self.status = Status.PLAY
        self.wager = 0
        self.balence = balence
        self.deck = deck
        self.used_cards = used_cards
        self.cards_showing = cards_showing
    def reshuffle(self):
        self.deck.extend(self.used_cards)
        random.shuffle(self.deck)
        rand_index = 8 + random.randint(-4, 4)
        blank_card = Card('Plastic', 'Blank')
        self.deck.insert(rand_index, blank_card)
    def set_wager(self, wager):
        self.wager = wager
    def hit(self):
        card = self.deck.pop()
        if card.val is 'Blank':
            self.reshuffle()
            card = self.deck.pop()
        self.hand.append(card)
        if not (isinstance(self, Dealer) and len(self.hand) == 2):
            self.cards_showing.append(card)
    def win(self, mult=1.0):
        self.balence += self.wager*mult
    def lose(self, mult=1.0):
        self.balence -= self.wager*mult
    def disp_hand(self):
        for card in self.hand:
            print(card)
    def hand_val(self, hard=False):
        """ returns the value of hand
        if hard is true Aces are 1 otherwise Aces are 11 """
        val = 0
        for card in self.hand:
            if card.val == 'K' or card.val == 'Q' or card.val == 'J':
                val += 10
            elif card.val == 'A' and not hard:
                val += 11
            elif card.val == 'A' and hard:
                val += 1
            else:
                val += int(card.val)
        return val
    def best_hand_val(self):
        """ returns most favorable value of hand """
        if self.hand_val(hard=True) > 21:
            return 0
        if self.hand_val() <= 21:
            return self.hand_val()
        return self.hand_val(hard=True)
    def has_blackjack(self):
        return self.hand_val() == 21 and len(self.hand) == 2
    def move(self):
        """ Implemented in child classes only """
        raise NotImplementedError

class Dealer(Player):
    def __init__(self, deck, used_cards, cards_showing):
        self.hand = []
        self.status = Status.PLAY
        self.deck = deck
        self.used_cards = used_cards
        self.cards_showing = cards_showing
    def move(self):
        if self.best_hand_val() >= 17 or self.best_hand_val() == 0:
            self.status = Status.STAND
        else:
            self.hit()

class UIPlayer(Player):
    def __init__(self, balence):
        super().__init__(balence)
    def move(self):
        s = input('S to stand, H to hit: ').lower()
        if s == 's':
            self.status = Status.STAND
        elif s == 'h':
            self.hit()
        else:
            print('Must enter S or H')

class SimplePlayer(Player):
    def __init__(self, balence, deck, used_cards, cards_showing):
        super().__init__(balence, deck, used_cards, cards_showing)
    def move(self):
        if self.best_hand_val() >= 17 or self.best_hand_val() == 0:
            self.status = Status.STAND
        else:
            self.hit()

class CCPlayer(Player):
    """ Card Counting Player """
    pass # TODO

def deal_cards(players):
    for i in range(2):
        for player in players:
            player.hit()

def clear_table(players):
    cards_showing = []
    for player in players:
        player.status = Status.PLAY
        while len(player.hand):
            player.used_cards.append(player.hand.pop())

def print_UI(dealer, player1, dealer_move=False):
    os.system('cls' if os.name == 'nt' else 'clear')
    print('Balence:', player1.balence)
    print('Wager:', player1.wager, '\n')
    if dealer_move:
        print('Dealer showing:', best_hand_val(dealer.hand))
        dealer.disp_hand()
        print()
    else:
        print('Dealer showing:\n'+str(dealer.hand[0]), '\n')
    print('Your hand:', best_hand_val(player1.hand))
    player1.disp_hand()

def UImain():
    player1 = UIPlayer(200)
    dealer = Dealer()
    while player1.balence > 0:
        os.system('cls' if os.name == 'nt' else 'clear')
        print('Balence:', player1.balence)
        s = int(input('Place wager amount: '))
        player1.set_wager(s)
        deal_cards([dealer, player1])

        # UI player loop
        while (player1.status != Status.STAND):
            print_UI(dealer, player1)
            player1.move()

        while dealer.status != Status.STAND:
            print_UI(dealer, player1, dealer_move=True)
            dealer.move()
            time.sleep(1)
        print_UI(dealer, player1, dealer_move=True)

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

def simulate_trial(num_hands):
    """ returns balence_log array for player one during simulated number of hands """
    balence_log = []
    # init cards 
    used_cards = []
    cards_showing = []
    deck = []
    for decks in range(8):
        for val in VALS:
            for suit in SUITS:
                deck.append(Card(suit, val))
    random.shuffle(deck)
    blank_card = Card('Plastic', 'Blank')
    rand_index = 8 + random.randint(-4,4)
    deck.insert(rand_index, blank_card)


    player1 = SimplePlayer(0, deck, used_cards, cards_showing)
    dealer = Dealer(deck, used_cards, cards_showing)
    players = [player1]
    for j in range(num_hands):
        deal_cards([dealer] + players)
        balence_log.append(player1.balence)

        # set wager
        for player in players:
            player.set_wager(1)

        # player loop
        while sum([player.status for player in players]):
            for player in players:
                if player.status == Status.STAND:
                    continue
                player.move()

        # dealer loop
        while dealer.status != Status.STAND:
            dealer.move()

        # eval hands
        dealer_hand_val = dealer.best_hand_val()
        for player in players:
            p_hand_val = player.best_hand_val()
            if p_hand_val > 21 or p_hand_val <= 0:
                player.lose()
            elif player.has_blackjack() and not dealer.has_blackjack(): 
                player.win()
            elif not player.has_blackjack() and dealer.has_blackjack(): 
                player.lose()
            elif p_hand_val > dealer_hand_val:
                player.win()
            elif p_hand_val < dealer_hand_val:
                player.lose()

        clear_table([dealer]+players)

    return balence_log

def main():
    # the great question:
    # how many trials do we need to have enough confidence?
    TRIALS = 20
    HANDS = 35
    winnings = np.empty([TRIALS, HANDS])
    with Pool() as pool:
        winnings = pool.map(simulate_trial, [HANDS]*TRIALS)
    
    winnings = np.array(winnings)

    # plot all simulated games
    t = np.arange(0, HANDS)
    for i in range(TRIALS):
        plt.plot(t, winnings[:][i])
    plt.title(str(TRIALS)+' simulated games')
    plt.xlabel('Number of hands played')
    plt.ylabel('Balence')
    plt.show()

    # plot average 
    t = np.arange(0, HANDS)
    avg = np.mean(winnings, axis=0)
#    plt.plot(t, avg)
#    plt.title('Average Balence')
#    plt.xlabel('Number of hands played')
#    plt.ylabel('$')
#    plt.show()

    # plot 95% confidence interval
    ci95 = np.std(winnings, axis=0)*1.96
#    plt.plot(t, ci95)
#    plt.title('95% confidence interval')
#    plt.ylabel('$')
#    plt.xlabel('Number of hands played')
#    plt.show()

#    plt.plot(t, avg, t, avg-ci95, t, avg+ci95)
#    plt.title('Average balence with 95% confidence interval bounds')
#    plt.ylabel('$')
#    plt.xlabel('Number of hands played')
#    plt.show()

if __name__ == '__main__':
    main()
