from fractions import Fraction
from typing import Iterator
import difflib
import math
import re


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

    def __repr__(self) -> str:
        return str(self)

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

    def make_copy(self) -> "Equation":
        resources = []
        for resource in self.resources:
            resources.append(Resource(resource.amount, resource.name))
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

    def calculate(self, equation: Equation) -> list[Equation]:
        # Never alter original equation.
        equation = equation.make_copy()

        equations = []
        while True:
            suodatettu = self.suodata(equation)
            equations.append(suodatettu)

            # Equation did not change so it is ready.
            valmis = [r for r in equation if r.name in self.resources]
            if valmis == []:
                break

            equation = self.korvaa(equation, suodatettu)
            equation = equation.evaluate()

        return equations

    def suodata(self, equation: Equation) -> Equation:
        """
        Returns equation with only highest tier resources in it.

        Example: 1 biofuel_extractor + 1 biofuel_generator -> 1 biofuel_generator
        Example: 1 cement_mixer + 1 concrete_furnace -> 1 concrete_furnace
        Example: 1 stone_furnace + 1 anvil_bench + 1 machining_bench -> 1 machining_bench
        Example: 1 anvil_bench + 1 machining_bench + 1 cement_mixer + 1 concrete_furnace + 1 fabricator -> 1 fabricator
        """

        equation = equation.make_copy()

        new_resources = []
        for resource in equation:
            temp = Equation([r for r in equation if r.name != resource.name])
            found: list[str] = self.search_variable(resource.name, temp)
            if found == [] and resource.name in self.resources:
                new_resources.append(resource)

        # All resources are raw materials.
        if new_resources == []:
            return equation

        # Pick a station of currently highest tier.
        station = self.order_by_station(new_resources)
        new_resources = [r for r in new_resources if self.stations[r.name] == station]

        return Equation(new_resources)

    def korvaa(self, equation: Equation, target: Equation):
        new_resources = []
        for resource in equation:
            if resource.name in self.resources:
                if resource in target.resources:
                    substituted = self.resources[resource.name]
                    substituted = substituted.make_copy()
                    substituted = substituted.multiply(resource.amount)
                    for new_resource in substituted:
                        new_resources.append(new_resource)
                else:
                    new_resources.append(resource)
            else:
                new_resources.append(resource)
        return Equation(new_resources)

    def search_variable(
        self, variable: str, equation: Equation, not_first: bool = False
    ) -> list[str]:
        variables = []
        for part in equation:

            # Variable occures in a derivative expression.
            if part.name == variable and not_first:
                variables.append(part.name)

            # Variable is required elsewhere as a workbench.
            if part.name in self.stations:
                station = self.stations[part.name]
                if variable == station:
                    variables.append(part.name)

            # Recursive function call for a derivative expression.
            if part.name in self.resources.keys():
                expression = self.resources[part.name]
                expression = expression.make_copy()
                found = self.search_variable(variable, expression, True)
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

    def order_by_station(self, resources: list[Resource]) -> str:
        """
        Return the order in which resources should be crafted in.
        Ordering is a numeric value based on items tier in tech tree.

        Example: 1 biofuel_extractor + 1 biofuel_generator = fabricator
        """

        max_station = self.stations[resources[0].name]
        max_value = self.get_station_value(max_station)
        for i in range(1, len(resources)):
            station = self.stations[resources[i].name]
            value = self.get_station_value(station)
            if max_value < value:
                max_value = value
                max_station = station
            elif max_value == value and max_station < station:
                max_value = value
                max_station = station

        return max_station

    def get_station_value(self, station: str) -> int:
        value = 1
        while station in self.stations:
            station = self.stations[station]
            value += 1
        return value

    def resources_per_station(self, equation: Equation) -> Equation:
        """
        Returns a material cost of an equation.

        Example: 1 biofuel_generator -> 20 steel_ingot + 8 copper_ingot + 12 electronics + 20 steel_screw + 2 glass
        Example: 40 iron_ore + 245 fiber = 40 iron_ore + 245 fiber
        """

        # Never alter the original copy.
        equation = equation.make_copy()

        crafting_cost = []
        for resource in equation:
            if resource.name in self.resources:

                # Never alter the original copy.
                new_equation = self.resources[resource.name]
                new_equation = new_equation.make_copy()

                # Calculate the amounts of new resources.
                for new_resource in new_equation:
                    new_resource.amount *= resource.amount
                    crafting_cost.append(new_resource)

            else:
                crafting_cost.append(resource)

        return Equation(crafting_cost).evaluate()

    def get_station(self, equation: Equation) -> str:
        """
        Returns the name of the crafting station where resources in equation can be crafted.
        Function assumes that all resources in an equation belong to the same crafting station.

        Example: 1 biofuel_extractor + 1 biofuel_generator -> fabricator
        Example: 1 cement_mixer + 1 concrete_furnace -> machining_bench
        Example: 40 iron_ore + 245 fiber -> total_resources
        Example: 1 biofuel_generator + 40 iron_ore -> fabricator
        """

        # There should be at least one resource to be crafted.
        if equation.resources == []:
            raise ValueError("Equation was empty.")

        # Convert items
        stations = []
        for resource in equation:
            if resource.name not in self.stations:
                stations.append("total_resources")
            else:
                station = self.stations[resource.name]
                stations.append(station)

        # All resources should be crafted at the same station.
        if stations.count(stations[0]) != len(stations):
            raise ValueError("Equation had multiple stations.")

        return stations[0]


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
