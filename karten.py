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
        self.db_connection = mysql.connector.connect(
            host="localhost",
            user="test",
            password="test",
            database="cardgame"
        )
        self.cursor = self.db_connection.cursor()
        self.create_highscore_table()

        self.deck = Deck()
        self.players = [Player(f"Player {i + 1}") for i in range(num_players)]
        self.discard_pile = []
        self.create_gui()

    def create_highscore_table(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS Highscore (player_name VARCHAR(255), score INT)")

    def save_highscore(self, player_name, score):
        self.cursor.execute("INSERT INTO Highscore (player_name, score) VALUES (%s, %s)", (player_name, score))
        self.db_connection.commit()

    def deal_cards(self, num_cards):
        for player in self.players:
            player.draw_hand(self.deck, num_cards)

    def start_game(self):
        self.deal_cards(5)
        self.discard_pile.append(self.deck.draw_card())

    def play_round(self):
        current_player = 0
        while True:
            player = self.players[current_player]
            if len(player.hand) == 0:
                messagebox.showinfo("Game Over", f"{player.name} wins!")
                self.save_highscore(player.name, len(player.hand))
                return

            self.root.update()
            self.update_gui(player)
            action = self.get_player_action(player)
            if action == 'draw':
                drawn_card = self.deck.draw_card()
                player.hand.append(drawn_card)
            else:
                card_index = int(action)
                selected_card = player.play_card(card_index, self.discard_pile)
                if selected_card.rank == '8':
                    messagebox.showinfo("Mau-Mau", "You played an 8! Skipping next player's turn.")
                    current_player = (current_player + 1) % len(self.players)
                elif self.check_win(player):
                    messagebox.showinfo("Game Over", f"{player.name} wins!")
                    self.save_highscore(player.name, len(player.hand))
                    return
                else:
                    current_player = (current_player + 1) % len(self.players)

    def check_win(self, player):
        return len(player.hand) == 0

    def update_gui(self, player):
        self.hand_label.config(
            text="Your Hand:\n" + "\n".join([f"{i + 1}: {card}" for i, card in enumerate(player.hand)]))
        self.discard_label.config(text="Discard Pile Top Card:\n" + str(self.discard_pile[-1]))

    def get_player_action(self, player):
        self.action = None

        def draw_card():
            self.action = 'draw'
            self.root.quit()

        def play_card():
            self.action = self.card_entry.get()
            self.root.quit()

        tk.Label(self.root, text="Enter the index of the card you want to play (or 'draw' to draw a card):").grid(row=2,
                                                                                                                  column=0)
        self.card_entry = tk.Entry(self.root)
        self.card_entry.grid(row=2, column=1)
        tk.Button(self.root, text="Draw Card", command=draw_card).grid(row=3, column=0)
        tk.Button(self.root, text="Play Card", command=play_card).grid(row=3, column=1)
        self.root.mainloop()
        return self.action

    def create_gui(self):
        self.hand_label = tk.Label(self.root, text="Your Hand:")
        self.hand_label.grid(row=0, column=0)
        self.discard_label = tk.Label(self.root, text="Discard Pile Top Card:")
        self.discard_label.grid(row=0, column=1)


# GUI initialisieren und Spiel starten
root = tk.Tk()
root.title("Mau-Mau")
game = MauMau(2, root)
game.start_game()
game.play_round()
