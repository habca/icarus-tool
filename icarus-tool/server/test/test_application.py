import json
import unittest
import unittest.mock
from typing import Any, Callable

from application import Application, FileSystem, JsonSystem
from calculator import Calculator
from ddt import data, ddt, file_data, unpack


class FileSystemTest(unittest.TestCase):
    filename = "data/tech_tree.txt"

    # TODO: calculator is responsible for its state
    def test_read_txt(self):
        reader = FileSystem(FileSystemTest.filename)
        reader.read(calculator := Calculator())

        for resource in calculator.resources:
            self.assertNotIn(resource, calculator.variables)
            self.assertIn(resource, calculator.stations)
            self.assertNotIn(resource, calculator.options)
        for option in calculator.options:
            self.assertNotIn(option, calculator.resources)
            self.assertNotIn(option, calculator.stations)
            self.assertNotIn(option, calculator.variables)
        for variable in calculator.variables:
            self.assertNotIn(variable, calculator.resources)
            self.assertNotIn(variable, calculator.stations)
            self.assertNotIn(variable, calculator.options)
        for station in calculator.stations:
            self.assertIn(station, calculator.resources)
            self.assertNotIn(station, calculator.variables)
            self.assertNotIn(station, calculator.options)

        self.assertEqual(445, len(calculator.resources))
        self.assertEqual(445, len(calculator.stations))
        self.assertEqual(0, len(calculator.errors))
        self.assertEqual(0, len(calculator.options))


# TODO: calculator is responsible for its state
class JsonSystemTest(unittest.TestCase):
    filename = "data/crafting/D_ProcessorRecipes.json"

    def setUp(self) -> None:
        self.maxDiff = None

    def test_read_json(self):
        reader = JsonSystem(JsonSystemTest.filename)
        reader.read(calculator := Calculator())

        options = sum([len(r) for r in calculator.options.values()])

        for resource in calculator.resources:
            self.assertNotIn(resource, calculator.variables)
            self.assertIn(resource, calculator.stations)
            self.assertNotIn(resource, calculator.options)
        for option in calculator.options:
            self.assertNotIn(option, calculator.resources)
            self.assertNotIn(option, calculator.stations)
            self.assertNotIn(option, calculator.variables)
        for variable in calculator.variables:
            self.assertNotIn(variable, calculator.resources)
            self.assertNotIn(variable, calculator.stations)
            self.assertNotIn(variable, calculator.options)
        for station in calculator.stations:
            self.assertIn(station, calculator.resources)
            self.assertNotIn(station, calculator.variables)
            self.assertNotIn(station, calculator.options)

        self.assertEqual(388, resources := len(calculator.resources))
        self.assertEqual(9, errors := len(calculator.errors))
        self.assertEqual(475, options)
        self.assertTrue(643 <= resources + errors + options)


@ddt
class ApplicationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.maxDiff = None

    def test_help(self):
        expected_output = [
            "Usage:",
            "  amount name [+/- amount name ...]",
        ]
        self.assertEqual(expected_output, Application().help())

    def test_manual(self):
        expected_output = [
            "Usage:",
            "  python ./application.py [options ...] file",
            "Options:",
            "  -g --gnu          Apply GNU readline functionality to python's input.",
            "  -i --implicit     Add all the necessary intermediate steps.",
            "  -r --recursive    Show the output as a tree data structure.",
            "  -h --help         Show this user manual and exit.",
        ]

        self.assertEqual(
            expected_output,
            ApplicationTest.get_output(
                [], lambda: Application().manual("./application.py")
            ),
        )

    def test_init(self):
        user_input = [
            "./application.py",
            "./application.py -z -g",
            "./application.py -g -g",
            f"./application.py {FileSystemTest.filename} -z -g",
            f"./application.py {FileSystemTest.filename} -g -g",
            "./application.py -z -g non_existent_file",
            "./application.py -g -g non_existent_file",
        ]

        expected_output = [
            "To see usage, type --help",
            "option -z not recognized",
            "To see usage, type --help",
            "No such file or directory: '-z'",
            "No such file or directory: '-g'",
            "option -z not recognized",
            "No such file or directory: 'non_existent_file'",
        ]

        def run_test_argv() -> None:
            for error in user_input:
                application = Application()
                application.init(error.split())

        self.assertEqual(
            expected_output, ApplicationTest.get_output(user_input, run_test_argv)
        )

    @data(
        json.load(open("test/testdata/test_tech_tree_01.json")),
        json.load(open("test/testdata/test_tech_tree_02.json")),
        json.load(open("test/testdata/test_tech_tree_03.json")),
        json.load(open("test/testdata/test_tech_tree_04.json")),
        json.load(open("test/testdata/test_tech_tree_05.json")),
        json.load(open("test/testdata/test_tech_tree_06.json")),
        json.load(open("test/testdata/test_tech_tree_07.json")),
        json.load(open("test/testdata/test_tech_tree_08.json")),
        json.load(open("test/testdata/test_processor_recipes_01.json")),
        json.load(open("test/testdata/test_processor_recipes_02.json")),
    )
    @unpack
    def test_main(
        self, program_args: list[str], user_input: list[str], expected_output: list[str]
    ):
        application = Application()
        application.init(program_args)
        actual_output = ApplicationTest.get_output(user_input, application.main)
        self.assertEqual(expected_output, actual_output)

    def test_ask_optional(self):
        """
        > 1 cement_mixer
        (0) stone_furnace : 1 refined_metal = 2 metal_ore
        (0) crafting_bench : 1 rope = 12 fiber
        = AssertionError: Multiple stations: total_resources, total_resources, stone_furnace, crafting_bench
        """

        user_input = ["1 cement_mixer", "0", "exit"]
        expected_output = [
            "(0) stone_furnace : 1 refined_metal = 2 metal_ore",
            "(1) concrete_furnace : 1 refined_metal = 2 metal_ore",
            "(2) electric_furnace : 1 refined_metal = 2 metal_ore",
            "(0) crafting_bench : 1 rope = 12 fiber",
            "(1) advanced_armor_bench : 1 rope = 5 leather",
            "(2) electric_armor_bench : 1 rope = 5 leather",
            "(3) armor_bench : 1 rope = 5 leather",
            "(4) character : 1 rope = 5 leather",
        ]
        application = Application()
        application.init(["./application.py", JsonSystemTest.filename])
        actual_output = ApplicationTest.get_output(user_input, application.main)
        self.assertEqual(expected_output, actual_output)

        # Application should complete without an error.
        user_input = ["1 cement_mixer", "0", "0", "exit"]
        application = Application()
        application.init(["./application.py", JsonSystemTest.filename])
        ApplicationTest.get_output(user_input, application.main)

    @staticmethod
    def get_output(user_input: list[str], callback: Callable):
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


if __name__ == "__main__":
    unittest.main()
