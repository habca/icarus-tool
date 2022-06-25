from calculator import Calculator
import utils
import readline

class FileSystem:
    """ Read equations from file rather than user input. """

    def __init__(self, filename: str):
        self.filename = filename

    def read(self, calculator: Calculator) -> None:
        """ Forward equations to the calculator. """

        with open(self.filename) as file:
            for line in file:
                _, line = utils.extract(line, sep="")
                # Skip comments and empty lines.
                if not (line == "" or line.startswith("#")):
                    calculator.assign_equation(line)

class Completer:

    def __init__(self, keywords: list[str]):
        self.keywords = sorted(keywords)
        readline.parse_and_bind("tab: complete")
        readline.set_completer(self.auto_complete)

    def auto_complete(self, text: str, state: int):
        options = [var for var in self.keywords if var.startswith(text)]
        if state < len(options):
            return options[state]
        else:
            return None

class Application:

    def __init__(self, calculator: Calculator = None):
        self.calculator = calculator

        if self.calculator is None:
            self.calculator = Calculator()

    def help(self):
        print(welcome := "Welcome to use Icarus tool")
        print("-" * len(welcome))
        print("amount name = amount name [+ amount name]")
        print("amount name [+ amount name]")

    def validate_user_input(self, equation: str) -> None:
        """ Raise an exception for not valid input. """

        self.calculator.syntax_check(equation)
        self.calculator.value_check(equation)

    def assign(self, equation: str):
        self.calculator.assign_equation(equation)

    def calculate(self, equation: str):
        if "=" in equation:
            self.assign(equation)
            return

        expression = self.calculator.calculate(equation)
        first_layer = self.calculator.print_first_layer(equation)
        last_layer = self.calculator.print_last_layer(expression)

        separator = "-" * (len(equation) + 2)
        print(separator)
        print(first_layer)
        if first_layer != last_layer:
            print(separator)
            print(last_layer)

    def quess(self, equation: str) -> None:
        similar_words = self.calculator.check_equation(equation)
        if similar_words != {}:
            # Line break before suggestions.
            print()

            print(f"Did you mean?")
            for name, word_list in similar_words.items():
                print("- " + name + ": " + ", ".join(word_list))

    def main(self):
        self.help()
        while True:
            try:
                # Line break before calculations.
                print()

                # Listen and preprocess user input.
                equation = input("> ")
                _, equation = utils.extract(equation, sep="")

                # Exit application.
                if equation in ["exit", "quit"]:
                    break

                # Validate and postprocess user input.
                self.validate_user_input(equation)
                self.calculate(equation)

            except KeyboardInterrupt:
                break
            except SyntaxError as err:
                print(str(err))
            except ValueError as err:
                print(str(err))
                self.quess(equation)

if __name__ == "__main__":
    # Create data structures.
    calculator = Calculator()

    # Import equations from a file.
    file_system = FileSystem("tech_tree.txt")
    file_system.read(calculator)

    # Apply GNU readline functionality.
    variables = calculator.get_keywords()
    completer = Completer(variables)

    # Start text-based user interface.
    application = Application(calculator)
    application.main()
