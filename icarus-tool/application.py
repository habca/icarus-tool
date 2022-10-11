from collections import deque
from typing import Any
from calculator import Calculator, Equation, EquationTree, Resource
from abc import ABC, abstractmethod
import sys, getopt
import json


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
                calculator.errors.append(line)

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

        self.user_input: str = None

    def help(self):
        print()  # Empty line to make welcome text readable.
        print(":: Usage: amount name [+ amount name] [- amount name]")

    def ask_input(self) -> str:
        """Throws SyntaxError, ValueError or SystemExit!"""

        # Line break for a readable terminal output.
        print()

        # Replace whitespace sequences with a spacebar.
        equation = " ".join(input("> ").split())

        # Terminates the program by raising a SystemExit.
        if equation in ("exit", "quit"):
            raise SystemExit

        # Return a valid equation.
        return equation

    def parse_input(self, equation: str) -> Equation:
        # Validate an equation before processing any further.
        self.calculator.validator.validate_syntax_calculation(equation)

        equation_obj: Equation = Equation.parse(equation)

        # Ensure there are only pre-assigned variable names.
        self.calculator.validator.validate_value_calculation(equation_obj)

        self.user_input = equation

        return equation_obj

    def recover(self, equation: str) -> None:
        resources = Equation.parse(equation)
        similar_words = self.calculator.find_similar(resources)
        if similar_words != {}:
            print()  # Line break for a readable terminal output.
            print(f":: Did you mean?")
            for name, word_list in similar_words.items():
                message = "- " + name + ": " + ", ".join(word_list)
                print(message)

    def resolve_recipes(self, equation: Equation) -> None:
        # Callback function to request user interaction.
        def ask_optional(options: list[str]) -> int:
            for i, option in enumerate(options):
                print(f"({i}) {option}")

            while True:
                choice = input(":: Which recipe would you like to use? ")
                print()  # Empty line to make welcome text readable.

                if choice in ("exit", "quit"):
                    raise SystemExit

                if choice.isdigit() and 0 <= int(choice) < len(options):
                    return int(choice)

        # Calculator knows all the recipes, but cannot inquire an user.
        # Therefore it's necessary to use callback function as a parameter.
        self.calculator.resolve_recipes(equation, callback=ask_optional)

    def print_output(self, equations: list[Equation]) -> None:
        # To make program's output more readable.
        separator = "-" * (len(self.user_input) + 2)

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
            # Otherwise, separate equations from each other.
            current_station = self.calculator.get_station(resources)
            if current_station != previous_station:
                print(separator.replace("-", "="))
                print(current_station.replace("_", " ").upper())
                print(separator.replace("-", "="))
            else:
                print(separator.replace("-", "="))

            # Update current station.
            previous_station = current_station

            # Print recipes above the separator.
            for resource_name in resources_str:
                print(resource_name)

            # Separate recipes and resources by the separator.
            print(separator)

            # Pick resources craftable in the current station only.
            resources = self.calculator.resources_per_station(equations[i])
            resources = resources.suodata(all=False, round=False)
            resources = resources.sort_resources()
            resources_str = resources.format_resources()

            # Print resources below the separator.
            for resource_name in resources_str:
                print(resource_name)

    def print_total_resources(self, equation: Equation) -> None:
        # To make program's output more readable.
        separator = "-" * (len(self.user_input) + 2)

        """
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
        resources = Equation.parse(self.user_input)
        resources = resources.suodata(all=True, round=False)
        resources = resources.sort_resources()
        resources_str = resources.format_resources()

        # There may be multiple crafting stations.
        print(separator.replace("-", "="))
        print("TOTAL RESOURCES")
        print(separator.replace("-", "="))

        # Print sorted and formated user input.
        for resource_name in resources_str:
            print(resource_name)

        # Separate crafting recipes and material costs.
        print(separator)

        # From here, print the program's output.
        resources = equation.suodata(all=True, round=True)
        resources = resources.sort_resources()
        resources_str = resources.format_resources()

        # Print sorted and formated program output.
        for resource_name in resources_str:
            print(resource_name)

    def print_output_recursive(self, root: EquationTree) -> None:

        # To make program's output more readable.
        separator = "-" * (len(self.user_input) + 2)

        def traverse(root: EquationTree, count: int = 0, step: int = 2) -> None:
            if root.data:
                resource: Resource = root.data
                message = " " * count + str(resource)
                if root.station:
                    message += " [%s]" % root.station
                print(message)

            for i, node in enumerate(root.children):
                # Separate root elements from user input.
                # Because they form different tree stuctures.
                if i > 0 and not root.data:
                    print(separator)

                # Do not increase indendation on empty root.
                # Root node artificially connects user input.
                if root.data:
                    traverse(node, count + step)
                else:
                    traverse(node, count)

        print()

        print(separator.replace("-", "="))
        print("RECURSIVE DATA STRUCTURE")
        print(separator.replace("-", "="))

        traverse(root)

    def main(self):
        while True:
            try:
                user_input = self.ask_input()
                equation = self.parse_input(user_input)
                self.resolve_recipes(equation)
                self.algorithm.calculate(equation)
            except SystemExit:
                break
            except KeyboardInterrupt:
                break
            except SyntaxError as err:
                print(str(err))
                self.help()
            except ValueError as err:
                print(str(err))
                self.recover(user_input)

    def init(self, argv: list[str]) -> None:
        try:
            # Parse command line arguments.
            opts, args = getopt.getopt(argv[1:], "gr", ["gnu", "recursive"])

            if args == []:
                raise SyntaxError()

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

                if opt in ("-r", "--recursive"):
                    algorithm = Recursive(self)
                    self.algorithm = algorithm

        except getopt.GetoptError as err:
            print(str(err))
        except FileNotFoundError as err:
            print(str(err).replace("[Errno 2] ", ""))
        except SyntaxError:
            print("Usage:", argv[0], "-g", "data/tech_tree.txt")


class Algorithm(ABC):
    def __init__(self, application: Application):
        self.application = application

    @abstractmethod
    def calculate(self, equation: Equation) -> None:
        pass


class Iterative(Algorithm):
    def calculate(self, equation: Equation) -> None:
        equations = list(self.application.calculator.calculate(equation))
        self.application.print_output(equations[:-1])
        self.application.print_total_resources(equations[-1])


class Recursive(Algorithm):
    def calculate(self, equation: Equation) -> None:
        total = deque(self.application.calculator.calculate(equation), maxlen=1).pop()
        equation_tree = self.application.calculator.calculate_recursive(equation)
        self.application.print_output_recursive(equation_tree)
        self.application.print_total_resources(total)


if __name__ == "__main__":
    # Start text-based user interface.
    application = Application()
    application.init(sys.argv)
    application.help()
    application.main()
