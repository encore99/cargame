import tkinter as tk
import os
import random
from PIL import ImageTk, Image

class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Bildbibliothek")
        self.geometry("800x400")

        self.hand = []
        self.spielfeld = []
        self.friedhof = []

        self.library_button = tk.Button(self, text="Bibliothek", command=self.add_to_hand)
        self.library_button.place(x=10, y=370)

        self.display_button = tk.Button(self, text="Anzeigen", command=self.display_hand)
        self.display_button.place(x=700, y=370)

        self.bind("<Button-3>", self.right_click_menu)  # Rechtsklick-Ereignis binden

    def add_to_hand(self):
        # Passe den Pfad zum Ordner mit deinen Bildern an
        image_folder = "deck\ZombieDeckTest"
        images = os.listdir(image_folder)
        if images:
            random_image = random.choice(images)
            if random_image not in self.hand:  # Überprüfung auf Doppelung
                self.hand.append(os.path.join(image_folder, random_image))
                print("Bild hinzugefügt:", random_image)
            else:
                print("Bild bereits in der Hand vorhanden.")
        else:
            print("Keine Bilder im Ordner gefunden.")

    def display_hand(self):
        if self.hand:
            hand_window = tk.Toplevel(self)
            hand_window.title("Hand")
            hand_window.geometry("600x100")

            for i, image_path in enumerate(self.hand):
                image = Image.open(image_path)
                image.thumbnail((100, 100))
                photo = ImageTk.PhotoImage(image)

                label = tk.Label(hand_window, image=photo)
                label.image = photo
                label.grid(row=0, column=i, padx=5, pady=5)

                # Binding des Klick-Ereignisses
                label.bind("<Button-1>", lambda event, path=image_path: self.show_full_image(path))
                label.bind("<Button-3>", lambda event, path=image_path: self.show_context_menu(event, path))

        else:
            print("Die Hand ist leer.")

    def show_full_image(self, image_path):
        full_image_window = tk.Toplevel(self)
        full_image_window.title("Vollbild")
        
        image = Image.open(image_path)
        photo = ImageTk.PhotoImage(image)

        label = tk.Label(full_image_window, image=photo)
        label.image = photo
        label.pack()

    def show_context_menu(self, event, image_path):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Ausspielen", command=lambda: self.move_to_spielfeld(image_path))
        menu.add_command(label="Abwerfen", command=lambda: self.move_to_friedhof(image_path))
        menu.post(event.x_root, event.y_root)

    def move_to_spielfeld(self, image_path):
        if image_path in self.hand:
            self.hand.remove(image_path)
            self.spielfeld.append(image_path)
            self.update_display()

    def move_to_friedhof(self, image_path):
        if image_path in self.hand:
            self.hand.remove(image_path)
            self.friedhof.append(image_path)
            self.update_display()

    def update_display(self):
        # Entferne vorhandene Labels
        for widget in self.winfo_children():
            if isinstance(widget, tk.Label):
                widget.destroy()

        # Anzeige Spielfeld
        for i, image_path in enumerate(self.spielfeld):
            image = Image.open(image_path)
            image.thumbnail((100, 100))
            photo = ImageTk.PhotoImage(image)

            label = tk.Label(self, image=photo)
            label.image = photo
            label.grid(row=1, column=i+1, padx=5, pady=5)

            # Binding des Klick-Ereignisses
            label.bind("<Button-1>", lambda event, path=image_path: self.show_full_image(path))

        # Anzeige Friedhof
        if self.friedhof:
            last_image = self.friedhof[-1]
            image = Image.open(last_image)
            image.thumbnail((100, 100))
            photo = ImageTk.PhotoImage(image)

            label = tk.Label(self, image=photo)
            label.image = photo
            label.grid(row=0, column=0, padx=5, pady=5)
            label.bind("<Button-1>", lambda event, images=self.friedhof: self.display_friedhof(images))

    def display_friedhof(self, images):
        hand_window = tk.Toplevel(self)
        hand_window.title("Friedhof")
        hand_window.geometry("600x100")

        for i, image_path in enumerate(images):
            image = Image.open(image_path)
            image.thumbnail((100, 100))
            photo = ImageTk.PhotoImage(image)

            label = tk.Label(hand_window, image=photo)
            label.image = photo
            label.grid(row=0, column=i, padx=5, pady=5)

            # Binding des Klick-Ereignisses
            label.bind("<Button-1>", lambda event, path=image_path: self.show_full_image(path))

    def right_click_menu(self, event):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Bibliothek", command=self.add_to_hand)
        menu.post(event.x_root, event.y_root)

if __name__ == "__main__":
    app = Application()
    app.mainloop()
