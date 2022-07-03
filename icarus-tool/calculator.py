from fractions import Fraction
import difflib
import string
import math
import re

class Calculator:
    pattern_num = "[1-9]+[0-9]*(?:/[1-9]+[0-9]*)*"
    pattern_var = "(?:[0-9]+[-_])*[a-z/]+(?:[-_][a-z/]+)*"

    def __init__(self):
        self.resources = dict()
        self.variables = list()
    
    def get_keywords(self) -> list:
        return list(self.resources.keys())

    def find_similar(self, equation: str) -> dict[str]:
        similar_words = dict()
        pattern = re.compile(Calculator.pattern_var)
        for name in pattern.findall(equation):
            if name not in self.variables:
                words = difflib.get_close_matches(name, self.get_keywords())
                if words != []:
                    similar_words[name] = words
        return similar_words

    def assign_equation(self, equation: str) -> tuple[str, str]:
        num = Calculator.pattern_num
        var = Calculator.pattern_var

        # Validate an equation before processing any further.
        pattern = re.compile(f"{num} {var} = {num} {var}( \+ {num} {var})*")
        if not pattern.fullmatch(equation):
            raise SyntaxError("SyntaxError: " + equation)

        iterator = iter(equation.split())
        amount = next(iterator)
        name = next(iterator)
        _ = next(iterator)

        # Variable name can be assigned just once.
        if name in self.resources:
            raise ValueError(f"Name is already in use: {name}")

        # Variables will be removed when re-assigned.
        if name in self.variables:
            self.variables.remove(name)

        equation = " ".join(iterator)
        multiplier = Fraction(1, int(amount))
        self.resources[name] = f"{multiplier} ( {equation} )"

        # Add new variables into the unassigned variables list.
        variables = re.findall(Calculator.pattern_var, equation)
        for variable in variables:
            if variable not in self.resources:
                if variable not in self.variables:
                    self.variables.append(variable)

    def calculate(self, equation: str) -> str:
        num = Calculator.pattern_num
        var = Calculator.pattern_var

        pattern = f"{num} {var}( \+ {num} {var})*"
        if not re.fullmatch(pattern, equation):
            raise SyntaxError(f"SyntaxError: {equation}")

        equations = []
        while True:
            equations.append(equation)
            equation = self.replace_variables(equation)
            iterator = iter(equation.split())
            equation = Calculator.multiply(iterator, Fraction(1))
            equation = Calculator.subtract(equation)
            
            # Equation did not change so it is ready.
            if equation == equations[-1]:
                # Ensure there are only pre-assigned variable names.
                variables = re.findall(Calculator.pattern_var, equation)
                for variable in variables:
                    if variable not in self.variables:
                        raise ValueError(f"ValueError: {variable}")
                break

        return equations

    def search_variable(self, variable: str, equation: str, not_first: bool = False) -> list[str]:
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
        new_equation = equation[:]
        for resource in equation.split():
            temp = equation.replace(resource, "")
            found = self.search_variable(resource, temp)
            if found == [] and resource in self.resources:
                expression = self.resources[resource]
                new_equation = new_equation.replace(resource, expression)
        return new_equation

    @classmethod
    def multiply(cls, iterator, multiplier: Fraction) -> str:
        """
        Iterator is a mutable object so it's shared between recursions.
        """
        fraction = multiplier
        equation = ""
        pattern = re.compile(Calculator.pattern_num)

        for word in iterator:
            if pattern.fullmatch(word):
                # Next word is an integer number.
                fraction *= Fraction(word)
                continue

            if word == "(":
                word = Calculator.multiply(iterator, fraction)
                equation += " " + word
                fraction = multiplier
                continue

            if word == ")":
                return equation

            if word == "+":
                equation += " " + word
                continue
                
            # Next word is the name of a variable.
            equation += f" {fraction} {word}"
            fraction = multiplier

        return equation.strip()

    @classmethod
    def subtract(cls, equation: str) -> str:
        iterator = iter(equation.split())
        amount = next(iterator)
        name = next(iterator)

        variables = {name: Fraction(amount)}

        for operator in iterator:
            amount = next(iterator)
            name = next(iterator)

            fraction = Fraction(amount)
            if operator == "-":
                fraction = -fraction
            
            if name in variables:
                variables[name] += fraction
                continue

            variables[name] = fraction

        equation = ""
        for name, amount in variables.items():
            amount = math.ceil(amount)
            equation += f" + {amount} {name}"
        return equation.removeprefix(" + ")

    @classmethod
    def sort_resources(cls, resources: list[str]) -> list[str]:
        """
        Sort resources by the amount and then by the name.
        """
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
    return int(resource.split()[0])

def get_name(resource: str) -> str:
    return resource.split()[-1]

# TODO tee resurssi-luokka
