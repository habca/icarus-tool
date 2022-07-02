from calculator import Calculator
import utils
import readline
import sys, getopt

class FileSystem:
    """ Read equations from file rather than user input. """

    def __init__(self, filename: str):
        self.filename = filename

    def read(self, calculator: Calculator) -> None:
        """
        Forwards assignment equations to the calculator.
        Function caller should handle FileNotFoundError!
        """

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
        """ Raise an exception for invalid input. """

        self.calculator.syntax_check(equation)
        self.calculator.value_check(equation)

    def calculate(self, equation: str) -> None:
        if "=" in equation:
            self.calculator.assign_equation(equation)
            return

        separator = "-" * (len(equation) + 2)
        equation_list = self.calculator.calculate(equation)

        if equation_list == []:
            raise ValueError("Error occured: " + equation)
        
        for i in range(1, len(equation_list)):
            previous = equation_list[i - 1].split(" + ")
            current = equation_list[i].split(" + ")

            resources = [r for r in current if r not in previous]
            resources = Calculator.sort_resources(resources)
            resources = Calculator.format_resources(resources)

            print(separator)
            for resource in resources:
                resources = Calculator.sort_resources(resources)
                resources = Calculator.format_resources(resources)
                print(resource)

        print()
        print("TOTAL RESOURCES")
        
        current = Calculator.sort_resources(current)
        current = Calculator.format_resources(current)

        print(separator)
        for resource in current:
            print(resource)

    def quess(self, equation: str) -> None:
        similar_words = self.calculator.check_equation(equation)
        if similar_words != {}:
            # Line break before suggestions.
            print()

            print(f"Did you mean?")
            for name, word_list in similar_words.items():
                print("- " + name + ": " + ", ".join(word_list))

    def main(self):
        while True:
            # Line break before calculations.
            print()

            # Listen and preprocess user input.
            equation = input("> ")
            _, equation = utils.extract(equation, sep="")

            # Exit application.
            if equation in ["exit", "quit"]:
                break

            try:
                # Validate and postprocess user input.
                self.validate_user_input(equation)
                self.calculate(equation)
            except SyntaxError as err:
                print(str(err))
            except ValueError as err:
                print(str(err))
                self.quess(equation)

if __name__ == "__main__":
    # Create data structures.
    calculator = Calculator()
    application = Application(calculator)

    try:
        # Parse command line arguments.
        opts, args = getopt.getopt(sys.argv[1:], "ghi:", ["gnu", "help", "file="])

        # Configure program based on the arguments.
        for opt, arg in opts:

            # Apply GNU readline functionality.
            if opt in ("-g", "--gnu"):    
                variables = calculator.get_keywords()
                Completer(variables)

            # Print manual at the beginning.
            if opt in ("-h", "--help"):
                application.help()

            # Import equations from a file.
            if opt in ("-i", "--file"):
                file_system = FileSystem(arg)
                file_system.read(calculator)

        # Start text-based user interface.
        application.main()

    except getopt.GetoptError as err:
        print("Usage:", sys.argv[0], '-i <inputfile> -gh')
    except FileNotFoundError as err:
        print("No such file:", arg)
    except KeyboardInterrupt as err:
        pass
