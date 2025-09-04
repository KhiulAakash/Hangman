import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import random
import time
import os
from PIL import Image, ImageDraw, ImageTk

class HangmanGame:
    def __init__(self, level='basic'):
        self.level = level
        self.words = self.load_words(level)
        self.secret_word = ''
        self.guessed_letters = set()
        self.lives = 6
        self.start_time = None
        self.timer_id = None
        self.hangman_parts = []  # Store hangman drawing elements for animation
        
        # Initialize GUI
        self.root = tk.Tk()
        self.root.title("Hangman Game")
        self.root.geometry("900x700")
        self.root.resizable(False, False)
        
        # Setup styles
        self.setup_styles()
        
        # Create GUI elements
        self.create_widgets()
        
        # Start the game
        self.initialize_game()
        
    def setup_styles(self):
        self.style = ttk.Style()
        self.style.configure('Title.TLabel', font=('Arial', 24, 'bold'))
        self.style.configure('Word.TLabel', font=('Courier', 18, 'bold'))
        self.style.configure('Timer.TLabel', font=('Arial', 14))
        self.style.configure('Lives.TLabel', font=('Arial', 14))
        self.style.configure('Letter.TButton', font=('Arial', 12))
        self.style.configure('Used.TLabel', font=('Arial', 12))
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Hangman Game", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=6, pady=10)
        
        # Level indicator
        self.level_label = ttk.Label(main_frame, text=f"Level: {self.level.capitalize()}", font=('Arial', 14))
        self.level_label.grid(row=1, column=0, columnspan=6, pady=5)
        
        # Hangman canvas for animation
        self.hangman_canvas = tk.Canvas(main_frame, width=300, height=300, bg='white', relief='solid', bd=2)
        self.hangman_canvas.grid(row=2, column=0, columnspan=6, pady=10)
        
        # Word display
        self.word_label = ttk.Label(main_frame, style='Word.TLabel')
        self.word_label.grid(row=3, column=0, columnspan=6, pady=20)
        
        # Timer and lives
        info_frame = ttk.Frame(main_frame)
        info_frame.grid(row=4, column=0, columnspan=6, pady=10)
        
        self.timer_label = ttk.Label(info_frame, style='Timer.TLabel')
        self.timer_label.grid(row=0, column=0, padx=20)
        
        self.lives_label = ttk.Label(info_frame, style='Lives.TLabel')
        self.lives_label.grid(row=0, column=1, padx=20)
        
        # Used letters
        self.used_label = ttk.Label(main_frame, style='Used.TLabel')
        self.used_label.grid(row=5, column=0, columnspan=6, pady=10)
        
        # Keyboard buttons
        self.create_keyboard(main_frame)
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=7, column=0, columnspan=6, pady=20)
        
        new_game_btn = ttk.Button(control_frame, text="New Game", command=self.new_game)
        new_game_btn.grid(row=0, column=0, padx=10)
        
        quit_btn = ttk.Button(control_frame, text="Quit", command=self.root.quit)
        quit_btn.grid(row=0, column=1, padx=10)
    
    def draw_hangman(self, stage):
        """Draw the hangman animation based on the current stage (0-6)"""
        self.hangman_canvas.delete("all")
        self.hangman_parts = []
        
        # Draw the gallows (always visible)
        gallows_parts = [
            self.hangman_canvas.create_line(50, 250, 150, 250, width=4, fill='brown'),  # base
            self.hangman_canvas.create_line(100, 250, 100, 50, width=4, fill='brown'),  # pole
            self.hangman_canvas.create_line(100, 50, 180, 50, width=4, fill='brown'),   # top beam
            self.hangman_canvas.create_line(180, 50, 180, 80, width=3, fill='brown')    # rope
        ]
        self.hangman_parts.extend(gallows_parts)
        
        # Draw hangman parts based on stage with animation delay
        if stage >= 1:  # Head
            head = self.hangman_canvas.create_oval(170, 80, 190, 100, width=2, outline='black')
            self.hangman_parts.append(head)
            self.animate_part(head)
        
        if stage >= 2:  # Body
            body = self.hangman_canvas.create_line(180, 100, 180, 150, width=2, fill='black')
            self.hangman_parts.append(body)
            self.animate_part(body)
        
        if stage >= 3:  # Left arm
            left_arm = self.hangman_canvas.create_line(180, 110, 160, 130, width=2, fill='black')
            self.hangman_parts.append(left_arm)
            self.animate_part(left_arm)
        
        if stage >= 4:  # Right arm
            right_arm = self.hangman_canvas.create_line(180, 110, 200, 130, width=2, fill='black')
            self.hangman_parts.append(right_arm)
            self.animate_part(right_arm)
        
        if stage >= 5:  # Left leg
            left_leg = self.hangman_canvas.create_line(180, 150, 160, 180, width=2, fill='black')
            self.hangman_parts.append(left_leg)
            self.animate_part(left_leg)
        
        if stage >= 6:  # Right leg
            right_leg = self.hangman_canvas.create_line(180, 150, 200, 180, width=2, fill='black')
            self.hangman_parts.append(right_leg)
            self.animate_part(right_leg)
        
        # Add facial features for the final stage
        if stage >= 6:
            # Sad face when game is lost
            left_eye = self.hangman_canvas.create_oval(173, 85, 177, 89, width=1, fill='black')
            right_eye = self.hangman_canvas.create_oval(183, 85, 187, 89, width=1, fill='black')
            mouth = self.hangman_canvas.create_arc(173, 92, 187, 98, start=0, extent=-180, outline='black', width=1)
            self.hangman_parts.extend([left_eye, right_eye, mouth])
    
    def animate_part(self, part_id):
        """Animate a single hangman part with a drawing effect"""
        coords = self.hangman_canvas.coords(part_id)
        original_state = self.hangman_canvas.itemcget(part_id, 'state')
        
        # Temporarily hide the part
        self.hangman_canvas.itemconfig(part_id, state='hidden')
        self.root.update()
        
        # Animate the drawing
        if len(coords) == 4:  # For oval/rectangle
            self.hangman_canvas.itemconfig(part_id, state='normal')
        else:  # For lines
            # Get line coordinates
            x1, y1, x2, y2 = coords
            steps = 20
            dx = (x2 - x1) / steps
            dy = (y2 - y1) / steps
            
            # Create temporary line for animation
            temp_line = self.hangman_canvas.create_line(x1, y1, x1, y1, width=2, fill='black')
            
            for i in range(steps + 1):
                self.hangman_canvas.coords(temp_line, x1, y1, x1 + dx * i, y1 + dy * i)
                self.root.update()
                time.sleep(0.03)
            
            # Replace with permanent line
            self.hangman_canvas.delete(temp_line)
            self.hangman_canvas.itemconfig(part_id, state='normal')
    
    def create_keyboard(self, parent):
        keyboard_frame = ttk.Frame(parent)
        keyboard_frame.grid(row=6, column=0, columnspan=6, pady=10)
        
        # First row of letters
        first_row = "QWERTYUIOP"
        for i, letter in enumerate(first_row):
            btn = ttk.Button(keyboard_frame, text=letter, width=3, 
                            command=lambda l=letter: self.guess_letter(l),
                            style='Letter.TButton')
            btn.grid(row=0, column=i, padx=2, pady=2)
            setattr(self, f'btn_{letter}', btn)
        
        # Second row of letters
        second_row = "ASDFGHJKL"
        for i, letter in enumerate(second_row):
            btn = ttk.Button(keyboard_frame, text=letter, width=3, 
                            command=lambda l=letter: self.guess_letter(l),
                            style='Letter.TButton')
            btn.grid(row=1, column=i+1, padx=2, pady=2)
            setattr(self, f'btn_{letter}', btn)
        
        # Third row of letters
        third_row = "ZXCVBNM"
        for i, letter in enumerate(third_row):
            btn = ttk.Button(keyboard_frame, text=letter, width=3, 
                            command=lambda l=letter: self.guess_letter(l),
                            style='Letter.TButton')
            btn.grid(row=2, column=i+2, padx=2, pady=2)
            setattr(self, f'btn_{letter}', btn)
    
    def load_words(self, level):
        filename = 'words.txt' if level == 'basic' else 'phrases.txt'
        try:
            with open(filename, 'r') as file:
                words = [line.strip().lower() for line in file if line.strip()]
            return words
        except FileNotFoundError:
            # Fallback words if files not found
            if level == 'basic':
                return ['python', 'hangman', 'testing', 'programming', 'computer']
            else:
                return ['test driven development', 'unit testing', 'python programming', 'software engineering']
    
    def select_random_word(self):
        return random.choice(self.words)
    
    def initialize_game(self):
        self.secret_word = self.select_random_word()
        self.guessed_letters = set()
        self.lives = 6
        self.start_time = time.time()
        
        # Clear hangman canvas
        self.hangman_canvas.delete("all")
        self.hangman_parts = []
        
        # Draw empty gallows
        self.draw_hangman(0)
        
        # Update GUI
        self.update_word_display()
        self.update_lives_display()
        self.update_used_letters()
        
        # Enable all buttons
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            btn = getattr(self, f'btn_{letter}', None)
            if btn:
                btn.state(['!disabled'])
        
        # Start timer
        self.update_timer()
    
    def update_timer(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        
        if self.lives > 0 and not self.is_word_guessed():
            time_remaining = self.get_time_remaining()
            self.timer_label.configure(text=f"Time: {time_remaining:.1f}s")
            
            if time_remaining <= 0:
                self.time_up()
            else:
                self.timer_id = self.root.after(100, self.update_timer)
    
    def get_time_remaining(self):
        elapsed = time.time() - self.start_time
        return max(0, 15 - elapsed)
    
    def time_up(self):
        self.lives -= 1
        self.start_time = time.time()  # Reset timer
        self.update_lives_display()
        self.draw_hangman(6 - self.lives)  # Update hangman animation
        
        if self.lives <= 0:
            self.game_over()
        else:
            self.update_timer()
    
    def generate_display_word(self):
        display = []
        for char in self.secret_word:
            if char == ' ':
                display.append(' ')
            elif char in self.guessed_letters:
                display.append(char)
            else:
                display.append('_')
        return ' '.join(display)
    
    def update_word_display(self):
        display = self.generate_display_word()
        self.word_label.configure(text=display)
    
    def update_lives_display(self):
        self.lives_label.configure(text=f"Lives: {self.lives}")
    
    def update_used_letters(self):
        used = ", ".join(sorted(self.guessed_letters)) if self.guessed_letters else "None"
        self.used_label.configure(text=f"Used letters: {used}")
    
    def process_guess(self, letter):
        letter = letter.lower()
        
        if letter in self.guessed_letters:
            return None  # Already guessed
        
        self.guessed_letters.add(letter)
        
        if letter in self.secret_word:
            return True  # Correct guess
        else:
            self.lives -= 1
            return False  # Incorrect guess
    
    def is_word_guessed(self):
        for char in self.secret_word:
            if char != ' ' and char not in self.guessed_letters:
                return False
        return True
    
    def guess_letter(self, letter):
        # Disable the button
        btn = getattr(self, f'btn_{letter}')
        btn.state(['disabled'])
        
        # Process the guess
        result = self.process_guess(letter)
        
        # Update displays
        self.update_word_display()
        self.update_lives_display()
        self.update_used_letters()
        
        # Update hangman animation for wrong guesses
        if result == False:
            self.draw_hangman(6 - self.lives)
        
        # Check game state
        if self.is_word_guessed():
            self.victory()
        elif self.lives <= 0:
            self.game_over()
        
        # Reset timer if correct guess
        if result:
            self.start_time = time.time()
            self.update_timer()
    
    def victory(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        
        # Add happy face to hangman
        if self.hangman_parts and len(self.hangman_parts) > 4:  # If head exists
            head_coords = self.hangman_canvas.coords(self.hangman_parts[4])
            if len(head_coords) == 4:  # Oval coordinates
                x1, y1, x2, y2 = head_coords
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                
                # Draw happy eyes and mouth
                self.hangman_canvas.create_oval(center_x-7, center_y-5, center_x-3, center_y-1, fill='black')
                self.hangman_canvas.create_oval(center_x+3, center_y-5, center_x+7, center_y-1, fill='black')
                self.hangman_canvas.create_arc(center_x-5, center_y, center_x+5, center_y+6, start=0, extent=-180, outline='black', width=2)
        
        messagebox.showinfo("Congratulations!", f"You won! The word was: {self.secret_word}")
    
    def game_over(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        messagebox.showinfo("Game Over", f"Sorry, you lost. The word was: {self.secret_word}")
    
    def new_game(self):
        # Ask for level
        level = simpledialog.askstring("New Game", "Choose level (basic/intermediate):", 
                                      initialvalue=self.level)
        if level and level.lower() in ['basic', 'intermediate']:
            self.level = level.lower()
            self.words = self.load_words(self.level)
            self.level_label.configure(text=f"Level: {self.level.capitalize()}")
        
        self.initialize_game()
    
    def run(self):
        self.update_timer()
        self.root.mainloop()

if __name__ == '__main__':
    # Ask for level at startup
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    level = simpledialog.askstring("Hangman", "Choose level (basic/intermediate):", 
                                  initialvalue="basic")
    if not level or level.lower() not in ['basic', 'intermediate']:
        level = 'basic'
    else:
        level = level.lower()
    
    root.destroy()
    
    # Start the game
    game = HangmanGame(level)
    game.run()