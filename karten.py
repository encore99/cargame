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
        self.add_players()  # Füge Spieler hinzu, bevor das GUI erstellt wird
        self.create_gui()
        self.start_game()  # Starte das Spiel nachdem die Spieler hinzugefügt wurden

    def create_tables(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS Players (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255))")
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS Games (id INT AUTO_INCREMENT PRIMARY KEY, winner_id INT, FOREIGN KEY (winner_id) REFERENCES Players(id), date_played DATE)")

    def add_players(self):
        for i in range(self.num_players):
            player_name = f"Player {i+1}"
            self.players.append(Player(player_name))

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
        self.play_round()

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
                if self.discard_pile[-1].rank == '7':
                    messagebox.showinfo("Mau-Mau", f"{player.name} played a 7! The next player draws 2 cards.")
                    self.players[(current_player + 1) % len(self.players)].draw_hand(self.deck, 2)
                player.hand.append(drawn_card)
            else:
                card_index = int(action)
                selected_card = player.play_card(card_index, self.discard_pile)
                if selected_card.rank == '7':
                    messagebox.showinfo("Mau-Mau", f"{player.name} played a 7! The next player draws 2 cards.")
                    self.players[(current_player + 1) % len(self.players)].draw_hand(self.deck, 2)
                elif selected_card.rank == '8':
                    if skip_next_player:
                        messagebox.showinfo("Mau-Mau", f"{player.name} played an 8! Skipping next player's turn.")
                        skip_next_player = False
                    else:
                        messagebox.showinfo("Mau-Mau", f"{player.name} played an 8! The next player is skipped.")
                        skip_next_player = True
                    current_player = (current_player + 1) % len(self.players)
                elif self.check_win(player):
                    messagebox.showinfo("Game Over", f"{player.name} wins!")
                    winner_id = self.add_player_to_database(player.name)
                    self.save_game_result(winner_id)
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

        tk.Label(self.root, text="Enter the index of the card you want to play (or 'draw' to draw a card):").grid(row=2, column=0)
        self.card_entry = tk.Entry(self.root)
        self.card_entry.grid(row=2, column=1)
        tk.Button(self.root, text="Draw Card", command=draw_card).grid(row=3, column=0, padx=5, pady=5)
        tk.Button(self.root, text="Play Card", command=play_card).grid(row=3, column=1, padx=5, pady=5)
        while self.action is None:
            self.root.update()
        self.root.quit()
        return self.action

    def create_gui(self):
        tk.Label(self.root, text="Enter Player Names:").grid(row=0, column=0, columnspan=2)

        self.player_names = []
        for i in range(self.num_players):
            entry = tk.Entry(self.root)
            entry.grid(row=i+1, column=1, padx=5, pady=5)
            self.player_names.append(entry)

        start_button = tk.Button(self.root, text="Start Game", command=self.start_game)
        start_button.grid(row=self.num_players+1, column=0, columnspan=2, padx=5, pady=5)

        self.hand_label = tk.Label(self.root, text="")
        self.hand_label.grid(row=self.num_players+2, column=0, columnspan=2, padx=5, pady=5)

        self.discard_label = tk.Label(self.root, text="")
        self.discard_label.grid(row=self.num_players+3, column=0, columnspan=2, padx=5, pady=5)


# GUI initialisieren und Spiel starten
root = tk.Tk()
root.title("Mau-Mau")
game = MauMau(2, root)
root.mainloop()
