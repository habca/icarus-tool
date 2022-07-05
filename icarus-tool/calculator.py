from fractions import Fraction
import difflib
import math
import re

class Resource:
    def __init__(self, amount: Fraction, name: str):
        self.amount = amount
        self.name = name

    def __str__(self) -> str:
        return f"{self.amount} {self.name}"

    @classmethod
    def parse(cls, resource: str) -> "Resource":
        amount, name = resource.split(" ")
        return Resource(Fraction(amount), name)

class Equation:
    def __init__(self, resources: list[Resource]):
        self.resources = resources

    def __str__(self) -> str:
        return " + ".join([str(resource) for resource in self.resources])

    @classmethod
    def parse(cls, equation: str) -> "Equation":
        resources = [Resource(resource) for resource in equation.split(" + ")]
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

class Calculator:
    def __init__(self):
        self.resources: dict[str, Equation] = dict()
        self.variables: list[str] = list()
        self.validator: Validator(self)
    
    def get_keywords(self) -> list[str]:
        return list(self.resources.keys())

    def assign_equation(self, assignment: str) -> None:
        # Validate an assignment before processing any further.
        self.validator.validate_syntax_assignment(assignment)
        
        # Separate an assignment into a Resource and an Equation.
        left, right = equation.split(" = ")

        resource = Resource.parse(left)
        equation = Equation.parse(right)
        equation = equation.multiply(Fraction(1, resource.amount))

        # Variable name can be assigned just once.
        self.validator.validate_value_assignment(resource)

        # Resource will be removed from the variables list when it's assigned.
        self.variables = [var for var in self.variables if var != resource.name]

        # Add new variables into the unassigned variables list.
        for resource in equation.resources:
            if resource.name not in self.resources:
                if resource.name not in self.variables:
                    self.variables.append(resource.name)
        
        self.resources[resource.name] = equation

    def calculate(self, equation: str) -> list[Equation]:
        # Validate an equation before processing any further.
        self.validator.validate_syntax_calculation(equation)

        equation = Equation.parse(equation)

        # Ensure there are only pre-assigned variable names.
        self.validator.validate_value_calculation(equation)

        equations = []
        while True:
            equations.append(equation)
            equation = self.replace_variables(equation)
            equation = Equation.subtract(equation)
            
            # Equation did not change so it is ready.
            if [r for r in equation if r.name in self.resources] == []:
                break

        return equations

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
        tmp = [str(r.name) for r in equation if r.name not in self.calc.resources]
        if tmp != []:
            raise ValueError(f"ValueError: {', '.join(tmp)}")
