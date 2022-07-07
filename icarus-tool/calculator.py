from fractions import Fraction
import difflib
import math
import re

class Resource:
    def __init__(self, amount: Fraction, name: str):
        self.amount = amount
        self.name = name

    def __eq__(self, other: "Resource") -> bool:
        return (self.amount, self.name) == (other.amount, other.name)

    def __str__(self) -> str:
        return f"{self.amount} {self.name}"

    @classmethod
    def parse(cls, resource: str) -> "Resource":
        amount, name = resource.split(" ")
        return Resource(Fraction(amount), name)

class Equation:
    def __init__(self, resources: list[Resource]):
        self.resources = resources

    def __eq__(self, other: "Equation") -> bool:
        return self.resources == other.resources

    def __iter__(self) -> iter:
        return iter(self.resources)

    def __str__(self) -> str:
        return " + ".join([str(resource) for resource in self.resources])

    @classmethod
    def parse(cls, equation: str) -> "Equation":
        resources = [Resource.parse(r) for r in equation.split(" + ")]
        return Equation(resources)

    def multiply(self, fraction: Fraction) -> "Equation":
        resources = [Resource(fraction * r.amount, r.name) for r in self.resources]
        return Equation(resources)

    def evaluate(self) -> "Equation":
        variables: dict[str, Resource] = dict()

        for resource in self.resources:
            if resource.name not in variables.keys():
                variables[resource.name] = resource
            else:
                variables[resource.name].amount += resource.amount

        for name, resource in variables.items():
            variables[name].amount = math.ceil(resource.amount)

        resources = [variables[name] for name in variables.keys()]
        return Equation(resources)

    def sort_resources(self) -> "Equation":
        """ Sort resources by the amount and then by the name. """
        resources = self.resources
        resources = sorted(resources, key=lambda x: x.name, reverse=False)
        resources = sorted(resources, key=lambda x: x.amount, reverse=True)
        return Equation(resources)

    def format_resources(self) -> list[str]:
        """ Returns a sorted list of resources as a formated strings. """
        if self.resources == []:
            return []

        margin = max([len(str(r.amount)) for r in self.resources])
        
        def format_resource(resource: Resource) -> str:
            return f"{resource.amount:{margin}d} {resource.name}"

        return [format_resource(r) for r in self.sort_resources()]

class Calculator:
    def __init__(self):
        self.resources: dict[str, Equation] = dict()
        self.variables: list[str] = list()
        self.validator: Validator = Validator(self)

    def assign_equation(self, assignment: str) -> None:
        # Validate an assignment before processing any further.
        self.validator.validate_syntax_assignment(assignment)
        
        # Separate an assignment into a Resource and an Equation.
        left, right = assignment.split(" = ")

        resource = Resource.parse(left)
        equation = Equation.parse(right)
        equation = equation.multiply(Fraction(1, resource.amount))

        # Variable name can be assigned just once.
        self.validator.validate_value_assignment(resource)

        self.resources[resource.name] = equation

        # Resource will be removed from the variables list when it's assigned.
        self.variables = [var for var in self.variables if var != resource.name]

        # Add new variables into the unassigned variables list.
        for resource in equation.resources:
            if resource.name not in self.resources:
                if resource.name not in self.variables:
                    self.variables.append(resource.name)

    def get_keywords(self) -> list[str]:
        return list(self.resources.keys())

    def calculate(self, equation: str) -> list[Equation]:
        # Validate an equation before processing any further.
        self.validator.validate_syntax_calculation(equation)

        equation = Equation.parse(equation)

        # Ensure there are only pre-assigned variable names.
        self.validator.validate_value_calculation(equation)

        equations = [equation]
        while True:
            equation = self.replace_variables(equation)
            equation = equation.evaluate()
            equations.append(equation)
            
            # Equation did not change so it is ready.
            if [r for r in equation if r.name in self.resources] == []:
                break

        return equations

    def replace_variables(self, equation: Equation) -> Equation:
        new_resources = []
        for resource in equation:
            temp = [r for r in equation if r.name != resource.name]
            found = self.search_variable(resource.name, temp)
            if found == [] and resource.name in self.resources:
                expression = self.resources[resource.name]
                expression = expression.multiply(resource.amount)
                new_resources += expression.resources
            else:
                new_resources.append(resource)
        return Equation(new_resources)

    def search_variable(self, variable: str, equation: Equation, not_first: bool = False) -> list[str]:
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

    def find_similar(self, equation: Equation) -> dict[str]:
        word_list = self.get_keywords()
        similar_words = dict()
        for resource in equation:
            words = difflib.get_close_matches(resource.name, word_list)
            if words != [] and resource.name not in self.resources:
                similar_words[resource.name] = words
        return similar_words

class Validator:
    pattern_num = "[1-9]+[0-9]*(?:/[1-9]+[0-9]*)*"
    pattern_var = "(?:[0-9]+[-_])*[a-z/]+(?:[-_][a-z/]+)*"

    def __init__(self, calc: Calculator):
        self.calc = calc

    def validate_syntax_assignment(self, assignment: str) -> None:
        num = Validator.pattern_num
        var = Validator.pattern_var
        
        pattern = re.compile(f"{num} {var} = {num} {var}( \+ {num} {var})*")
        if not pattern.fullmatch(assignment):
            raise SyntaxError("SyntaxError: " + assignment)

    def validate_syntax_calculation(self, equation: str) -> None:
        num = Validator.pattern_num
        var = Validator.pattern_var
        
        pattern = re.compile(f"{num} {var}( \+ {num} {var})*")
        if not pattern.fullmatch(equation):
            raise SyntaxError("SyntaxError: " + equation)

    def validate_value_assignment(self, resource: Resource) -> None:
        if resource.name in self.calc.resources:
            raise ValueError(f"Name is already in use: {resource.name}")

    def validate_value_calculation(self, equation: Equation) -> None:
        errors: list[str] = []
        for resource in equation:
            if resource.name not in self.calc.resources:
                if resource.name not in self.calc.variables:
                    errors.append(resource.name) 
        if errors != []:
            error: str = ", ".join(errors)
            raise ValueError("ValueError: " + error)
