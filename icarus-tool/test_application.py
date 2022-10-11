from os import stat
from typing import Any, Callable
from application import Application, FileSystem, JsonSystem
from calculator import Calculator, Equation

import unittest
import unittest.mock


class FileSystemTest(unittest.TestCase):
    filename = "data/tech_tree.txt"

    def test_read(self):
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


class JsonSystemTest(unittest.TestCase):
    filename = "data/crafting/D_ProcessorRecipes.json"

    def test_read(self):
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

        # TODO: vaihda nimet samoiksi kuin pelissa
        # self.assertIn("machining_bench", calculator.resources)
        # self.assertIn("hunting_rifle", calculator.resources)
        # self.assertIn("iron_ingot", calculator.resources)
        # self.assertIn("iron_ore", calculator.variables)
        # self.assertIn("aluminium_ore", calculator.variables)

        self.assertEqual(388, resources := len(calculator.resources))
        self.assertEqual(9, errors := len(calculator.errors))
        self.assertEqual(475, options)
        self.assertTrue(643 <= resources + errors + options)


class ApplicationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.maxDiff = None

    def test_help(self):
        user_input = ["exit"]
        expected_output = [
            ":: Usage: amount name [+ amount name] [- amount name]",
        ]
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
        self.assertEqual(
            expected_output, ApplicationTest.get_output(user_input, application.main)
        )

    def test_application_biofuel_extractor_biofuel_generator(self):
        user_input = [
            "1 biofuel_extractor + 1 biofuel_generator",
            "exit",
        ]

        expected_output = ApplicationTest.read_testfile(
            "test/test_biofuel_extractor_biofuel_generator.txt"
        )

        application = Application()
        application.init(["./application.py", "-g", FileSystemTest.filename])

        actual_output = ApplicationTest.get_output(user_input, application.main)
        self.assertEqual(expected_output, actual_output)

    def test_application_fabricator(self):
        user_input = [
            "1 fabricator",
            "exit",
        ]

        expected_output = ApplicationTest.read_testfile("test/test_fabricator.txt")

        application = Application()
        application.init(["./application.py", "-g", FileSystemTest.filename])

        actual_output = ApplicationTest.get_output(user_input, application.main)
        self.assertEqual(expected_output, actual_output)

    def test_application_cement_mixer_concrete_furnace(self):
        user_input = [
            "1 cement_mixer + 1 concrete_furnace",
            "exit",
        ]

        expected_output = ApplicationTest.read_testfile(
            "test/test_cement_mixer_concrete_furnace.txt"
        )

        application = Application()
        application.init(["./application.py", "-g", FileSystemTest.filename])
        actual_output = ApplicationTest.get_output(user_input, application.main)
        self.assertEqual(expected_output, actual_output)

    def test_application_stone_furnace_anvil_bench_machining_bench(self):
        user_input = [
            "1 stone_furnace + 1 anvil_bench + 1 machining_bench",
            "exit",
        ]

        expected_output = ApplicationTest.read_testfile(
            "test/test_stone_furnace_anvil_bench_machining_bench.txt"
        )

        application = Application()
        application.init(["./application.py", "-g", FileSystemTest.filename])
        actual_output = ApplicationTest.get_output(user_input, application.main)
        self.assertEqual(expected_output, actual_output)

    def test_application_cement_mixer_concrete_furnace_thermos(self):
        user_input = [
            "1 cement_mixer + 1 concrete_furnace + 1 thermos",
            "exit",
        ]

        expected_output = ApplicationTest.read_testfile(
            "test/test_cement_mixer_concrete_furnace_thermos.txt"
        )

        application = Application()
        application.init(["./application.py", "-g", FileSystemTest.filename])
        actual_output = ApplicationTest.get_output(user_input, application.main)
        self.assertEqual(expected_output, actual_output)

    def test_application_subtract(self):
        user_input = [
            "1 stone_furnace + 1 anvil_bench + 1 machining_bench - 10 epoxy",
            "exit",
        ]

        expected_output = ApplicationTest.read_testfile(
            "test/test_stone_furnace_anvil_bench_machining_bench_stone_wood.txt"
        )

        application = Application()
        application.init(["./application.py", "-g", FileSystemTest.filename])
        actual_output = ApplicationTest.get_output(user_input, application.main)
        self.assertEqual(expected_output, actual_output)

    def test_resolve_recipes(self):
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
            ":: Did you mean?",
            "- anvil: anvil_bench",
            "ValueError: anvil_benchs, anvil_bvve",
            ":: Did you mean?",
            "- anvil_benchs: anvil_bench, masonry_bench, animal_bed",
            "- anvil_bvve: anvil_bench, animal_bed",
        ]

        application = Application()
        application.init(["./application.py", "-g", FileSystemTest.filename])
        actual_output = ApplicationTest.get_output(user_input, application.main)
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

    def test_application_recursive(self):
        user_input = [
            "1 kit_machining_bench + 1 anvil_bench - 10 epoxy",
            "0",
            "0",
            "0",
            "0",
            "2",
            "exit",
        ]

        expected_output = ApplicationTest.read_testfile(
            "test/test_kit_machining_bench_epoxy.txt"
        )

        application = Application()
        application.init(["./application.py", "-r", JsonSystemTest.filename])
        actual_output = ApplicationTest.get_output(user_input, application.main)
        self.assertEqual(expected_output, actual_output)

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
        expected_output = [l for l in expected_output if l != ""]
        expected_output[:1] = []  # Remove first line.
        # Remove comments which clarify user interactions.
        expected_output = [l for l in expected_output if not l.startswith("#")]
        return expected_output


if __name__ == "__main__":
    unittest.main()
