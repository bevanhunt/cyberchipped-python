from z3 import Solver, Bool, And, Implies, Not, unsat, sat
import unittest
from unittest.mock import MagicMock, patch
import json
from cyberchipped.ai import AI
from z3 import Solver, Bool, Not, sat, unsat, is_expr
from dotenv import load_dotenv
import os
load_dotenv()


class TestAI(unittest.TestCase):
    def setUp(self):
        self.ai = AI(os.getenv("OPENAI_API_KEY"),
                     "TestAI", "Test instructions", None)

    def test_create_solver_and_vars(self):
        solver, vars = self.ai.create_solver_and_vars()
        self.assertIsInstance(solver, Solver)
        self.assertEqual(vars, {})

    def test_add_transitive_property(self):
        solver = Solver()
        vars = {
            "A is taller than B": Bool("A_taller_B"),
            "B is taller than C": Bool("B_taller_C"),
            "A is taller than C": Bool("A_taller_C"),
            "C is taller than D": Bool("C_taller_D"),
            "A is taller than D": Bool("A_taller_D"),
            "X is red": Bool("X_is_red")  # Non-height related variable
        }

        self.ai.add_transitive_property(solver, vars)

        # Test case 1: If A > B and B > C, then A > C
        solver.push()
        solver.add(vars["A is taller than B"])
        solver.add(vars["B is taller than C"])
        self.assertEqual(solver.check(Not(vars["A is taller than C"])), unsat)
        solver.pop()

        # Test case 2: If A > B, B > C, and C > D, then A > D
        solver.push()
        solver.add(vars["A is taller than B"])
        solver.add(vars["B is taller than C"])
        solver.add(vars["C is taller than D"])
        self.assertEqual(solver.check(Not(vars["A is taller than D"])), unsat)
        solver.pop()

        # Test case 3: Transitivity should not force a relationship that wasn't implied
        solver.push()
        solver.add(vars["A is taller than B"])
        solver.add(vars["C is taller than D"])
        self.assertEqual(solver.check(Not(vars["A is taller than C"])), sat)
        self.assertEqual(solver.check(Not(vars["A is taller than D"])), sat)
        solver.pop()

    def test_check_argument_valid_and_true(self):
        parsed_argument = {
            "premises": [
                {"type": "implication", "antecedents": [
                    "A"], "consequent": "B"},
                {"type": "statement", "statement": "A", "value": True}
            ],
            "conclusion": {"statement": "B", "value": True}
        }
        result = self.ai.check_argument(parsed_argument)
        self.assertEqual(result, "valid_and_true")

    def test_check_argument_valid_but_not_always_true(self):
        parsed_argument = {
            "premises": [
                {"type": "implication", "antecedents": [
                    "A"], "consequent": "B"},
                {"type": "statement", "statement": "B", "value": True}
            ],
            "conclusion": {"statement": "A", "value": True}
        }
        result = self.ai.check_argument(parsed_argument)
        self.assertEqual(result, "valid_but_not_always_true")

    def test_prontoqa_example(self):
        parsed_argument = {
            "premises": [
                {"type": "implication", "antecedents": [
                    "x is taller than y", "y is taller than z"], "consequent": "x is taller than z"},
                {"type": "statement",
                    "statement": "John is taller than Mary", "value": True},
                {"type": "statement", "statement": "Mary is taller than Tom", "value": True}
            ],
            "conclusion": {"statement": "John is taller than Tom", "value": True}
        }
        result = self.ai.check_argument(parsed_argument)
        self.assertEqual(result, "valid_and_true")

    def test_proofwriter_example(self):
        parsed_argument = {
            "premises": [
                {"type": "implication", "antecedents": [
                    "Anne is an aardvark"], "consequent": "Anne likes ants"},
                {"type": "implication", "antecedents": [
                    "Bob is a bear"], "consequent": "Bob likes honey"},
                {"type": "statement", "statement": "Anne is an aardvark", "value": True},
                {"type": "statement", "statement": "Bob is a bear", "value": True}
            ],
            "conclusion": {"statement": "Anne likes ants and Bob likes honey", "value": True}
        }
        result = self.ai.check_argument(parsed_argument)
        self.assertEqual(result, "valid_and_true")

    def test_get_or_create_var(self):
        vars = {}
        var1 = self.ai.get_or_create_var(vars, "test1")
        self.assertIn("test1", vars)
        self.assertTrue(is_expr(var1))
        self.assertEqual(str(vars["test1"]), str(var1))

        var2 = self.ai.get_or_create_var(vars, "test1")
        self.assertEqual(str(var1), str(var2))

        # Test with a different statement
        var3 = self.ai.get_or_create_var(vars, "test2")
        self.assertIn("test2", vars)
        self.assertTrue(is_expr(var3))
        self.assertEqual(str(vars["test2"]), str(var3))
        self.assertNotEqual(str(var1), str(var3))

    def test_add_premise_to_solver_implication(self):
        solver, vars = self.ai.create_solver_and_vars()
        premise = {
            "type": "implication",
            "antecedents": ["A", "B"],
            "consequent": "C"
        }
        self.ai.add_premise_to_solver(solver, vars, premise)
        self.assertEqual(len(solver.assertions()), 1)
        self.assertIn("A", vars)
        self.assertIn("B", vars)
        self.assertIn("C", vars)

    def test_add_premise_to_solver_statement(self):
        solver, vars = self.ai.create_solver_and_vars()
        premise = {
            "type": "statement",
            "statement": "X",
            "value": True
        }
        self.ai.add_premise_to_solver(solver, vars, premise)
        self.assertEqual(len(solver.assertions()), 1)
        self.assertIn("X", vars)

    def test_check_premise_consistency_consistent(self):
        solver, vars = self.ai.create_solver_and_vars()
        premise1 = {"type": "statement", "statement": "A", "value": True}
        premise2 = {"type": "statement", "statement": "B", "value": False}
        self.ai.add_premise_to_solver(solver, vars, premise1)
        self.ai.add_premise_to_solver(solver, vars, premise2)
        self.assertTrue(self.ai.check_premise_consistency(solver))

    def test_check_premise_consistency_inconsistent(self):
        solver, vars = self.ai.create_solver_and_vars()
        premise1 = {"type": "statement", "statement": "A", "value": True}
        premise2 = {"type": "statement", "statement": "A", "value": False}
        self.ai.add_premise_to_solver(solver, vars, premise1)
        self.ai.add_premise_to_solver(solver, vars, premise2)
        self.assertFalse(self.ai.check_premise_consistency(solver))

    def test_interpret_result_valid_and_true(self):
        result = "valid_and_true"
        conclusion = {"statement": "A is true", "value": True}
        interpretation = self.ai.interpret_result(result, conclusion)
        self.assertEqual(
            interpretation, "The argument is valid and true. A is true is indeed true.")

    def test_interpret_result_valid_but_not_always_true(self):
        result = "valid_but_not_always_true"
        conclusion = {"statement": "A is true", "value": True}
        interpretation = self.ai.interpret_result(result, conclusion)
        self.assertEqual(
            interpretation, "The argument is valid, but A is true is not necessarily true.")

    def test_interpret_result_invalid_or_inconsistent(self):
        result = "invalid_or_inconsistent"
        conclusion = {"statement": "A is true", "value": True}
        interpretation = self.ai.interpret_result(result, conclusion)
        self.assertEqual(
            interpretation, "The argument is invalid or inconsistent.")

    def test_parse_argument(self):
        argument = "If A, then B. A is true. Therefore, B is true."
        parsed = self.ai.parse_argument(argument)

        self.assertIsInstance(parsed, dict)
        self.assertIn("premises", parsed)
        self.assertIn("conclusion", parsed)

        # Check the structure of the parsed argument
        self.assertEqual(len(parsed["premises"]), 2)
        self.assertIn("type", parsed["premises"][0])
        self.assertIn("antecedents", parsed["premises"][0])
        self.assertIn("consequent", parsed["premises"][0])
        self.assertIn("type", parsed["premises"][1])
        self.assertIn("statement", parsed["premises"][1])
        self.assertIn("value", parsed["premises"][1])

        self.assertIn("statement", parsed["conclusion"])
        self.assertIn("value", parsed["conclusion"])

    def test_english_to_logic(self):
        # Mock the parse_argument method
        self.ai.parse_argument = MagicMock(return_value={
            "premises": [
                {"type": "implication", "antecedents": [
                    "A"], "consequent": "B"},
                {"type": "statement", "statement": "A", "value": True}
            ],
            "conclusion": {"statement": "B", "value": True}
        })

        result = self.ai.english_to_logic(
            "If A, then B. A is true. Therefore, B is true.")

        self.ai.parse_argument.assert_called_once()
        self.assertIsInstance(result, str)
        self.assertIn("valid", result.lower())


if __name__ == '__main__':
    unittest.main()
