from typing import Any, Callable
from application import Application, FileSystem
from calculator import Calculator

import unittest
import unittest.mock


class FileSystemTest(unittest.TestCase):
    filename = "data/tech_tree.txt"

    def test_file(self):
        """Reading a file should not raise any errors."""

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
        self.assertEqual(len(calc.stations), len(calc.resources))

        for resource in calc.resources:
            self.assertNotIn(resource, calc.variables)
        for variable in calc.variables:
            self.assertNotIn(variable, calc.resources)
            self.assertNotIn(variable, calc.stations)


class ApplicationTest(unittest.TestCase):
    filename = "data/output.txt"

    def test_help(self):
        user_input = ["exit"]
        expected_output = [
            "Welcome to Icarus tool!",
            "-----------------------",
            "amount name [+ amount name]",
        ]

        self.maxDiff = None
        self.assertEqual(
            expected_output, ApplicationTest.get_output(user_input, Application().help)
        )

    def test_main(self):
        user_input = [
            "1 crafting_bench",
            "exit",
        ]

        expected_output = [
            "==================",
            "CHARACTER",
            "==================",
            "1 crafting_bench",
            "------------------",
            "60 fiber",
            "50 wood",
            "20 leather",
            "12 stone",
            "==================",
            "TOTAL RESOURCES",
            "==================",
            "1 crafting_bench",
            "------------------",
            "60 fiber",
            "50 wood",
            "20 leather",
            "12 stone",
        ]

        lines = [
            "character : 1 crafting_bench = 60 fiber + 50 wood + 12 stone + 20 leather",
            "crafting_bench : 1 anvil_bench = 40 iron_ingot + 20 wood + 10 stone",
            "crafting_bench : 1 stone_furnace = 4 stick + 12 wood + 80 stone + 12 leather",
            "stone_furnace : 1 iron_ingot = 2 iron_ore",
            "character : 10 stick = 1 wood",
        ]

        application = Application()
        for line in lines:
            application.calculator.assign_equation(line)

        self.maxDiff = None
        self.assertEqual(
            expected_output, ApplicationTest.get_output(user_input, application.main)
        )

    def test_application_biofuel_extractor_biofuel_generator(self):
        user_input = [
            "1 biofuel_extractor + 1 biofuel_generator",
            "exit",
        ]

        expected_output = ApplicationTest.read_testfile(
            "data/test_biofuel_extractor_biofuel_generator.txt"
        )

        application = Application()
        application.init(["./application.py", "-g", FileSystemTest.filename])

        actual_output = ApplicationTest.get_output(user_input, application.main)

        self.maxDiff = None
        self.assertEqual(expected_output, actual_output)

    def test_application_fabricator(self):
        user_input = [
            "1 fabricator",
            "exit",
        ]

        expected_output = ApplicationTest.read_testfile("data/test_fabricator.txt")

        application = Application()
        application.init(["./application.py", "-g", FileSystemTest.filename])

        actual_output = ApplicationTest.get_output(user_input, application.main)

        self.maxDiff = None
        self.assertEqual(expected_output, actual_output)

    def test_application_cement_mixer_concrete_furnace(self):
        user_input = [
            "1 cement_mixer + 1 concrete_furnace",
            "exit",
        ]

        expected_output = ApplicationTest.read_testfile(
            "data/test_cement_mixer_concrete_furnace.txt"
        )

        application = Application()
        application.init(["./application.py", "-g", FileSystemTest.filename])

        actual_output = ApplicationTest.get_output(user_input, application.main)

        self.maxDiff = None
        self.assertEqual(expected_output, actual_output)

    def test_application_stone_furnace_anvil_bench_machining_bench(self):
        user_input = [
            "1 stone_furnace + 1 anvil_bench + 1 machining_bench",
            "exit",
        ]

        expected_output = ApplicationTest.read_testfile(
            "data/test_stone_furnace_anvil_bench_machining_bench.txt"
        )

        application = Application()
        application.init(["./application.py", "-g", FileSystemTest.filename])

        actual_output = ApplicationTest.get_output(user_input, application.main)

        self.maxDiff = None
        self.assertEqual(expected_output, actual_output)

    def test_recover(self):
        user_input = [
            "1 anvi",
            "1 anvil",
            "1 anvil_benchs + 1 anvil_bvve",
            "exit",
        ]

        expected_output = [
            "ValueError: anvi",
            "ValueError: anvil",
            "Did you mean?",
            "- anvil: anvil_bench",
            "ValueError: anvil_benchs, anvil_bvve",
            "Did you mean?",
            "- anvil_benchs: anvil_bench, masonry_bench, animal_bed",
            "- anvil_bvve: anvil_bench, animal_bed",
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
            "./application.py -i -g non_existent_file",
            "./application.py -g -g non_existent_file",
        ]

        expected_output = [
            "Usage: ./application.py -g data/tech_tree.txt",
            "option -i not recognized",
            "Usage: ./application.py -g data/tech_tree.txt",
            "No such file or directory: '-i'",
            "No such file or directory: '-g'",
            "option -i not recognized",
            "No such file or directory: 'non_existent_file'",
        ]

        def run_test_argv() -> None:
            for error in user_input:
                application = Application()
                application.init(error.split())

        self.assertEqual(
            expected_output, ApplicationTest.get_output(user_input, run_test_argv)
        )

    @classmethod
    def get_output(cls, user_input: list[str], callback: Callable):
        with unittest.mock.patch("builtins.print") as mock_print:
            with unittest.mock.patch("builtins.input") as mock_input:
                mock_input.side_effect = user_input

                callback()

                def argument_str(mock_call_args: tuple[Any, ...]) -> str:
                    """Converts function arguments into an argument string."""
                    return " ".join(list(map(str, mock_call_args)))

                args = [
                    argument_str(mock_call.args) for mock_call in mock_print.mock_calls
                ]
                args = [arg for arg in args if arg != ""]
                return args

    @classmethod
    def read_testfile(cls, filename) -> list[str]:
        with open(filename) as reader:
            data = reader.read()
        expected_output = data.splitlines()
        expected_output[:1] = []  # Remove first line.
        return expected_output


if __name__ == "__main__":
    unittest.main()
