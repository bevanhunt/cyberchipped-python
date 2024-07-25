import unittest
from .ai import english_to_logic


class TestPyLogQuery(unittest.TestCase):

    def test_english_to_logic_valid_true(self):
        argument = "If it rains, then the ground is wet. It rains is true. Therefore, the ground is wet is true."
        expected = "The argument is valid and true. the ground is wet is indeed true."
        self.assertEqual(english_to_logic(argument), expected)

    def test_english_to_logic_valid_false_conclusion(self):
        argument = "If it's sunny, then it's hot. It's sunny is true. Therefore, it's hot is false."
        expected = "The argument is valid, but the conclusion is false. It's sunny is true, and it's hot is true, but the conclusion states it is false."
        self.assertEqual(english_to_logic(argument), expected)

    def test_english_to_logic_invalid_conclusion(self):
        argument = "If it's sunny, then it's hot. It's sunny is true. Therefore, it's cold is true."
        expected = "The argument is invalid. The conclusion 'it's cold' does not match the consequent 'it's hot'."
        self.assertEqual(english_to_logic(argument), expected)

    def test_english_to_logic_false_premise(self):
        argument = "If it's raining, then the streets are wet. It's raining is false. Therefore, the streets are wet is true."
        expected = "The argument is valid, but it's raining is false, so no definite conclusion can be drawn about the streets are wet."
        self.assertEqual(english_to_logic(argument), expected)


if __name__ == '__main__':
    unittest.main()
