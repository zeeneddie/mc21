#!/usr/bin/env python3
import random, os, time
import matplotlib.pyplot as plt
import numpy as np
from multiprocessing import Pool
from blackjack import Card, Status, Player, Dealer, UIPlayer, SimplePlayer
from blackjack import BasicStratPlayer, CCPlayer, HLPlayer, deal_cards
from blackjack import clear_table, print_UI

TRIALS = 1000
HANDS = 16000
VALS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10','J', 'Q', 'K']
SUITS = ['Clubs', 'Heart', 'Diamond', 'Spades']

def UImain():
    used_cards = []
    cards_showing = []
    deck = []
    for decks in range(1):
        for val in VALS:
            for suit in SUITS:
                deck.append(Card(suit, val))
    random.shuffle(deck)
    blank_card = Card('Plastic', 'Blank')
    rand_index = 8 + random.randint(-4,4)
    deck.insert(rand_index, blank_card)

    player1 = UIPlayer(200.0, deck, used_cards, cards_showing)
    dealer = Dealer(deck, used_cards, cards_showing)
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

        dealer_hand_val = dealer.best_hand_val()
        p_hand_val = player1.best_hand_val()

        if p_hand_val > 21 or p_hand_val <= 0:
            print('You lose', player1.wager)
            player1.lose()
        elif player1.has_blackjack() and not dealer.has_blackjack():
            print('You win', player1.wager)
            player1.win()
        elif not player1.has_blackjack() and dealer.has_blackjack():
            print('You lose', player1.wager)
            player1.lose()
        elif p_hand_val > dealer_hand_val:
            print('You win', player1.wager)
            player1.win()
        elif p_hand_val < dealer_hand_val:
            print('You lose', player1.wager)
            player1.lose()

        input('\nhit any key to continue ')
        clear_table([dealer, player1])

def simulate_trial(num_hands):
    """ returns balence_log array for player one during simulated number of hands """
    balence_log = []
    # init cards 
    used_cards = []
    cards_showing = []
    deck = []
    for _ in range(8):
        for val in VALS:
            for suit in SUITS:
                deck.append(Card(suit, val))
    random.shuffle(deck)
    blank_card = Card('Plastic', 'Blank')
    rand_index = 8 + random.randint(-4,4)
    deck.insert(rand_index, blank_card)

    dealer = Dealer(deck, used_cards, cards_showing)
    # player1 = SimplePlayer(0, deck, used_cards, cards_showing)
    player1 = BasicStratPlayer(0, deck, used_cards, cards_showing, dealer)
    # player1 = HLPlayer(0, deck, used_cards, cards_showing, dealer)

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
            # no split
            if len(player.split_hand) == 0:
                p_hand_val = player.best_hand_val()
                if p_hand_val > 21 or p_hand_val <= 0:
                    player.lose()
                elif player.has_blackjack() and not dealer.has_blackjack():
                    player.win(1.5)
                elif not player.has_blackjack() and dealer.has_blackjack():
                    player.lose()
                elif p_hand_val > dealer_hand_val:
                    player.win()
                elif p_hand_val < dealer_hand_val:
                    player.lose()
            # split hands
            else:
                for i in range(2):
                    if i == 1:
                        player.hand = player.split_hand
                        player.set_wager(player.split_wager)
                    p_hand_val = player.best_hand_val()
                    if p_hand_val > 21 or p_hand_val <= 0:
                        player.lose()
                    elif p_hand_val > dealer_hand_val:
                        player.win()
                    elif p_hand_val < dealer_hand_val:
                        player.lose()

        clear_table([dealer]+players)
    return balence_log

def main():
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
    t = np.arange(0, HANDS)
    avg = np.mean(winnings, axis=0)
    ci95 = np.std(winnings, axis=0)*1.96 # 95% confidence interval
    plt.plot(t, avg, 'k', t, avg-ci95, 'k--', t, avg+ci95, 'k--')
    plt.xlabel('Number of hands played')
    print('exp return:', str(round((avg[-1]/HANDS*100), 4))+' +/-'
            +str(round((ci95[-1]/HANDS*100), 4))+'%')
    plt.show()

if __name__ == '__main__':
    main()
