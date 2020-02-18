#!/usr/bin/env python3
"""
Classes and functions for Blackjack simulations and game
"""
from enum import IntEnum
import random, os

class Card(object):
    def __init__(self, suit, val):
        self.suit = suit
        self.val = val
    def get_num_val(self, hard=False):
        if self.val == 'Blank':
            raise ValueError('Cannot evaluate card with value', self.val)
        if self.val == 'A':
            if hard:
                return 1
            else:
                return 11
        if self.val == 'J' or self.val == 'Q' or self.val == 'K':
            return 10
        return int(self.val)
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
    SPLIT_1 = 2
    SPLIT_2 = 3

class Player(object):
    def __init__(self, balence, deck, used_cards, cards_showing):
        self.hand = []
        self.split_hand = []
        self.status = Status.PLAY
        self.wager = 0
        self.split_wager = 0
        self.balence = balence
        self.deck = deck
        self.used_cards = used_cards
        self.cards_showing = cards_showing
    def reshuffle(self):
        self.deck.extend(self.used_cards)
        self.used_cards.clear()
        random.shuffle(self.deck)
        rand_index = 8 + random.randint(-4, 4)
        blank_card = Card('Plastic', 'Blank')
        self.deck.insert(rand_index, blank_card)
    def set_wager(self, wager):
        if self.status == Status.SPLIT_1:
            self.split_wager = wager
        else:
            self.wager = wager
    def hit(self):
        card = self.deck.pop()
        if card.val == 'Blank':
            self.reshuffle()
            card = self.deck.pop()
        self.hand.append(card)
        if not (isinstance(self, Dealer) and len(self.hand) == 2):
            self.cards_showing.append(card)
    def stand(self):
        if self.status == Status.SPLIT_1:
            tmp = self.hand
            self.hand = self.split_hand
            self.split_hand = tmp
            self.status = Status.SPLIT_2
        else:
            self.status = Status.STAND
    def double(self):
        self.set_wager(self.wager*2)
        self.hit()
        self.stand()
    def split(self):
        if len(self.hand) == 2 and len(self.split_hand) == 0:
            self.split_hand.append(self.hand.pop())
            self.status = Status.SPLIT_1
            self.split_wager = self.wager
        else:
            for card in self.hand:
                print(card)
            for card in self.split_hand:
                print(card)
            raise Exception('status:', self.status)
    def win(self, mult=1.0):
        self.balence += self.wager*mult
    def lose(self, mult=1.0):
        self.balence -= self.wager*mult
    def disp_hand(self):
        for card in self.hand:
            print(card)
    def hand_val(self, hard=False):
        """ returns the value of hand
        if hard is true Aces are 1 otherwise Aces are 11
        """
        val = 0
        for card in self.hand:
            val += card.get_num_val(hard=hard)
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
        self.split_hand = []
        self.status = Status.PLAY
        self.deck = deck
        self.used_cards = used_cards
        self.cards_showing = cards_showing
    def move(self):
        """ Dealer hits until soft 17 """
        if self.best_hand_val() >= 17 or self.best_hand_val() == 0:
            self.stand()
        else:
            self.hit()

class UIPlayer(Player):
    def __init__(self, balence, deck, used_cards, cards_showing):
        Player.__init__(self, balence, deck, used_cards, cards_showing)
    def move(self):
        s = input('S to stand, H to hit: ').lower()
        if s == 'h':
            self.hit()
        elif s == 's':
            self.stand()
        if self.best_hand_val() == 0:
            self.stand()

class SimplePlayer(Player):
    def __init__(self, balence, deck, used_cards, cards_showing):
        Player.__init__(self, balence, deck, used_cards, cards_showing)
    def move(self):
        if self.best_hand_val() >= 17:
            self.stand()
        elif self.best_hand_val() == 0:
            self.stand()
        else:
            self.hit()

class BasicStratPlayer(Player):
    """ Strategy Board Player """
    def __init__(self, balence, deck, used_cards, cards_showing, dealer):
        Player.__init__(self, balence, deck, used_cards, cards_showing)
        self.dealer = dealer
    def move(self):
        # print('len(self.deck):\t', len(self.deck))
        # print('len(self.used_cards):\t', len(self.used_cards))
        # print('total:\t',
        #         len(self.deck)+len(self.used_cards)+
        #         len(self.hand)+len(self.dealer.hand))
        dealer_showing = self.dealer.hand[0].get_num_val()
        if self.best_hand_val() == 0:
            self.stand()
        # SPLITS
        elif ((len(self.hand) == 2 and self.hand[0].val == self.hand[1].val and
                len(self.split_hand) == 0) and self.status == Status.PLAY and
                not (self.hand[0].val == 'J' or 
                self.hand[0].val == '5' or self.hand[0].val == 'K' or
                self.hand[0].val == 'Q' or self.hand[0].val == '10')):
            card_val = self.hand[0].val
            if card_val == 'A':
                self.split()
            elif card_val == '8':
                self.split()
            elif card_val == '9':
                if (dealer_showing == 7 or
                        10 <= dealer_showing <= 11):
                    self.stand()
                else:
                    self.split()
            elif card_val == '7':
                if dealer_showing <= 7:
                    self.split()
                else:
                    self.hit()
            elif card_val == '6':
                if dealer_showing <= 6:
                    self.split()
                else:
                    self.hit()
            elif card_val == '4':
                if 5 <= dealer_showing <= 6:
                    self.split()
                else:
                    self.hit()
            elif card_val == '2' or card_val == '3':
                if dealer_showing <= 7:
                    self.split()
                else:
                    self.hit()
        # SOFT
        elif (14 <= self.hand_val(hard=False) <= 21 and
                self.hand_val(hard=False) !=  self.hand_val(hard=True)):
            print('inf loop')
            self.disp_hand()
            print(self.status)
            soft_val = self.hand_val(hard=False)
            if soft_val >= 19:
                self.stand()
            elif 9 <= dealer_showing <= 11:
                self.hit()
            elif soft_val == 18:
                if 3 <= dealer_showing <= 6:
                    self.double()
                else:
                    self.stand()
            elif 7 <= dealer_showing:
                self.hit()
            elif soft_val == 17:
                if dealer_showing == 2:
                    self.hit()
                else:
                    self.double()
            elif 15 <= soft_val <= 16:
                if 2 <= dealer_showing <= 3:
                    self.hit()
                else:
                    self.double()
            elif soft_val == 14:
                if 2 <= dealer_showing <= 4:
                    self.hit()
                else:
                    self.double()
        # HARD
        else:
            hand_val = self.hand_val()
            if hand_val >= 17:
                self.stand()
            elif 13 <= hand_val <= 16:
                if dealer_showing <= 6:
                    self.stand()
                else:
                    self.hit()
            elif hand_val == 12:
                if 4 <= dealer_showing <= 6:
                    self.stand()
                else:
                    self.hit()
            elif hand_val == 11:
                if dealer_showing == 11:
                    self.hit()
                else:
                    self.double()
            elif hand_val == 10:
                if dealer_showing >= 10:
                    self.hit()
                else:
                    self.double()
            elif hand_val == 9:
                if 3 <= dealer_showing <= 6:
                    self.double()
                else:
                    self.hit()
            else:
                self.hit()

class CCPlayer(Player):
    """ Card Counting Player """
    def __init__(self, balence, deck, used_cards, cards_showing, dealer):
        Player.__init__(balence, deck, used_cards, cards_showing)
        self.dealer = dealer
    def expected_return(self):
        """ Return expected return of bet given the remaining deck
        for each permutations of the remaining deck calculate expected return
        and then calculate the average
        """
        pass # TODO
    def move(self):
        pass # TODO
    def set_wager(self, wager):
        pass # TODO

class HLPlayer(BasicStratPlayer):
    """ player using high low counting system """
    def __init__(self, balence, deck, used_cards, cards_showing, dealer):
        BasicStratPlayer.__init__(
                self,
                balence,
                deck,
                used_cards,
                cards_showing,
                dealer
            )
    def set_wager(self, wager):
        running_cnt = 0
        for card in self.deck:
            if card.val == 'Blank':
                continue
            val = card.get_num_val()
            if 2 <= val <= 6:
                running_cnt += 1
            elif 10 <= val <= 11:
                running_cnt -= 1
        L = len(self.deck)
        decks_remaining = L//26
        decks_remaining = 1 if decks_remaining < 1 else decks_remaining
        tru_cnt = running_cnt/float(decks_remaining)
        bet = wager*(tru_cnt)
        if bet < 1:
            bet = wager
        if bet > 50:
            bet = 50
        self.wager = bet

def deal_cards(players):
    for i in range(2):
        for player in players:
            player.hit()

def clear_table(players): 
    for player in players:
        player.status = Status.PLAY
        while len(player.hand):
            player.used_cards.append(player.hand.pop())
        while len(player.split_hand):
            player.used_cards.append(player.split_hand.pop())

def print_UI(dealer, player1, dealer_move=False):
    os.system('cls' if os.name == 'nt' else 'clear')
    print('Balence:', player1.balence)
    print('Wager:', player1.wager, '\n')
    print(len(player1.deck))
    for card in player1.deck:
        print(card, ',', end=' ')
    print()
    if dealer_move:
        print('Dealer showing:', dealer.best_hand_val())
        dealer.disp_hand()
        print()
    else:
        print('Dealer showing:\n'+str(dealer.hand[0]), '\n')
    print('Your hand:', player1.best_hand_val())
    player1.disp_hand()
