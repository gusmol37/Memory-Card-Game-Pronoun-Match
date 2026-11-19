"""
PRONOUN MEMORY GAME
-------------------
Juego de memoria digital para 2 jugadores con 20 cartas (10 parejas)
+ 2 comodines ("Extra Turn" y "Lose a Pair").

- 10 cartas con oraciones de situaciones diarias (school, home, friends).
- 10 cartas con el pronombre que completa cada oración
  (personal, possessive y object pronouns).
- Las cartas se voltean con un clic y aparecen los mensajes
  "Match!" o "Try again!".

Requisitos: Python 3.7+ (tkinter viene incluido con Python).
Ejecutar:   python memory_pronouns.py
"""

import random
import tkinter as tk
from tkinter import messagebox, simpledialog

# ---------------------------------------------------------------------------
# DATOS DEL JUEGO: (oración, pronombre, tipo de pronombre, categoría)
# ---------------------------------------------------------------------------
PAIRS = [
    ("The teacher asked Ana a question and ____ answered correctly.",
     "She", "Personal pronoun", "School"),
    ("My brother and I clean the kitchen every day. ____ are a good team.",
     "We", "Personal pronoun", "Home"),
    ("Carlos and Luis are my friends. ____ play soccer with me every Friday.",
     "They", "Personal pronoun", "Friends"),
    ("I can't find a pencil. Can you lend ____ one, please?",
     "me", "Object pronoun", "School"),
    ("My mom is cooking dinner, so I am going to help ____.",
     "her", "Object pronoun", "Home"),
    ("Tom is shy, so I always invite ____ to my birthday party.",
     "him", "Object pronoun", "Friends"),
    ("The teacher gave ____ a lot of homework, so we studied together.",
     "us", "Object pronoun", "School"),
    ("This is not your jacket. It is ____. I bought it last week.",
     "mine", "Possessive pronoun", "Home"),
    ("That backpack belongs to Anna. It is ____.",
     "hers", "Possessive pronoun", "Friends"),
    ("Is this ____ notebook, Maria? You left it on the desk.",
     "your", "Possessive adjective", "School"),
]

WILDCARDS = ["Extra Turn", "Lose a Pair"]

RULES = (
    "HOW TO PLAY\n\n"
    "1. Two players take turns.\n"
    "2. On your turn, flip TWO cards by clicking on them.\n"
    "3. Match each sentence with the pronoun that completes it.\n"
    "4. If they match ('Match!'), you keep the pair.\n"
    "   If not ('Try again!'), the cards are turned face down again.\n"
    "5. Wildcards (gold cards):\n"
    "   • Extra Turn: you play one more turn after this one.\n"
    "   • Lose a Pair: you lose your last pair (it goes back to the board).\n"
    "     If you have no pairs, nothing happens.\n"
    "6. The player with MORE PAIRS at the end wins!"
)

# ---------------------------------------------------------------------------
# COLORES
# ---------------------------------------------------------------------------
BACK_COLOR = "#334155"
KIND_COLORS = {"sentence": "#dbeafe", "pronoun": "#dcfce7", "wild": "#fde68a"}
OWNER_COLORS = ["#fdba74", "#d8b4fe"]          # jugador 1 / jugador 2
PLAYER_ACTIVE = ["#f97316", "#a855f7"]
BG = "#f1f5f9"

COLUMNS = 6


class MemoryGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Pronoun Memory Game")
        self.root.configure(bg=BG)

        # Nombres de los jugadores
        n1 = simpledialog.askstring("Player 1", "Name of Player 1:",
                                    parent=root) or "Player 1"
        n2 = simpledialog.askstring("Player 2", "Name of Player 2:",
                                    parent=root) or "Player 2"
        self.names = [n1.strip() or "Player 1", n2.strip() or "Player 2"]

        self._build_ui()
        self.new_game()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        top = tk.Frame(self.root, bg=BG)
        top.pack(pady=(10, 4))

        self.score_labels = []
        for i in range(2):
            lbl = tk.Label(top, font=("Arial", 14, "bold"), width=22,
                           padx=8, pady=6, relief="ridge", bd=3)
            lbl.grid(row=0, column=i, padx=10)
            self.score_labels.append(lbl)

        self.turn_label = tk.Label(self.root, font=("Arial", 13), bg=BG)
        self.turn_label.pack()

        self.msg_label = tk.Label(self.root, text="", font=("Arial", 20, "bold"),
                                  bg=BG, height=1)
        self.msg_label.pack(pady=4)

        self.board = tk.Frame(self.root, bg=BG)
        self.board.pack(padx=12, pady=6)

        bottom = tk.Frame(self.root, bg=BG)
        bottom.pack(pady=(4, 12))
        tk.Button(bottom, text="New Game", font=("Arial", 12),
                  command=self.new_game).grid(row=0, column=0, padx=8)
        tk.Button(bottom, text="Rules", font=("Arial", 12),
                  command=lambda: messagebox.showinfo("Rules", RULES)
                  ).grid(row=0, column=1, padx=8)

    # ------------------------------------------------------- NUEVO JUEGO
    def new_game(self):
        for w in self.board.winfo_children():
            w.destroy()

        self.current = 0                 # jugador en turno
        self.won = [[], []]              # ids de parejas ganadas por jugador
        self.first = None                # índice de la primera carta volteada
        self.lock = False                # bloquea clics mientras se anima
        self.extra_turn = False          # ¿el jugador juega otra vez?

        # Crear las 22 cartas
        cards = []
        for pid, (sentence, pronoun, ptype, category) in enumerate(PAIRS):
            cards.append({"pair": pid, "kind": "sentence",
                          "text": sentence, "tag": category})
            cards.append({"pair": pid, "kind": "pronoun",
                          "text": pronoun, "tag": ptype})
        for w in WILDCARDS:
            cards.append({"pair": None, "kind": "wild",
                          "text": w, "tag": "WILDCARD"})
        random.shuffle(cards)

        self.cards = cards
        for i, c in enumerate(cards):
            c["up"] = False
            c["owner"] = None
            lbl = tk.Label(self.board, width=21, height=7, wraplength=150,
                           relief="raised", bd=4, justify="center",
                           cursor="hand2")
            lbl.grid(row=i // COLUMNS, column=i % COLUMNS, padx=4, pady=4)
            lbl.bind("<Button-1>", lambda e, idx=i: self.on_click(idx))
            c["label"] = lbl
            self.refresh(i)

        self.say("Flip two cards!", "#0f172a")
        self.update_labels()

    # ------------------------------------------------------ VISUALIZACIÓN
    def refresh(self, i):
        c = self.cards[i]
        lbl = c["label"]
        if not c["up"]:
            lbl.config(text="?", bg=BACK_COLOR, fg="white",
                       font=("Arial", 30, "bold"))
            return

        bg = KIND_COLORS[c["kind"]]
        if c["owner"] is not None:
            bg = OWNER_COLORS[c["owner"]]

        if c["kind"] == "sentence":
            text, font = f'[{c["tag"]}]\n\n{c["text"]}', ("Arial", 11)
        elif c["kind"] == "pronoun":
            text, font = f'[{c["tag"]}]\n\n{c["text"]}', ("Arial", 17, "bold")
        else:
            text, font = f'★ WILDCARD ★\n\n{c["text"]}', ("Arial", 15, "bold")
        lbl.config(text=text, bg=bg, fg="#0f172a", font=font)

    def say(self, text, color="#0f172a"):
        self.msg_label.config(text=text, fg=color)

    def update_labels(self):
        for i in range(2):
            active = (i == self.current)
            self.score_labels[i].config(
                text=f"{self.names[i]}: {len(self.won[i])} pairs",
                bg=PLAYER_ACTIVE[i] if active else "#e2e8f0",
                fg="white" if active else "#334155")
        extra = "  (+ Extra Turn!)" if self.extra_turn else ""
        self.turn_label.config(text=f"Turn: {self.names[self.current]}{extra}")

    # ------------------------------------------------------------- JUEGO
    def on_click(self, i):
        if self.lock:
            return
        card = self.cards[i]
        if card["up"]:
            return

        card["up"] = True
        self.refresh(i)

        if card["kind"] == "wild":
            self.play_wildcard(card)
            return

        if self.first is None:           # primera carta del turno
            self.first = i
            self.say("Now flip a second card!", "#0f172a")
            return

        # segunda carta del turno
        self.lock = True
        a, b = self.cards[self.first], card
        if a["pair"] == b["pair"]:
            self.handle_match(a, b)
        else:
            self.handle_miss(a, b)

    def handle_match(self, a, b):
        a["owner"] = b["owner"] = self.current
        self.won[self.current].append(a["pair"])
        self.refresh(self.cards.index(a))
        self.refresh(self.cards.index(b))
        self.first = None
        self.say("Match!", "#16a34a")
        self.update_labels()

        if self.all_matched():
            self.root.after(900, self.finish_game)
        else:
            self.root.after(1200, self.next_turn)

    def handle_miss(self, a, b):
        self.say("Try again!", "#dc2626")

        def hide_cards():
            for card in (a, b):
                card["up"] = False
                self.refresh(self.cards.index(card))
            self.first = None
            self.next_turn()

        self.root.after(1400, hide_cards)

    # ---------------------------------------------------------- COMODINES
    def play_wildcard(self, card):
        if card["text"] == "Extra Turn":
            self.extra_turn = True
            self.say("Extra Turn! You play again!", "#ca8a04")
            self.update_labels()
            return                       # el turno actual continúa

        # "Lose a Pair"
        if not self.won[self.current]:
            self.say("Lose a Pair... but you have none. Lucky!", "#ca8a04")
            return

        pair_id = self.won[self.current].pop()
        for c in self.cards:
            if c["pair"] == pair_id:     # la pareja vuelve al tablero
                c["owner"] = None
                c["up"] = False
                self.refresh(self.cards.index(c))
        self.say("Lose a Pair! Your last pair goes back to the board.",
                 "#dc2626")
        self.update_labels()
        self.lock = True

        def end_penalty():
            if self.first is not None:   # voltear la carta pendiente
                self.cards[self.first]["up"] = False
                self.refresh(self.first)
                self.first = None
            self.next_turn()

        self.root.after(1800, end_penalty)

    # --------------------------------------------------------- TURNOS/FIN
    def next_turn(self):
        if self.extra_turn:
            self.extra_turn = False
            self.say(f"{self.names[self.current]} plays again!", "#ca8a04")
        else:
            self.current = 1 - self.current
            self.say("Flip two cards!", "#0f172a")
        self.update_labels()
        self.lock = False

    def all_matched(self):
        return all(c["owner"] is not None
                   for c in self.cards if c["kind"] != "wild")

    def finish_game(self):
        s1, s2 = len(self.won[0]), len(self.won[1])
        if s1 > s2:
            result = f"{self.names[0]} wins!"
        elif s2 > s1:
            result = f"{self.names[1]} wins!"
        else:
            result = "It's a tie!"
        again = messagebox.askyesno(
            "Game Over",
            f"{result}\n\n{self.names[0]}: {s1} pairs\n"
            f"{self.names[1]}: {s2} pairs\n\nPlay again?")
        if again:
            self.new_game()
        else:
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    MemoryGame(root)
    root.mainloop()
