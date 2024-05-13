import mysql.connector
import random
import tkinter as tk
from tkinter import messagebox


class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{self.rank} of {self.suit}"


class Deck:
    def __init__(self):
        self.cards = []
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
        for suit in suits:
            for rank in ranks:
                self.cards.append(Card(suit, rank))
        random.shuffle(self.cards)

    def draw_card(self):
        return self.cards.pop()


class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []

    def draw_hand(self, deck, num_cards):
        for _ in range(num_cards):
            self.hand.append(deck.draw_card())

    def play_card(self, card_index, discard_pile):
        card = self.hand.pop(card_index)
        discard_pile.append(card)
        return card


class MauMau:
    def __init__(self, num_players, root):
        self.root = root
        self.num_players = num_players
        self.db_connection = mysql.connector.connect(
            host="localhost",
            user="test",
            password="test",
            database="cardgame"
        )
        self.cursor = self.db_connection.cursor()
        self.create_tables()
        self.players = []
        self.create_gui()

    def create_tables(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS Players (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255))")
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS Games (id INT AUTO_INCREMENT PRIMARY KEY, winner_id INT, FOREIGN KEY (winner_id) REFERENCES Players(id), date_played DATE)")

    def add_player_to_database(self, name):
        self.cursor.execute("INSERT INTO Players (name) VALUES (%s)", (name,))
        self.db_connection.commit()
        return self.cursor.lastrowid

    def save_game_result(self, winner_id):
        self.cursor.execute("INSERT INTO Games (winner_id, date_played) VALUES (%s, CURDATE())", (winner_id,))
        self.db_connection.commit()

    def deal_cards(self, num_cards):
        for player in self.players:
            player.draw_hand(self.deck, num_cards)

    def start_game(self):
        self.deck = Deck()
        self.deal_cards(5)
        self.discard_pile = [self.deck.draw_card()]  # place one card on the discard pile to start

    def play_round(self):
        current_player = 0
        skip_next_player = False
        while True:
            player = self.players[current_player]
            if len(player.hand) == 0:
                messagebox.showinfo("Game Over", f"{player.name} wins!")
                winner_id = self.add_player_to_database(player.name)
                self.save_game_result(winner_id)
                return

            self.root.update()
            self.update_gui(player)
            action = self.get_player_action(player)
            if action == 'draw':
                drawn_card = self.deck.draw_card()

