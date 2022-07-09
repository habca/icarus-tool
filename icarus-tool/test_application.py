from application import Application, FileSystem
from calculator import Calculator

import unittest
import unittest.mock

class FileSystemTest(unittest.TestCase):
    filename = "data/tech_tree.txt"

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

    def test_recover(self):
        user_input = [
            "1 anvi",
            "1 anvil",
            "1 anvil_benchs + 1 anvil_bvve",
            "exit",
        ]

        expected_output = [
            'ValueError: anvi',

            'ValueError: anvil',
            'Did you mean?',
            '- anvil: anvil_bench',
            
            'ValueError: anvil_benchs, anvil_bvve',
            'Did you mean?',
            '- anvil_benchs: anvil_bench, masonry_bench, textiles_bench',
            '- anvil_bvve: anvil_bench',
        ]

        application = Application()
        application.init(["./application.py", "-g", FileSystemTest.filename])

        actual_output = ApplicationTest.get_output(user_input, application.main)

        self.maxDiff = None
        self.assertEqual(expected_output, actual_output)

    def test_argv(self):
        user_input = [
            "./application.py",
            "./application.py -i -g",
            "./application.py -g -g",
            f"./application.py {FileSystemTest.filename} -i -g",
            f"./application.py {FileSystemTest.filename} -g -g",
            f"./application.py -i -g non_existent_file",
            f"./application.py -g -g non_existent_file",
        ]

        expected_output = [
            "Usage: ./application.py -g <inputfile>",
            "option -i not recognized",
            "Usage: ./application.py -g <inputfile>",
            "Usage: ./application.py -g <inputfile>",
            "Usage: ./application.py -g <inputfile>",
            'option -i not recognized',
            "No such file or directory: 'non_existent_file'",
        ]

        def run_test_argv() -> None:
            for error in user_input:
                application = Application()
                application.init(error.split())

        self.assertEqual(expected_output,
            ApplicationTest.get_output(user_input,
                run_test_argv))

    @classmethod
    def get_output(cls, user_input: list[str], callback: callable):
        with unittest.mock.patch("builtins.print") as mock_print:
            with unittest.mock.patch("builtins.input") as mock_input:
                mock_input.side_effect = user_input
 
                callback()
 
                def argument_str(mock_call_args: tuple[str]) -> str:
                    """ Converts function arguments into an argument string. """
                    return " ".join(list(map(str, mock_call_args)))

                args = [argument_str(mock_call.args) for mock_call in mock_print.mock_calls]
                args = [arg for arg in args if arg != ""]
                return args

if __name__ == "__main__":
    unittest.main()
