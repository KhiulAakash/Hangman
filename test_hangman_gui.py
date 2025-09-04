import unittest
import time
from unittest.mock import patch, MagicMock
from hangman_gui import HangmanGame

class TestHangmanGUI(unittest.TestCase):
    
    def test_load_words_basic(self):
        game = HangmanGame('basic')
        words = game.load_words('basic')
        self.assertIsInstance(words, list)
        self.assertTrue(len(words) > 0)
        self.assertTrue(all(' ' not in word for word in words))
    
    def test_load_words_intermediate(self):
        game = HangmanGame('intermediate')
        phrases = game.load_words('intermediate')
        self.assertIsInstance(phrases, list)
        self.assertTrue(len(phrases) > 0)
        self.assertTrue(any(' ' in phrase for phrase in phrases))
    
    def test_select_random_word(self):
        game = HangmanGame('basic')
        game.words = ['python', 'hangman', 'testing']
        word = game.select_random_word()
        self.assertIn(word, game.words)
    
    def test_generate_display_word(self):
        game = HangmanGame('basic')
        game.secret_word = 'python'
        game.guessed_letters = set()
        
        display = game.generate_display_word()
        self.assertEqual(display, '_ _ _ _ _ _')
        
        game.guessed_letters.add('p')
        display = game.generate_display_word()
        self.assertEqual(display, 'p _ _ _ _ _')
        
        game.guessed_letters.add('y')
        game.guessed_letters.add('n')
        display = game.generate_display_word()
        self.assertEqual(display, 'p y _ _ _ n')
    
    def test_process_guess_correct(self):
        game = HangmanGame('basic')
        game.secret_word = 'python'
        game.guessed_letters = set()
        
        result = game.process_guess('p')
        self.assertTrue(result)
        self.assertIn('p', game.guessed_letters)
    
    def test_process_guess_incorrect(self):
        game = HangmanGame('basic')
        game.secret_word = 'python'
        game.guessed_letters = set()
        
        result = game.process_guess('z')
        self.assertFalse(result)
        self.assertIn('z', game.guessed_letters)
    
    def test_process_guess_already_guessed(self):
        game = HangmanGame('basic')
        game.secret_word = 'python'
        game.guessed_letters = {'p'}
        
        result = game.process_guess('p')
        self.assertIsNone(result)
    
    def test_is_word_guessed(self):
        game = HangmanGame('basic')
        game.secret_word = 'python'
        
        game.guessed_letters = {'p', 'y', 't', 'h', 'o', 'n'}
        self.assertTrue(game.is_word_guessed())
        
        game.guessed_letters = {'p', 'y', 't'}
        self.assertFalse(game.is_word_guessed())
    
    @patch('hangman_gui.HangmanGame.select_random_word')
    def test_initialize_game(self, mock_select):
        mock_select.return_value = 'python'
        game = HangmanGame('basic')
        game.initialize_game()
        
        self.assertEqual(game.secret_word, 'python')
        self.assertEqual(game.guessed_letters, set())
        self.assertEqual(game.lives, 6)
        self.assertIsNotNone(game.start_time)

if __name__ == '__main__':
    unittest.main()