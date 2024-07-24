import unittest
from .ai import pylog_query, parse_natural_query, format_results, execute_member_query


class TestPyLogQuery(unittest.TestCase):

    def test_pylog_query_member(self):
        self.assertEqual(pylog_query(
            "Is 3 in [1, 2, 3, 4, 5]?"), "Yes, 3 is a member of the list [1, 2, 3, 4, 5].")
        self.assertEqual(pylog_query(
            "Is 6 in [1, 2, 3, 4, 5]?"), "No, 6 is not a member of the list [1, 2, 3, 4, 5].")
        self.assertEqual(pylog_query("Is 'apple' in ['apple', 'banana', 'cherry']?"),
                         "Yes, apple is a member of the list ['apple', 'banana', 'cherry'].")
        self.assertEqual(pylog_query("Is 'orange' in ['apple', 'banana', 'cherry']?"),
                         "No, orange is not a member of the list ['apple', 'banana', 'cherry'].")

    def test_parse_natural_query(self):
        self.assertEqual(parse_natural_query(
            "Is 3 in [1, 2, 3, 4, 5]?"), ("member", ["3", "[1, 2, 3, 4, 5]"]))
        self.assertEqual(parse_natural_query("Is 'apple' in ['apple', 'banana', 'cherry']?"), ("member", [
                         "apple", "['apple', 'banana', 'cherry']"]))

    def test_format_results(self):
        self.assertEqual(format_results(
            [{"X": "3"}], "3", "[1, 2, 3, 4, 5]"), "Yes, 3 is a member of the list [1, 2, 3, 4, 5].")
        self.assertEqual(format_results([], "6", "[1, 2, 3, 4, 5]"),
                         "No, 6 is not a member of the list [1, 2, 3, 4, 5].")
        self.assertEqual(format_results([{"X": "apple"}, {"X": "banana"}], "fruit", "['apple', 'banana', 'cherry']"),
                         "The following items are members of the list ['apple', 'banana', 'cherry']: apple, banana")

    def test_execute_member_query(self):
        self.assertEqual(execute_member_query(
            ["3", "[1, 2, 3, 4, 5]"]), [{"X": "3"}])
        self.assertEqual(execute_member_query(["6", "[1, 2, 3, 4, 5]"]), [])
        self.assertEqual(execute_member_query(
            ["apple", "['apple', 'banana', 'cherry']"]), [{"X": "apple"}])
        self.assertEqual(execute_member_query(
            ["orange", "['apple', 'banana', 'cherry']"]), [])

    def test_case_insensitivity(self):
        self.assertEqual(pylog_query("Is 'APPLE' in ['apple', 'banana', 'cherry']?"),
                         "Yes, apple is a member of the list ['apple', 'banana', 'cherry'].")

    def test_quoted_strings(self):
        self.assertEqual(pylog_query("Is 'apple' in ['apple', 'banana', 'cherry']?"),
                         "Yes, apple is a member of the list ['apple', 'banana', 'cherry'].")
        self.assertEqual(pylog_query('Is "apple" in ["apple", "banana", "cherry"]?'),
                         'Yes, apple is a member of the list ["apple", "banana", "cherry"].')

    def test_error_handling(self):
        self.assertTrue(pylog_query("Is apple in invalid_list").startswith(
            "Error executing PyLog query"))
        self.assertTrue(pylog_query("Invalid query").startswith(
            "Error executing PyLog query"))


if __name__ == '__main__':
    unittest.main()
