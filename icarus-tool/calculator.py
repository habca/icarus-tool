from fractions import Fraction
import difflib
import string
import utils
import math
import re

class Calculator:

    def __init__(self):
        self.resources = dict()

    def get_keywords(self):
        return self.resources.keys()

    def syntax_check(self, equation: str) -> None:
        num = "[1-9]+[0-9]*"
        var = "[a-z/]+([-_][a-z/]+)*"
        pattern1 = f"{num} {var}( \+ {num} {var})*"
        pattern2 = f"{num} {var} = {num} {var}( \+ {num} {var})*"
        
        if not re.fullmatch(pattern1, equation):
            if not re.fullmatch(pattern2, equation):
                raise SyntaxError(f"SyntaxError: {equation}")

    def value_check(self, equation: str) -> None:
        # Skip assignments.
        if "=" in equation:
            return

        pattern = "[a-z/]+(?:[-_][a-z/]+)*"
        variables = re.findall(pattern, equation)
        for variable in variables:
            if variable not in self.resources:
                raise ValueError(f"ValueError: {variable}")
    
    def check_equation(self, equation: str) -> dict[str]:
        similar_words = dict()
        for variable in equation.split():
            if variable.isdigit():
                continue
            if variable in string.punctuation:
                continue
            words = self.spell_check(variable)
            if words == []:
                continue
            similar_words[variable] = words
        return similar_words

    def spell_check(self, variable: str) -> list[str]:
        if variable not in self.resources:
            return difflib.get_close_matches(variable, self.resources)
        return []

    def assign_equation(self, equation: str) -> str:
        """
        Selvittää materiaalien määrän suhteessa resurssiin.
        equation: "100 steel_screw = 1 steel_ingot"
        return: "1 steel_screw = 1/100 ( 1 steel_ingot )")
        """

        amount, equation = utils.extract(equation)
        name, equation = utils.extract(equation)
        _, equation = utils.extract(equation)

        if name in self.resources:
            # Variable name can be assigned just once.
            raise ValueError("Variable name is assigned.")

        multiplier = Fraction(1, int(amount))
        self.resources[name] = f"{multiplier} ( {equation} )"

    def calculate(self, equation: str) -> str:
        while True:
            previous = equation
            equation = self.replace_variables(equation)
            equation = Calculator.multiply(equation, Fraction(1))
            equation = Calculator.subtract(equation)
            if equation == previous:
                break
        return equation

    def search_variable(self, variable: str, equation: str, not_first = False) -> list:
        """
        Palauttaa listan epäsuorista viittauksista muuttujaan.
        variable: "iron_ingot"
        equation: "12 wood + 8 leather + 40 titanium_ingot + 4 epoxy + 16 steel_screw"
        return: ["steel_screw"]
        """
        
        variables = []
        for part in equation.split():
            if part == variable and not_first:
                variables.append(part)
            if part in self.resources:
                expression = self.resources[part]
                found = self.search_variable(variable, expression, True)
                if found != []:
                    variables.append(part)
        return variables

    def replace_variables(self, equation: str) -> str:
        """ Korvaa muuttujan sitä vastaavalla lausekkeella. """

        for resource in equation.split():
            temp = equation.replace(resource, "")
            found = self.search_variable(resource, temp)
            if found == [] and resource in self.resources:
                expression = self.resources[resource]
                equation = equation.replace(resource, expression)
        return equation

    @classmethod
    def multiply(cls, equation: str, multiplier: Fraction) -> str:
        frac = multiplier
        sb = ""
        while equation != "":
            word, equation = utils.extract(equation)

            if word.isdigit() or "/" in word:
                # Next word is an integer number.
                frac *= Fraction(word)
                continue

            if word == "(":
                start, equation = Calculator.multiply(equation, frac)
                sb += " " + start
                frac = multiplier
                continue

            if word == ")":
                return sb, equation

            if word == "+":
                sb += " " + word
                continue
                
            # Next word is the name of a variable.
            sb += f" {frac} {word}"
            frac = multiplier
        return sb.lstrip()

    @classmethod
    def subtract(cls, equation: str) -> str:
        amount, equation = utils.extract(equation)
        name, equation = utils.extract(equation)

        variables = { name: Fraction(amount) }

        while equation != "":
            operator, equation = utils.extract(equation)
            amount, equation = utils.extract(equation)
            name, equation = utils.extract(equation)

            frac = Fraction(amount)
            if operator == "-":
                frac = -frac
            
            if name in variables:
                variables[name] += frac
                continue

            variables[name] = frac

        sb = ""
        for name, amount in variables.items():
            amount = math.ceil(amount)
            sb += f" + {amount} {name}"
        sb = sb.removeprefix(" + ")
        return sb

    def print_first_layer(self, equation: str) -> list[str]:
        resource_list = []
        for parts in equation.split(" + "):
            amount, name = parts.split()
            if name in self.resources:
                resource = f"{amount} {self.resources[name]}"
                resource = Calculator.multiply(resource, Fraction(1))
                resource = Calculator.subtract(resource)
                for res in resource.split(" + "):
                    resource_list.append(res)
        equation = " + ".join(resource_list)
        equation = Calculator.subtract(equation)
        resource_list = equation.split(" + ")
        resource_list = Calculator.sort_resources(resource_list)
        resource_list = Calculator.format_resources(resource_list)
        return "\n".join(resource_list)

    def print_last_layer(self, expression: str) -> list[str]:
        resource_list = []

        for resource in expression.split(" + "):
            resource_list.append(resource)
        resource_list = Calculator.sort_resources(resource_list)
        resource_list = Calculator.format_resources(resource_list)
        return "\n".join(resource_list)

    @classmethod
    def sort_resources(cls, resources: list[str]) -> list[str]:
        """ Sort resources by the amount and then by the name. """

        resources = sorted(resources, key=get_name, reverse=False)
        resources = sorted(resources, key=get_amount, reverse=True)
        return resources

    @classmethod
    def format_resources(cls, resources: list[str]) -> int:
        margin = max([len(str(get_amount(res))) for res in resources])
        resource_list = []
        for resource in resources:
            amount, name = get_amount(resource), get_name(resource)
            resource_text = f"{amount:{margin}d} {name}"
            resource_list.append(resource_text)
        return resource_list

def get_amount(resource: str) -> int:
    return int(utils.extract(resource)[0])

def get_name(resource: str) -> str:
    return utils.extract(resource, reverse=True)[0]

def get_both(resource: str) -> tuple:
    return tuple(resource.split())
