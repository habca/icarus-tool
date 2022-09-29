from calculator import Calculator, Equation
import sys, getopt


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

    def help(self):
        print()  # Empty line to make welcome text readable.
        print(welcome := "Welcome to Icarus tool!")
        print("-" * len(welcome))
        print("amount name [+ amount name] [- amount name]")

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

    def calculate(self, equation_str: str) -> None:
        # To make program's output more readable.
        separator = "-" * (len(equation_str) + 2)

        # Validate an equation before processing any further.
        self.calculator.validator.validate_syntax_calculation(equation_str)

        equation = Equation.parse(equation_str)

        # Ensure there are only pre-assigned variable names.
        self.calculator.validator.validate_value_calculation(equation)

        # List of derivative equations explaining materials step by step.
        equations: list[Equation] = self.calculator.calculate(equation)

        previous_station = None
        for i in range(len(equations) - 1):

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
        resources = Equation.parse(equation_str)
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
        resources = equations[-1].make_copy()
        resources = resources.suodata(all=True, round=True)
        resources = resources.sort_resources()
        resources_str = resources.format_resources()

        # Print sorted and formated program output.
        for resource_name in resources_str:
            print(resource_name)

    def recover(self, equation: str) -> None:
        resources = Equation.parse(equation)
        similar_words = self.calculator.find_similar(resources)
        if similar_words != {}:
            # Line break for a readable terminal output.
            print()

            print(f"Did you mean?")
            for name, word_list in similar_words.items():
                print("- " + name + ": " + ", ".join(word_list))

    def main(self):
        while True:
            try:
                equation = self.ask_input()
                self.calculate(equation)
            except SyntaxError as err:
                print(str(err))
            except ValueError as err:
                print(str(err))
                self.recover(equation)
            except SystemExit:
                break
            except KeyboardInterrupt:
                break

    def init(self, argv: list[str]) -> None:
        try:
            # Parse command line arguments.
            opts, args = getopt.getopt(argv[1:], "g", ["gnu"])

            if args == []:
                raise ArgumentError

            # Import equations from files.
            for argument in args:
                file_system = FileSystem(argument)
                file_system.read(self.calculator)

            # Configure program based on options.
            for opt, arg in opts:

                # Apply GNU readline functionality.
                if opt in ("-g", "--gnu"):
                    variables = self.calculator.get_keywords()
                    Completer(variables)

        except getopt.GetoptError as err:
            print(str(err))
        except FileNotFoundError as err:
            print(str(err).replace("[Errno 2] ", ""))
        except ArgumentError:
            print("Usage:", argv[0], "-g", "data/tech_tree.txt")


class ArgumentError(Exception):
    """Custom error type to validate an argument string."""

    def __init__(self):
        super().__init__()


if __name__ == "__main__":
    # Start text-based user interface.
    application = Application()
    application.init(sys.argv)
    application.help()
    application.main()
