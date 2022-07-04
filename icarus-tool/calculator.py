from fractions import Fraction
import difflib
import fractions
import math
import re

class Resource:
    def __init__(self, amount: Fraction, name: str):
        self.amount = amount
        self.name = name

    # TODO toteuta vertailu jarjestamiseen
    def get_amount(self) -> Fraction:
        return self.amount

    def get_name(self) -> str:
        return self.name

    def __str__(self) -> str:
        return f"{self.amount} {self.name}"

class Equation:
    pattern_num = "[1-9]+[0-9]*(?:/[1-9]+[0-9]*)*"
    pattern_var = "(?:[0-9]+[-_])*[a-z/]+(?:[-_][a-z/]+)*"

    def __init__(self, left_hand: Resource, resources: list[Resource]):
        self.left_hand = left_hand
        self.resources = resources

    @classmethod
    def parse(cls, equation: str) -> "Equation":
        num = Equation.pattern_num
        var = Equation.pattern_var

        # Validate an equation before processing any further.
        pattern = re.compile(f"{num} {var} = {num} {var}( \+ {num} {var})*")
        if not pattern.fullmatch(equation):
            raise SyntaxError("SyntaxError: " + equation)

        iterator = iter(equation.split())
        amount = next(iterator)
        name = next(iterator)

        left_hand = Resource(1, name)
        multiplier = Fraction(1, Fraction(amount))
        resources = []

        # Operators (=) and (+) can be discarded.
        for _ in iterator:
            amount = next(iterator)
            name = next(iterator)

            resource = Resource(multiplier * Fraction(amount), name)
            resources.append(resource)

        return Equation(left_hand, resources)

    @classmethod
    def parse_list(cls, equation: str) -> list["Equation"]:
        num = Equation.pattern_num
        var = Equation.pattern_var

        pattern = re.compile(f"{num} {var}( \+ {num} {var})*")
        if not pattern.fullmatch(equation):
            raise SyntaxError(f"SyntaxError: {equation}")

        iterator = iter(equation.split())
        amount = next(iterator)
        name = next(iterator)

        resource = Resource(Fraction(amount), name)
        resources = [resource]

        for _ in iterator:
            amount = next(iterator)
            name = next(iterator)

            resource = Resource(Fraction(amount), name)
            resources.append(resource)

        return resources
    
    def __str__(self) -> str:
        left_hand = str(self.left_hand)
        resources = " + ".join(map(str, self.resources))
        return f"{left_hand} = {resources}"
    
    def __iter__(self):
        """ Palauttaa iteraattori puurakenteen lapikayntiin. """
        raise NotImplementedError("TODO")

    def __next__(self):
        """ TODO siirra omaan luokkaan, kun valmis muuten. """
        raise NotImplementedError("TODO")

class Calculator:
    def __init__(self):
        self.resources: dict[str, Equation] = dict()
        self.variables: list[str] = list()
    
    # TODO poista ellei tarvita
    def get_keywords(self) -> list[str]:
        return list(self.resources.keys())

    def assign_equation(self, assignment: str) -> None:
        equation = Equation.parse(assignment)
        name = equation.left_hand.name

        # Variable name can be assigned just once.
        if name in self.resources:
            raise ValueError(f"Name is already in use: {name}")

        # Variables will be removed when re-assigned.
        if name in self.variables:
            self.variables.remove(name)

        # Add new variables into the unassigned variables list.
        for resource in equation.resources:
            variable = resource.name
            if variable not in self.resources:
                if variable not in self.variables:
                    self.variables.append(variable)
        
        self.resources[name] = equation

    # TODO: siirra Equation-luokkaan.
    def replace_variables(self, resources: list[Resource]) -> list[Resource]:
        new_resources = []
        # TODO tupleina resurssien purkaminen helpottuu.
        for resource in resources:
            new_resources.append(resource)
            temp = [r for r in resources if r.name != resource.name]
            found = self.search_variable(resource.name, temp)
            if found == [] and resource.name in self.resources.keys():
                expression = self.resources[resource.name].resources
                for i, res in enumerate(expression):
                    expression[i] = Resource(resource.amount * res.amount, res.name)
                new_resources[-1:] = expression
        return new_resources

    def search_variable(self, variable: str, equation: list[Resource], not_first: bool = False) -> list[str]:
        variables = []
        for part in equation:
            if part.name == variable and not_first:
                variables.append(part.name)
            if part.name in self.resources.keys():
                expression = self.resources[part.name].resources
                found = self.search_variable(variable, expression, True)
                if found != []:
                    variables.append(part.name)
        return variables

    def calculate(self, equation: str) -> list[Equation]:
        resources = Equation.parse_list(equation)

        # Ensure there are only pre-assigned variable names.
        tmp = [str(r.name) for r in resources if r.name not in self.resources]
        if tmp != []:
            raise ValueError(f"ValueError: {', '.join(tmp)}")

        equations = []
        while True:
            equations.append(str(resources))
            resources = self.replace_variables(resources)
            resources = Calculator.subtract(resources)
            
            # Equation did not change so it is ready.
            if [r for r in resources if r.name in self.resources] == []:
                break

        return equations

    @classmethod
    def subtract(cls, equation: list[Resource]) -> list[Resource]:
        variables: dict[str, Resource] = dict()

        for resource in equation:
            if resource.name in variables.keys():
                variables[resource.name].amount += resource.amount
            else:
                variables[resource.name] = resource

        for name, resource in variables.items():
            variables[name].amount = math.ceil(resource.amount)

        return [variables[name] for name in variables.keys()]

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

    def find_similar(self, equation: str) -> dict[str]:
        similar_words = dict()
        pattern = re.compile(Calculator.pattern_var)
        for name in pattern.findall(equation):
            if name not in self.variables:
                words = difflib.get_close_matches(name, self.get_keywords())
                if words != []:
                    similar_words[name] = words
        return similar_words

# TODO poista kun ei tarvita
def get_amount(resource: str) -> int:
    return int(resource.split()[0])

def get_name(resource: str) -> str:
    return resource.split()[-1]
