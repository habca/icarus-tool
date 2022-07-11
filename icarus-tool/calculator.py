from fractions import Fraction
import difflib
import math
import re
from typing import Iterator


class Resource:
    def __init__(self, amount: Fraction, name: str):
        self.amount = amount
        self.name = name

    def __eq__(self, other: object) -> bool:
        result = False
        if isinstance(other, Resource):
            result = (self.amount, self.name) == (other.amount, other.name)
        return result

    def __str__(self) -> str:
        return f"{self.amount} {self.name}"

    @classmethod
    def parse(cls, resource: str) -> "Resource":
        amount, name = resource.split(" ")
        return Resource(Fraction(amount), name)


class Equation:
    def __init__(self, resources: list[Resource]):
        self.resources = resources

    def __eq__(self, other: object) -> bool:
        result = False
        if isinstance(other, Equation):
            result = self.resources == other.resources
        return result

    def __iter__(self) -> Iterator[Resource]:
        return iter(self.resources)

    def __str__(self) -> str:
        return " + ".join([str(resource) for resource in self.resources])

    def __repr__(self) -> str:
        # AssertionError: <calculator.Equation object at 0x7f685b1b3ee0> != <calculator.Equation object at 0x7f685b1cb1c0>
        # AssertionError: 60 fiber + 50 wood + 12 stone + 20 leather != 1 crafting_bench
        return str(self)

    def filter(self, resource: Resource) -> "Equation":
        resources = [r for r in self.resources if r != resource]
        return Equation(resources)

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
            fraction = Fraction(math.ceil(resource.amount))
            variables[name].amount = fraction

        resources = [variables[name] for name in variables.keys()]
        return Equation(resources)

    def sort_resources(self) -> "Equation":
        """Sort resources by the amount and then by the name."""
        resources = self.resources
        resources = sorted(resources, key=lambda x: x.name, reverse=False)
        resources = sorted(resources, key=lambda x: x.amount, reverse=True)
        return Equation(resources)

    def format_resources(self) -> list[str]:
        """Returns a sorted list of resources as a formated strings."""
        if self.resources == []:
            return []

        margin = max([len(str(r.amount)) for r in self.resources])

        def format_resource(resource: Resource) -> str:
            amount: int = int(resource.amount)
            return f"{amount:{margin}d} {resource.name}"

        return [format_resource(r) for r in self.sort_resources()]


class Calculator:
    def __init__(self):
        self.resources: dict[str, Equation] = dict()
        self.variables: list[str] = list()
        self.stations: dict[str, str] = dict()
        self.validator: Validator = Validator(self)

    def assign_equation(self, assignment: str) -> None:
        # Validate an assignment before processing any further.
        self.validator.validate_syntax_assignment(assignment)

        # Every craftable resource should have a crafting station.
        station, assignment = assignment.split(" : ")

        # Separate an assignment into a Resource and an Equation.
        left, right = assignment.split(" = ")

        resource = Resource.parse(left)
        equation = Equation.parse(right)
        equation = equation.multiply(Fraction(1, resource.amount))

        # Variable name can be assigned just once.
        self.validator.validate_value_assignment(resource)

        self.resources[resource.name] = equation
        self.stations[resource.name] = station

        # Resource will be removed from the variables list when it's assigned.
        self.variables = [var for var in self.variables if var != resource.name]

        # Add new variables into the unassigned variables list.
        for resource in equation.resources:
            if resource.name not in self.resources:
                if resource.name not in self.variables:
                    self.variables.append(resource.name)

    def get_keywords(self) -> list[str]:
        return list(self.resources.keys())

    def calculate(self, equation_str: str) -> list[Equation]:
        # Validate an equation before processing any further.
        self.validator.validate_syntax_calculation(equation_str)

        equation = Equation.parse(equation_str)

        # Ensure there are only pre-assigned variable names.
        self.validator.validate_value_calculation(equation)

        """
        equations = [equation]
        while True:
            equation = self.substitute_variables(equation)
            equation = equation.evaluate()
            equations.append(equation)

            # Equation did not change so it is ready.
            if [r for r in equation if r.name in self.resources] == []:
                break
        """

        # TODO sekava funktiokutsu
        grouped_resources, variables = self.group_by_station(equation, {}, Equation([]))
        ordered_stations = self.order_by_station(grouped_resources)
        equations = [grouped_resources[station] for station in ordered_stations]
        equations.append(variables)

        return equations

    def substitute_variables(self, equation: Equation) -> Equation:
        new_resources = []
        for resource in equation:
            temp: list[Resource] = [r for r in equation if r.name != resource.name]
            found: list[str] = self.search_variable(resource.name, Equation(temp))
            if found == [] and resource.name in self.resources:
                expression = self.resources[resource.name]
                expression = expression.multiply(resource.amount)
                new_resources += expression.resources
            else:
                new_resources.append(resource)
        return Equation(new_resources)

    def search_variable(
        self, variable: str, equation: Equation, not_first: bool = False
    ) -> list[str]:
        variables = []
        for part in equation:
            if part.name == variable and not_first:
                variables.append(part.name)
            if part.name in self.resources.keys():
                expression = self.resources[part.name].resources
                found: list[str] = self.search_variable(
                    variable, Equation(expression), True
                )
                if found != []:
                    variables.append(part.name)
        return variables

    def find_similar(self, equation: Equation) -> dict[str, list[str]]:
        word_list = self.get_keywords()
        similar_words: dict[str, list[str]] = dict()
        for resource in equation:
            words = difflib.get_close_matches(resource.name, word_list)
            if words != [] and resource.name not in self.resources:
                similar_words[resource.name] = words
        return similar_words

    def group_by_station(
        self, equation: Equation, groups: dict[str, Equation], total: Equation
    ) -> tuple[dict[str, Equation], Equation]:
        """Groups resources based on which station they are crafted in."""
        for resource in equation:
            if resource.name in self.variables:
                total.resources.append(resource)
                continue

            station = self.stations[resource.name]
            if station not in groups.keys():
                groups[station] = Equation([])

            groups[station].resources.append(resource)
            groups[station] = groups[station].evaluate()

            if resource.name in self.resources.keys():
                substituted = self.resources[resource.name]
                substituted = substituted.multiply(resource.amount)
                substituted = substituted.evaluate()
                groups, total = self.group_by_station(substituted, groups, total)

        # TODO tuplen kanssa ongelmia
        return groups, total.evaluate()

    def order_by_station(self, groups: dict[str, Equation]) -> list[str]:
        """Regroup resources based on which order they are crafted in."""
        new_groups: list[str] = []
        available_stations = list(groups.keys())
        while len(new_groups) < len(groups):
            for station in available_stations:
                equation: Equation = groups[station]
                equation = self.resources_per_station(equation)

                available = available_stations[:]
                available.remove(station)

                # TODO lippumuuttuja huono
                lippu = True
                for temp in available:
                    for resource in groups[temp]:
                        found = self.search_variable(resource.name, equation, True)
                        if found != []:
                            lippu = False

                if lippu:
                    new_groups.append(station)
                    available_stations.remove(station)

        return list(reversed(new_groups))

    def resources_per_station(self, equation: Equation) -> Equation:
        crafting_cost = Equation([])
        for resource in equation:
            for new_resource in self.resources[resource.name]:
                new_resource.amount *= resource.amount
                crafting_cost.resources.append(new_resource)
        return crafting_cost.evaluate()


class Validator:
    pattern_num = "[1-9]+[0-9]*(?:/[1-9]+[0-9]*)*"
    pattern_var = "(?:[0-9]+[-_])*[a-z/]+(?:[-_][a-z/]+)*"

    def __init__(self, calc: Calculator):
        self.calc = calc

    def validate_syntax_assignment(self, assignment: str) -> None:
        num = Validator.pattern_num
        var = Validator.pattern_var

        pattern = re.compile(f"{var} : {num} {var} = {num} {var}( \+ {num} {var})*")
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
