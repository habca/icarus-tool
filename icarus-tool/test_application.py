from application import Application, FileSystem
from calculator import Calculator

import unittest
import unittest.mock

class FileSystemTest(unittest.TestCase):
    filename = "tech_tree.txt"

    def test_file(self):
        """ Reading a file should not raise any errors. """

        calc = Calculator()
        with open(FileSystemTest.filename) as tiedosto:
            for line in tiedosto:
                line = line.replace("\n", "")
                if line != "" and not line.startswith("#"):
                    calc.assign_equation(line)
        
    def test_read(self):
        calc = Calculator()
        tiedosto = FileSystem(FileSystemTest.filename)
        tiedosto.read(calc)

        self.assertTrue(len(calc.resources) > 0)
        self.assertTrue(len(calc.variables) > 0)

        for resource in calc.resources:
            self.assertNotIn(resource, calc.variables)
        for variable in calc.variables:
            self.assertNotIn(variable, calc.resources)

        # self.assertEqual(calc.calculate("1 crafting_bench")[-1], "60 fiber + 50 wood + 12 stone + 20 leather")
        # self.assertEqual(calc.calculate("1 anvil_bench")[-1], "80 iron_ore + 20 wood + 10 stone")
        # self.assertEqual(calc.calculate("2 stone_furnace")[-1], "25 wood + 160 stone + 24 leather")
        # self.assertEqual(calc.calculate("40 iron_ingot")[-1], "80 iron_ore")
        # self.assertEqual(calc.calculate("8 stick")[-1], "1 wood")

class ApplicationTest(unittest.TestCase):
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
            ApplicationTest.get_output(user_input,
                Application().help))

    def test_main(self):
        user_input = [
            "1 crafting_bench = 60 fiber + 50 wood + 12 stone + 20 leather",
            "1 anvil_bench = 40 iron_ingot + 20 wood + 10 stone",
            "1 stone_furnace = 4 stick + 12 wood + 80 stone + 12 leather",
            "1 iron_ingot = 2 iron_ore",
            "10 stick = 1 wood",

            "1 crafting_bench",
            "exit",
        ]

        expected_output = [
            '------------------',
            '60 fiber',
            '50 wood',
            '20 leather',
            '12 stone',

            'TOTAL RESOURCES',
            '------------------',
            '60 fiber',
            '50 wood',
            '20 leather',
            '12 stone',
        ]

        self.maxDiff = None
        self.assertEqual(expected_output, 
            ApplicationTest.get_output(user_input,
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

# TODO testaa paaohjelmasta komentorivin parametrit

if __name__ == "__main__":
    unittest.main()
