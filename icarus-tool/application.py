from calculator import Calculator
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
                line = line.replace("\n", "")
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

    def ask_input(self) -> str:
        """ Throws SyntaxError, ValueError or SystemExit! """

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
        equation_list = self.calculator.calculate(equation)

        if equation_list == []:
            raise ValueError("Error occured: " + equation)
        
        for i in range(1, len(equation_list)):
            previous = equation_list[i - 1].split(" + ")
            current = equation_list[i].split(" + ")

            # TODO bottom-up: ensin luetellaan raaka-aineet, sitten rakennetaan.
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
        similar_words = self.calculator.find_similar(equation)
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
                self.quess(equation)
            except SystemExit:
                break

def main(argv: list[str]) -> None:
    # Create data structures.
    calculator = Calculator()
    application = Application(calculator)

    try:
        # Parse command line arguments.
        opts, args = getopt.getopt(argv[1:], "gi:", ["gnu", "file="])

        # Configure program based on the arguments.
        for opt, arg in opts:

            # Apply GNU readline functionality.
            if opt in ("-g", "--gnu"):
                variables = calculator.get_keywords()
                Completer(variables)

            # Import equations from a file.
            if opt in ("-i", "--file"):
                file_system = FileSystem(arg)
                file_system.read(calculator)
        
        if args != []:
            # User may drag-n-drop text files over script.
            file_system = FileSystem(args[0])
            file_system.read(calculator)
            
            # In that case, use tab completion by default.
            variables = calculator.get_keywords()
            Completer(variables)

        # Start text-based user interface.
        application.help()
        application.main()

    except getopt.GetoptError:
        print("Usage:", argv[0], "<inputfile>")
    except FileNotFoundError:
        print("No such file:", arg)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main(sys.argv)
