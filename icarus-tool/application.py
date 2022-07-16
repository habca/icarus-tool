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
        print(welcome := "Welcome to use Icarus tool")
        print("-" * len(welcome))
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
        separator = "-" * (len(equation) + 2)
        equations = self.calculator.calculate(equation)

        previous_station = None
        for i in range(len(equations)):
            resources = equations[i]
            resources = resources.sort_resources()
            resource_names = resources.format_resources()

            current_station = self.calculator.get_station(resources)
            if current_station != previous_station:
                previous_station = current_station

                print(separator.replace("-", "="))
                print(current_station.replace("_", " ").upper())
                print(separator.replace("-", "="))
            else:
                print(separator.replace("-", "="))

            for resource_name in resource_names:
                print(resource_name)

            resources = self.calculator.resources_per_station(equations[i])
            resources = resources.sort_resources()
            resource_names = resources.format_resources()

            if equations[i] != equations[-1]:
                print(separator)
                for resource_name in resource_names:
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
