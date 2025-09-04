import time
import unittest
from hangman import HangmanCore, is_valid_phrase, DICTIONARY_WORDS

class TestHangmanCore(unittest.TestCase):
    def setUp(self):
        self.core = HangmanCore(level='basic', max_lives=6, round_time=0.2)  # fast timer for tests
        self.core.pool = ["python"]  # deterministic
        self.core.new_round()

    def test_new_round_sets_word_and_resets_state(self):
        self.assertEqual(self.core.secret_word, "python")
        self.assertEqual(self.core.lives, 6)
        self.assertEqual(self.core.guessed_letters, set())
        self.assertTrue(0 <= self.core.time_remaining() <= self.core.round_time)

    def test_process_guess_correct_and_reveal(self):
        self.assertTrue(self.core.process_guess('p'))
        self.assertIn('p', self.core.guessed_letters)
        self.assertIn('p', self.core.display_word())

    def test_process_guess_wrong_deducts_life(self):
        lives_before = self.core.lives
        self.assertFalse(self.core.process_guess('z'))
        self.assertEqual(self.core.lives, lives_before - 1)

    def test_process_guess_repeated_returns_none(self):
        self.core.process_guess('p')
        self.assertIsNone(self.core.process_guess('p'))

    def test_is_word_guessed(self):
        for ch in set("python"):
            self.core.process_guess(ch)
        self.assertTrue(self.core.is_word_guessed())

    def test_time_up_deducts_life(self):
        lives_before = self.core.lives
        # Let the timer expire logically
        time.sleep(self.core.round_time + 0.05)
        self.core.time_up()
        self.assertEqual(self.core.lives, lives_before - 1)

    def test_level_switch_refreshes_pool(self):
        self.core.set_level('intermediate')
        self.core.new_round()
        self.assertIn(' ', self.core.secret_word)  # phrase has a space

class TestDictionaryValidation(unittest.TestCase):
    def test_valid_phrase(self):
        self.assertTrue(is_valid_phrase("unit testing"))
        self.assertTrue(is_valid_phrase("software engineer"))

    def test_invalid_phrase(self):
        # uses a word not in DICTIONARY_WORDS
        invalid = "fuzzy unicorn"
        # guard to ensure this is actually not in dictionary
        self.assertFalse(set(invalid.split()).issubset(DICTIONARY_WORDS))
        self.assertFalse(is_valid_phrase(invalid))

if __name__ == "__main__":
    unittest.main()
