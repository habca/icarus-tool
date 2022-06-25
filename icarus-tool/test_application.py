from application import Application, FileSystem
from calculator import Calculator
import utils

import unittest
import unittest.mock

class TestFileSystem(unittest.TestCase):

    def test_file(self):
        calc = Calculator()

        with open("tech_tree.txt") as tiedosto:
            for line in tiedosto:
                _, line = utils.extract(line, sep="")
                if line == "" or line.startswith("#"):
                    continue
                calc.syntax_check(line)
        
    def test_read(self):
        calc = Calculator()
        tiedosto = FileSystem("tech_tree.txt")
        tiedosto.read(calc)

        self.assertEqual(calc.calculate("1 crafting_bench"), "60 fiber + 50 wood + 12 stone + 20 leather")
        self.assertEqual(calc.calculate("1 anvil_bench"), "80 iron_ore + 20 wood + 10 stone")
        self.assertEqual(calc.calculate("2 stone_furnace"), "25 wood + 160 stone + 24 leather")
        self.assertEqual(calc.calculate("2 20 iron_ingot"), "80 iron_ore")
        self.assertEqual(calc.calculate("8 stick"), "1 wood")

class TestApplication(unittest.TestCase):

    def test_help(self):
        user_input = ["exit"]
        expected_output = [
            "Welcome to use Icarus tool",
            "--------------------------",
            "amount name = amount name [+ amount name]",
            "amount name [+ amount name]",
        ]

        self.maxDiff = None
        self.assertEqual(expected_output, 
            TestApplication.get_output(user_input,
                Application().main))

    def test_main(self):
        user_input = [
            "1 crafting_bench = 60 fiber + 50 wood + 12 stone + 20 leather",
            "1 anvil_bench = 40 iron_ingot + 20 wood + 10 stone",
            "1 stone_furnace = 4 stick + 12 wood + 80 stone + 12 leather",
            "1 iron_ingot = 2 iron_ore",
            "10 stick = 1 wood",

            "1 anvil_bench",
            "2 stone_furnace",
            "40 iron_ingot",
            "8 stick",
            "exit",
        ]

        expected_output = [
           'Welcome to use Icarus tool',
            '--------------------------',
            'amount name = amount name [+ amount name]',
            'amount name [+ amount name]',
            '---------------',
            '40 iron_ingot\n20 wood\n10 stone',
            '---------------',
            '80 iron_ore\n20 wood\n10 stone',
            '-----------------',
            '160 stone\n 24 leather\n 24 wood\n  8 stick',
            '-----------------',
            '160 stone\n 25 wood\n 24 leather',
            '---------------',
            '80 iron_ore',
            '---------',
            '1 wood',
        ]

        self.maxDiff = None
        self.assertEqual(expected_output, 
            TestApplication.get_output(user_input,
                Application().main))

    @classmethod
    def get_output(cls, user_input: list, callback: callable):
        with unittest.mock.patch("builtins.print") as mock_print:
            with unittest.mock.patch("builtins.input") as mock_input:
                mock_input.side_effect = user_input
 
                callback()
 
                actual = []
                for mock_call in mock_print.mock_calls:
                    actual += list(map(str, mock_call.args))
                return actual

if __name__ == "__main__":
    unittest.main()
