import random
import time
import os

class Hangman:
    def __init__(self, level='basic'):
        self.level = level
        self.words = self.load_words(level)
        self.secret_word = ''
        self.guessed_letters = set()
        self.lives = 6
        self.start_time = None
    
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
    
    def get_time_remaining(self):
        elapsed = time.time() - self.start_time
        return max(0, 15 - elapsed)
    
    def is_time_up(self):
        return self.get_time_remaining() <= 0
    
    def play(self):
        self.initialize_game()
        
        print(f"Welcome to Hangman ({self.level} level)!")
        print("You have 15 seconds to guess each letter.")
        print("Type 'quit' to exit the game.\n")
        
        while self.lives > 0:
            time_remaining = self.get_time_remaining()
            print(f"Time remaining: {time_remaining:.1f} seconds")
            print(f"Lives remaining: {self.lives}")
            print(self.generate_display_word())
            
            if self.is_time_up():
                print("\nTime's up! You lose a life.")
                self.lives -= 1
                self.start_time = time.time()  # Reset timer
                continue
            
            guess = input("Guess a letter: ").lower()
            
            if guess == 'quit':
                print(f"\nGame ended. The word was: {self.secret_word}")
                break
            
            if len(guess) != 1 or not guess.isalpha():
                print("Please enter a single letter.")
                continue
            
            result = self.process_guess(guess)
            
            if result is None:
                print("You already guessed that letter.")
            elif result:
                print("Correct guess!")
            else:
                print("Incorrect guess!")
            
            if self.is_word_guessed():
                print(f"\nCongratulations! You guessed the word: {self.secret_word}")
                break
            
            print()  # Empty line for readability
        
        if self.lives <= 0:
            print(f"\nGame over! The word was: {self.secret_word}")

if __name__ == '__main__':
    import sys
    
    level = 'basic'
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'intermediate':
        level = 'intermediate'
    
    game = Hangman(level)
    game.play()