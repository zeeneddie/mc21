#!/usr/bin/env python3
import os, random

class Card(object):
    def __init__(self, suit, val):
        self.suit = suit
        self.val = val
    def __str__(self):
        return str(self.val) + ' of ' + str(self.suit)

VALS = ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'King',
    'Queen', 'Jack']
SUITS = ['Clubs', 'Heart', 'Diamond', 'Spades']
deck = []
for decks in range(8):
    for val in VALS:
        for suit in SUITS:
            deck.append(Card(suit, val))
random.shuffle(deck)
# TODO: add blank plastic card toward end of deck

used_cards = []
cards_showing = []

def deal_cards(players):
    for player in players:
        # TODO: if blank plastic card, re-shuffle
        player.hit(deck.pop())

def clear_table(players):
    for player in players:
        while len(player.hand):
            used_cards.append(player.hand.pop())

class Player(object):
    def __init__(self):
        self.hand = []
        self.status = None
    def hit(self):
        self.hand.append(deck.pop())
    def move(self):
        raise NotImplementedError

def main():
    player1 = Player()

if __name__ == '__main__':
    main()
