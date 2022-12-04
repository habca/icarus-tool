import getopt
import json
import sys
from abc import ABC, abstractmethod
from collections import deque
from typing import Any

from calculator import Calculator, Equation, EquationTree, Resource


class FileSystem:
    """Read equations from file rather than user input."""

    def __init__(self, filename: str):
        self.filename = filename

    def read(self, calculator: Calculator) -> None:
        """
        Forwards assignment equations to the calculator.
        Function caller should handle FileNotFoundError!
        """

        with open(self.filename) as file:
            for line in file:
                line = line.replace("\n", "")
                # Skip comments and empty lines.
                if not (line == "" or line.startswith("#")):
                    calculator.assign_equation(line)


class JsonSystem(FileSystem):
    def __init__(self, filename: str):
        super().__init__(filename)

    def read(self, calculator: Calculator) -> None:
        with open(self.filename) as file:
            data = file.read()
        recipes = json.loads(data)

        for recipe in recipes["Rows"]:
            try:
                for line in JsonSystem.to_equation(recipe):
                    calculator.assign_equation(line)
            except IndexError:
                calculator.errors.append(recipe)

    @classmethod
    def to_equation(cls, recipe: dict[str, Any]) -> list[str]:
        lines: list[str] = []

        # Station
        for i in range(len(recipe["RecipeSets"])):
            line = recipe["RecipeSets"][i]["RowName"].lower()
            line += " : "

            # Output
            line += str(recipe["Outputs"][0]["Count"])
            line += " "
            line += recipe["Outputs"][0]["Element"]["RowName"].lower()
            line += " = "

            # Input
            line += str(recipe["Inputs"][0]["Count"])
            line += " "
            line += recipe["Inputs"][0]["Element"]["RowName"].lower()
            for i in range(1, len(recipe["Inputs"])):
                line += " + "
                line += str(recipe["Inputs"][i]["Count"])
                line += " "
                line += recipe["Inputs"][i]["Element"]["RowName"].lower()

            lines.append(line)

        return lines


class Completer:
    def __init__(self, keywords: list[str]):
        self.keywords = sorted(keywords)
        import readline

        readline.parse_and_bind("tab: complete")
        readline.set_completer(self.auto_complete)

    def auto_complete(self, text: str, state: int):
        options = [var for var in self.keywords if var.startswith(text)]
        if state < len(options):
            return options[state]
        else:
            return None


class Application:
    def __init__(self):
        self.calculator = Calculator()

        # Algorithm depends on command line arguments.
        self.algorithm: Algorithm = Iterative(self)

        # Process the equation before applying the algorithm.
        self.preprocessor: Preprocessor = Explicit(self)

        self.separator = "-" * 72

    def manual(self, script: str):
        print()
        print("Usage:")
        print("  python", script, "[options ...]", "file")
        print()
        print("Options:")
        print("  -g --gnu          Apply GNU readline functionality to python's input.")
        print("  -i --implicit     Add all the necessary intermediate steps.")
        print("  -r --recursive    Show the output as a tree data structure.")
        print("  -h --help         Show this user manual and exit.")
        print()

    def help(self) -> list[str]:
        output: list[str] = []
        output.append("Usage:")
        output.append("  amount name [+/- amount name ...]")
        return output

    def ask_input(self) -> str:
        """Throws SyntaxError, ValueError or SystemExit!"""

        # Line break for a readable terminal output.
        print()

        # Replace whitespace sequences with a spacebar.
        equation = " ".join(input("> ").split())

        # Terminates the program by raising a SystemExit.
        if equation in ("exit", "quit"):
            raise SystemExit

        # Separator should match the user input line.
        self.separator = "-" * (len(equation) + 2)

        # Return a valid equation.
        return equation

    def parse_input(self, equation: str) -> Equation:
        # Validate an equation before processing any further.
        self.calculator.validator.validate_syntax_calculation(equation)

        equation_obj: Equation = Equation.parse(equation)

        # Ensure there are only pre-assigned variable names.
        self.calculator.validator.validate_value_calculation(equation_obj)

        return equation_obj

    def recover(self, equation: str) -> list[str]:
        output: list[str] = []
        resources = Equation.parse(equation)
        similar_words = self.calculator.find_similar(resources)
        if similar_words != {}:
            output.append("")  # Line break for a readable terminal output.
            output.append(f":: Did you mean?")
            for name, word_list in similar_words.items():
                message = "- " + name + ": " + ", ".join(word_list)
                output.append(message)
        return output

    def ask_optional(self, options: list[str]) -> int:
        """Callback function to request user interaction."""

        for i, option in enumerate(options):
            print(f"({i}) {option}")

        while True:
            choice = input(":: Which recipe would you like to use? ")
            print()  # Empty line to make welcome text readable.

            if choice in ("exit", "quit"):
                raise SystemExit

            if choice.isdigit() and 0 <= int(choice) < len(options):
                return int(choice)

    def print_output(self, equations: list[Equation]) -> list[str]:
        # To make program's output more readable.
        separator: str = self.separator
        output: list[str] = []

        """
        > 1 anvil_bench + 1 crafting_bench
        ==================================
        CHARACTER
        ==================================
        1 crafting_bench
        ----------------------------------
        60 fiber
        50 wood
        20 leather
        12 stone
        ==================================
        STONE FURNACE
        ==================================
        40 iron_ingot
        ----------------------------------
        80 iron_ore
        ==================================
        CRAFTING BENCH
        ==================================
        1 anvil_bench
        ----------------------------------
        40 iron_ingot
        20 wood
        10 stone
        """

        previous_station: str | None = None
        for i in range(len(equations)):

            resources = equations[i]
            resources = resources.suodata(all=False, round=False)
            resources = resources.sort_resources()
            resources_str = resources.format_resources()

            # After subraction there may not be anything to craft.
            if not resources.resources:
                continue

            # Print the name of station when it changes.
            # Otherwise separate equations from each other.
            current_station = self.calculator.get_station(resources)
            if current_station != previous_station:
                output.append(separator.replace("-", "="))
                output.append(current_station.replace("_", " ").upper())
                output.append(separator.replace("-", "="))
            else:
                output.append(separator.replace("-", "="))

            # Update current station.
            previous_station = current_station

            # Print recipes above the separator.
            for resource_name in resources_str:
                output.append(resource_name)

            # Separate recipes and resources by the separator.
            output.append(separator)

            # Pick resources craftable in the current station only.
            resources = self.calculator.resources_per_station(equations[i])
            resources = resources.suodata(all=False, round=False)
            resources = resources.sort_resources()
            resources_str = resources.format_resources()

            # Print resources below the separator.
            for resource_name in resources_str:
                output.append(resource_name)

        return output

    def print_total_resources(
        self, equation: Equation, user_input: Equation
    ) -> list[str]:
        # To make program's output more readable.
        separator: str = self.separator
        output: list[str] = []

        """
        > 1 anvil_bench + 1 crafting_bench
        ==================================
        TOTAL RESOURCES
        ==================================
        1 anvil_bench
        1 crafting_bench
        ----------------------------------
        80 iron_ore
        70 wood
        60 fiber
        22 stone
        20 leather
        """

        # From here, print the program's input.
        resources = user_input
        resources = resources.suodata(all=True, round=False)
        resources = resources.sort_resources()
        resources_str = resources.format_resources()

        # There may be multiple crafting stations.
        output.append(separator.replace("-", "="))
        output.append("TOTAL RESOURCES")
        output.append(separator.replace("-", "="))

        # Print sorted and formated user input.
        for resource_name in resources_str:
            output.append(resource_name)

        # Separate crafting recipes and material costs.
        output.append(separator)

        # From here, print the program's output.
        resources = equation.suodata(all=True, round=True)
        resources = resources.sort_resources()
        resources_str = resources.format_resources()

        # Print sorted and formated program output.
        for resource_name in resources_str:
            output.append(resource_name)

        return output

    def print_output_recursive(self, root: EquationTree) -> list[str]:

        # To make program's output more readable.
        separator: str = self.separator
        output: list[str] = []

        """
        > 1 anvil_bench + 1 crafting_bench
        ==================================
        RECURSIVE DATA STRUCTURE
        ==================================
        1 crafting_bench [character]
        60 fiber
        50 wood
        12 stone
        20 leather
        ----------------------------------
        1 anvil_bench [crafting_bench]
        40 iron_ingot [stone_furnace]
            80 iron_ore
        20 wood
        10 stone
        """

        def traverse(root: EquationTree, count: int = 0, step: int = 2) -> None:
            if root.data:
                resource: Resource = root.data
                message = " " * count + str(resource)
                if root.station:
                    message += " [%s]" % root.station
                output.append(message)

            for i, node in enumerate(root.children):
                # Separate root elements from user input.
                # Because they form different tree stuctures.
                if i > 0 and not root.data:
                    output.append(separator)

                # Do not increase indendation on empty root.
                # Root node artificially connects user input.
                if root.data:
                    traverse(node, count + step)
                else:
                    traverse(node, count)

        output.append(separator.replace("-", "="))
        output.append("RECURSIVE DATA STRUCTURE")
        output.append(separator.replace("-", "="))

        traverse(root)

        return output

    def process(self, user_input: str) -> list[str]:
        equation: Equation = self.parse_input(user_input)
        equation = self.preprocessor.process(equation)
        output: list[str] = self.algorithm.calculate(equation)
        return output

    def main(self):
        user_input: str = ""
        while True:
            try:
                user_input = self.ask_input()
                output: list[str] = self.process(user_input)
            except SystemExit:
                break
            except KeyboardInterrupt:
                break
            except SyntaxError as err:
                print(str(err))
                output = self.help()
            except ValueError as err:
                print(str(err))
                output = self.recover(user_input)

            for line in output:
                print(line)

    def init(self, argv: list[str]) -> None:
        try:
            # Parse command line arguments.
            opts, args = getopt.getopt(
                argv[1:], "girjh", ["gnu", "implicit", "recursive", "json", "help"]
            )

            for argument in args:
                # Application class should create a file reader.
                # Because is given as a command line argument.

                # Read from a json file.
                if argument.endswith(".json"):
                    filesystem: FileSystem = JsonSystem(argument)
                    filesystem.read(self.calculator)

                # Read from a text file by default.
                else:
                    filesystem = FileSystem(argument)
                    filesystem.read(self.calculator)

            # Configure program based on options.
            for opt, arg in opts:

                # Apply GNU readline functionality.
                if opt in ("-g", "--gnu"):
                    variables = self.calculator.get_keywords()
                    Completer(variables)

                # Configure application's output.
                if opt in ("-r", "--recursive"):
                    algorithm: Algorithm = Recursive(self)
                    self.algorithm = algorithm

                if opt in ("-j", "--json"):
                    algorithm = RecursiveJson(self)
                    self.algorithm = algorithm

                # Include all necessary workstations
                if opt in ("-i", "--implicit"):
                    preprocessor = Implicit(self)
                    self.preprocessor = preprocessor

                # Print user manual and exit.
                if opt in ("-h", "--help"):
                    self.manual(argv[0])

        except getopt.GetoptError as err:
            print(str(err))
        except FileNotFoundError as err:
            print(str(err).replace("[Errno 2] ", ""))
        except SyntaxError as err:
            print(str(err))


class Algorithm(ABC):
    def __init__(self, application: Application):
        self.application = application

    @abstractmethod
    def calculate(self, equation: Equation) -> list[str]:
        pass


class Iterative(Algorithm):
    def calculate(self, equation: Equation) -> list[str]:
        equations = list(self.application.calculator.calculate(equation))
        output = self.application.print_output(equations[:-1][::-1])
        output += self.application.print_total_resources(equations[-1], equation)
        return output


class Recursive(Algorithm):
    def calculate(self, equation: Equation) -> list[str]:
        total = deque(self.application.calculator.calculate(equation), maxlen=1).pop()
        equation_tree = self.application.calculator.calculate_recursive(equation)
        output = self.application.print_output_recursive(equation_tree)
        output += self.application.print_total_resources(total, equation)
        return output


class RecursiveJson(Algorithm):
    def calculate(self, equation: Equation) -> list[str]:
        equation_tree = self.application.calculator.calculate_recursive(equation)
        dictionaries = self.application.calculator.convert_to_dictionaries(
            equation_tree
        )
        output = json.dumps(dictionaries, indent=2).strip().split("\n")
        return output


class Preprocessor(ABC):
    def __init__(self, application: Application):
        self.application = application

    @abstractmethod
    def process(self, equation: Equation) -> Equation:
        pass


class Explicit(Preprocessor):
    def process(self, equation: Equation) -> Equation:
        """
        Calculator knows all the recipes, but cannot inquire an user.
        Therefore it's necessary to use callback function as a parameter.
        """

        self.application.calculator.resolve_recipes(
            equation, callback=self.application.ask_optional
        )
        return equation


class Implicit(Preprocessor):
    def process(self, equation: Equation) -> Equation:
        """Calculator extends input when deemed necessary."""

        self.application.calculator.resolve_recipes_implicit(
            equation, callback=self.application.ask_optional
        )
        return self.application.calculator.find_workstations(equation)


if __name__ == "__main__":
    # Start text-based user interface.
    application = Application()
    application.init(sys.argv)
    application.help()
    application.main()
