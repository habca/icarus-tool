﻿from calculator import Calculator, Equation, Resource
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
        print(welcome := "Welcome to use Icarus tool")
        print("-" * len(welcome))
        print("amount name = amount name [+ amount name]")
        print("amount name [+ amount name]")

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

    def calculate(self, equation: str) -> None:
        if "=" in equation:
            self.calculator.assign_equation(equation)
            return

        separator = "-" * (len(equation) + 2)
        equations = self.calculator.calculate(equation)

        for i in range(len(equations)):
            previous = equations[i - 1]
            current = equations[i]

            resource_list: list[Resource] = [
                r for r in current if str(r) not in str(previous)
            ]
            resources = Equation(resource_list)
            resources = resources.sort_resources()
            resource_names: list[str] = resources.format_resources()

            print(separator)
            for resource_name in resource_names:
                print(resource_name)

        """
        print()
        print("TOTAL RESOURCES")

        current = current.sort_resources()
        current = current.format_resources()

        print(separator)
        for resource in current:
            print(resource)
        """

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
            print("Usage:", argv[0], "-g", "<inputfile>")


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
