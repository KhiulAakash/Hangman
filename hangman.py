import random
import time
import tkinter as tk
from tkinter import ttk, messagebox

# -----------------------------
# "Dictionary" and Word Banks
# -----------------------------
# A compact built-in dictionary of valid words for demo & tests.
# (You can expand this list as you like; all phrases are built from these.)
DICTIONARY_WORDS = {
    # common words used for basic play and to compose phrases
    "python", "hangman", "testing", "programming", "software", "engineer", "unit",
    "quality", "logic", "timer", "random", "letter", "guess", "phrase", "word",
    "game", "player", "lives", "time", "round", "level", "basic", "intermediate",
    "code", "refactor", "mock", "assert", "class", "method", "function", "module",
    "object", "system", "design", "pattern", "practice", "clean", "state", "event",
    "loop", "input", "output", "screen", "window", "button", "canvas", "gallows",
    "rope", "head", "body", "arm", "leg", "win", "lose", "over", "computer",
    "science", "data", "structure", "algorithm", "debug", "feature", "release"
}

BASIC_WORDS = [
    "python", "hangman", "testing", "programming", "software", "logic",
    "random", "letter", "guess", "timer", "player", "lives", "round", "level"
]

# Phrases (INTERMEDIATE) are composed strictly from DICTIONARY_WORDS.
INTERMEDIATE_PHRASES = [
    "unit testing",
    "software engineer",
    "clean code",
    "design pattern",
    "data structure",
    "debug feature",
    "game window",
    "random letter",
    "timer event",
    "quality practice",
    "programming logic",
    "computer science"
]


def is_valid_phrase(phrase: str) -> bool:
    """Every token must be a valid dictionary word."""
    return all(token in DICTIONARY_WORDS for token in phrase.lower().split())


# -----------------------------
# Pure Logic (Testable)
# -----------------------------
class HangmanCore:
    def __init__(self, level='basic', max_lives=6, round_time=15):
        """
        level: 'basic' -> single word; 'intermediate' -> phrase
        """
        self.level = level.lower()
        self.max_lives = int(max_lives)
        self.round_time = float(round_time)

        self.secret_word = ''
        self.guessed_letters = set()
        self.lives = self.max_lives
        self.start_time = time.time()

        # seed pools based on level
        self._refresh_pool()

    def _refresh_pool(self):
        if self.level == 'intermediate':
            # Filter only valid phrases
            self.pool = [p for p in INTERMEDIATE_PHRASES if is_valid_phrase(p)]
        else:
            # basic -> single valid words
            self.pool = [w for w in BASIC_WORDS if w in DICTIONARY_WORDS]

        # Fallback safety (should not happen with provided lists)
        if not self.pool:
            self.pool = ["python"] if self.level == 'basic' else ["unit testing"]

    def set_level(self, level: str):
        self.level = (level or 'basic').lower()
        self._refresh_pool()

    def new_round(self):
        self.secret_word = random.choice(self.pool)
        self.guessed_letters.clear()
        self.lives = self.max_lives
        self.start_time = time.time()

    def process_guess(self, letter: str):
        """Returns True (correct), False (wrong), or None (repeated/invalid)."""
        if not letter or len(letter) != 1 or not letter.isalpha():
            return None
        letter = letter.lower()
        if letter in self.guessed_letters:
            return None

        self.guessed_letters.add(letter)
        if letter not in self.secret_word.replace(" ", ""):
            self.lives = max(0, self.lives - 1)
            return False
        return True

    def is_word_guessed(self):
        # Spaces don't need to be guessed
        return all(ch == ' ' or ch in self.guessed_letters
                   for ch in self.secret_word.lower())

    def display_word(self):
        # Underscores for letters; preserve spaces
        return ' '.join(
            ch if (ch == ' ' or ch.lower() in self.guessed_letters) else '_'
            for ch in self.secret_word
        )

    def time_remaining(self):
        return max(0.0, self.round_time - (time.time() - self.start_time))

    def time_up(self):
        """Deduct a life when the 15s round timer expires."""
        self.lives = max(0, self.lives - 1)
        self.start_time = time.time()


# -----------------------------
# GUI Layer (with drawing)
# -----------------------------
class HangmanGUI:
    def __init__(self, core: HangmanCore):
        self.core = core

        self.root = tk.Tk()
        self.root.title("Hangman Game")
        self.root.geometry("820x640")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.root.quit)

        self.timer_id = None
        self._build_ui()
        self.start_new_game()

    def _build_ui(self):
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Arial', 22, 'bold'))
        style.configure('Word.TLabel', font=('Courier New', 24, 'bold'))
        style.configure('Info.TLabel', font=('Arial', 14))
        style.configure('Letter.TButton', font=('Arial', 12))

        # Layout: two columns (left = canvas; right = controls/info)
        root_frame = ttk.Frame(self.root, padding=15)
        root_frame.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(root_frame)
        left.grid(row=0, column=0, sticky="n", padx=(0, 15))
        right = ttk.Frame(root_frame)
        right.grid(row=0, column=1, sticky="n")

        ttk.Label(right, text="Hangman", style='Title.TLabel').grid(row=0, column=0, pady=(0, 10))

        # Level selector
        level_row = ttk.Frame(right)
        level_row.grid(row=1, column=0, sticky="w", pady=(0, 8))
        ttk.Label(level_row, text="Level:", style='Info.TLabel').grid(row=0, column=0, padx=(0, 8))
        self.level_var = tk.StringVar(value=self.core.level.title())
        self.level_combo = ttk.Combobox(
            level_row, textvariable=self.level_var, values=["Basic", "Intermediate"],
            state="readonly", width=15
        )
        self.level_combo.grid(row=0, column=1)
        self.level_combo.bind('<<ComboboxSelected>>', self._on_level_change)

        # Word display
        self.word_label = ttk.Label(right, style='Word.TLabel')
        self.word_label.grid(row=2, column=0, pady=10)

        # Info row: lives + timer
        info_frame = ttk.Frame(right)
        info_frame.grid(row=3, column=0, pady=(4, 8))
        self.lives_label = ttk.Label(info_frame, style='Info.TLabel')
        self.lives_label.grid(row=0, column=0, padx=10)
        self.timer_label = ttk.Label(info_frame, style='Info.TLabel')
        self.timer_label.grid(row=0, column=1, padx=10)

        # Used letters
        self.used_label = ttk.Label(right, style='Info.TLabel', wraplength=360, justify="left")
        self.used_label.grid(row=4, column=0, pady=(4, 10), sticky="w")

        # On-screen keyboard
        kb = ttk.Frame(right)
        kb.grid(row=5, column=0, pady=10)
        for r, letters in enumerate(["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]):
            for c, letter in enumerate(letters):
                btn = ttk.Button(
                    kb, text=letter, width=3, style='Letter.TButton',
                    command=lambda l=letter: self._on_guess(l)
                )
                btn.grid(row=r, column=c, padx=2, pady=2)
                setattr(self, f'btn_{letter}', btn)

        # Controls
        ctl = ttk.Frame(right)
        ctl.grid(row=6, column=0, pady=10)
        ttk.Button(ctl, text="New Round", command=self.start_new_game).grid(row=0, column=0, padx=8)
        ttk.Button(ctl, text="Quit", command=self.root.quit).grid(row=0, column=1, padx=8)

        # Drawing canvas (left side)
        self.canvas = tk.Canvas(left, width=280, height=280, bg='white', relief='solid', highlightthickness=1)
        self.canvas.grid(row=0, column=0, pady=(4, 10))

        # Small hint about rules
        rules = (
            "Rules:\n"
            "• 15s per guess; time-out costs 1 life.\n"
            "• Wrong letter costs 1 life.\n"
            "• Correct guesses reveal all positions.\n"
            "• Spaces in phrases are pre-shown."
        )
        ttk.Label(left, text=rules, style='Info.TLabel', justify="left").grid(row=1, column=0, sticky="w")

        # Bind physical keyboard
        self.root.bind("<Key>", self._on_keypress)

    # ---------- Drawing ----------
    def _draw_stage(self):
        """Draw gallows and parts depending on lives left (scaled for 280x280 canvas)."""
        self.canvas.delete("all")

        # gallows
        self.canvas.create_line(40, 250, 120, 250, width=4, fill='brown')   # base
        self.canvas.create_line(80, 250, 80, 20, width=4, fill='brown')     # pole
        self.canvas.create_line(80, 20, 200, 20, width=4, fill='brown')     # top beam
        self.canvas.create_line(200, 20, 200, 45, width=4, fill='brown')    # rope

        mistakes = self.core.max_lives - self.core.lives

        if mistakes >= 1:  # head
            self.canvas.create_oval(185, 45, 215, 75, width=2)
        if mistakes >= 2:  # body
            self.canvas.create_line(200, 75, 200, 130, width=2)
        if mistakes >= 3:  # left arm
            self.canvas.create_line(200, 90, 175, 110, width=2)
        if mistakes >= 4:  # right arm
            self.canvas.create_line(200, 90, 225, 110, width=2)
        if mistakes >= 5:  # left leg
            self.canvas.create_line(200, 130, 185, 165, width=2)
        if mistakes >= 6:  # right leg
            self.canvas.create_line(200, 130, 215, 165, width=2)

    # ---------- Game flow ----------
    def _on_level_change(self, _event=None):
        new_level = self.level_var.get().lower()
        self.core.set_level(new_level)
        self.start_new_game()

    def start_new_game(self):
        self.core.new_round()
        # enable all letter buttons
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            btn = getattr(self, f'btn_{letter}', None)
            if btn:
                btn.state(['!disabled'])
        self._refresh_ui()
        self._schedule_timer()

    def _on_keypress(self, event: tk.Event):
        ch = getattr(event, "char", "")
        if ch and ch.isalpha() and len(ch) == 1:
            self._on_guess(ch.upper())

    def _on_guess(self, letter):
        btn = getattr(self, f'btn_{letter}', None)
        if btn and 'disabled' not in btn.state():
            btn.state(['disabled'])
        result = self.core.process_guess(letter)
        self._refresh_ui()

        if self.core.is_word_guessed():
            self._cancel_timer()
            messagebox.showinfo("You win!", f"The answer was: {self.core.secret_word}")
            # Keep game going after success
            self.start_new_game()
            return

        if self.core.lives <= 0:
            self._cancel_timer()
            messagebox.showinfo("Game Over", f"The answer was: {self.core.secret_word}")
            # Keep game going after failure as well (until player quits)
            self.start_new_game()
            return

        # Correct guess resets timer window
        if result:
            self.core.start_time = time.time()
            self._schedule_timer()

    # ---------- UI helpers ----------
    def _refresh_ui(self):
        self.word_label.config(text=self.core.display_word())
        self.lives_label.config(text=f"Lives: {self.core.lives}")
        used = ", ".join(sorted(self.core.guessed_letters)).upper() or "None"
        self.used_label.config(text=f"Used letters: {used}")
        self._draw_stage()

    def _schedule_timer(self):
        self._cancel_timer()
        self._update_timer()

    def _update_timer(self):
        rem = self.core.time_remaining()
        self.timer_label.config(text=f"Time: {rem:.1f}s")
        if rem <= 0:
            # time out -> deduct life and continue
            self.core.time_up()
            self._refresh_ui()

            if self.core.lives <= 0:
                messagebox.showinfo("Game Over", f"The answer was: {self.core.secret_word}")
                self.start_new_game()
                return

        self.timer_id = self.root.after(100, self._update_timer)

    def _cancel_timer(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

    def run(self):
        self.root.mainloop()


# -----------------------------
# Run GUI
# -----------------------------
if __name__ == "__main__":
    core = HangmanCore(level='basic', max_lives=6, round_time=15)
    gui = HangmanGUI(core)
    gui.run()
