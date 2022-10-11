from fractions import Fraction
from typing import Callable, Iterator, Optional
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

    def format_resource(self, margin: int) -> str:
        amount: int = int(self.amount)
        return f"{amount:{margin}d} {self.name}"


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
        """
        Example: 1 wood - 2 wood
        Example: -1 wood + 0 wood
        """

        output = ""
        if self.resources:
            # Create an iterator to avoid accessing an index.
            iterator = iter(self.resources)

            # Print the first element as is.
            output = str(next(iterator))
            for resource in iterator:
                # Print an operator based on sign of number.
                output += " - " if resource.amount < 0 else " + "
                output += f"{abs(resource.amount)} {resource.name}"

        return output

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
        resources: list[Resource] = []

        if parts := equation.split():
            amount = Fraction(parts[0])
            name = parts[1]
            resources.append(Resource(amount, name))

        if (len(parts) - 2) % 3 != 0:
            error = "Error in equation: " + str(equation)
            raise ValueError(error)

        for i in range((len(parts) - 2) // 3):
            index = 2 + i * 3
            operator = parts[index]
            amount = Fraction(parts[index + 1])
            if operator == "-":
                amount = -amount
            name = parts[index + 2]
            resources.append(Resource(amount, name))

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
            amount = math.ceil(resource.amount)
            variables[name].amount = Fraction(amount)

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
        return [r.format_resource(margin) for r in self.sort_resources()]

    def suodata(self, all: bool = True, round: bool = True) -> "Equation":
        """Example: -1 stone + 1 wood - 12 wood = 0 stone + 1 wood + 0 wood"""

        new_resources: list[Resource] = []
        for resource in self.resources:
            if resource.amount < 0 and round:
                resource.amount = Fraction(0)

            if resource.amount <= 0 and all:
                new_resources.append(resource)
            elif resource.amount > 0:
                new_resources.append(resource)

        return Equation(new_resources)


class EquationTree:
    def __init__(self, data: Resource = None) -> None:
        self.children: list[EquationTree] = []
        self.data: Optional[Resource] = data

    def __iter__(self) -> Iterator[Equation]:
        if self.data:
            yield Equation([self.data])
        for tree_data in self.children:
            yield from tree_data


class Calculator:
    def __init__(self):
        # Validator depends on the file being read.
        self.validator: Validator = Validator(self)

        self.resources: dict[str, Equation] = dict()
        self.resources_str: dict[str, str] = dict()
        self.options: dict[str, list[str]] = dict()
        self.variables: list[str] = list()
        self.stations: dict[str, str] = dict()
        self.errors: list[str] = list()

    def assign_equation(self, assignment: str) -> None:
        # Validate an assignment before processing any further.
        self.validator.validate_syntax_assignment(assignment)

        # Every craftable resource should have a crafting station.
        station, assignment_tail = assignment.split(" : ")

        # Separate an assignment into a Resource and an Equation.
        left, right = assignment_tail.split(" = ")

        resource = Resource.parse(left)
        equation = Equation.parse(right)
        equation = equation.multiply(Fraction(1, resource.amount))

        name = resource.name

        # Variable name can be assigned just once.
        if name in self.resources:
            if name not in self.options:
                self.options[name] = []
                self.options[name].append(self.resources_str[name])
                self.options[name].append(assignment)
                del self.stations[name]
                del self.resources[name]
                del self.resources_str[name]
        elif name not in self.resources:
            if name not in self.options:
                self.resources[name] = equation
                self.stations[name] = station
                self.resources_str[name] = assignment
            elif name in self.options:
                self.options[name].append(assignment)

        # Resource will be removed from the variables list when it's assigned.
        self.variables = [var for var in self.variables if var != resource.name]

        # Add new variables into the unassigned variables list.
        for resource in equation.resources:
            if resource.name not in self.resources:
                if resource.name not in self.variables:
                    self.variables.append(resource.name)

    def get_keywords(self) -> list[str]:
        keywords = list(self.resources.keys())
        keywords += self.options.keys()
        keywords += self.variables.copy()

        # Remove duplicates keywords.
        return list(dict.fromkeys(keywords))

    def resolve_recipes(self, equation: Equation, callback: Callable) -> None:
        stack: list[Resource] = equation.resources[:]
        while stack != []:
            resource: Resource = stack.pop(0)
            if resource.name in self.options.keys():
                options = self.options[resource.name]

                # Return control to application to ask user.
                # Application does not need to know details.
                choice: int = callback(options)

                line = self.options[resource.name][choice]
                del self.options[resource.name]
                self.assign_equation(line)
            if resource.name in self.resources:
                next: Equation = self.resources[resource.name]
                stack += next.resources.copy()

    def calculate(self, equation: Equation) -> Iterator[Equation]:
        while True:
            equation = equation.evaluate()
            suodatettu = self.suodata(equation)

            yield suodatettu
            equation = self.korvaa(equation, suodatettu)

            # Equation did not change so it is ready.
            if equation == suodatettu:
                break

        return equation

    def calculate_2nd(self, user_input: str) -> Iterator[str]:
        """
        Second version of function calculate.
        Generates recipe names one at a time.
        User may then repeat the process.
        TODO: ei kaytossa
        """

        equation: Equation = Equation.parse(user_input)
        while True:
            equation = equation.evaluate()
            suodatettu = self.suodata(equation)
            for resource in suodatettu:
                if resource.name in self.resources:
                    yield resource.name
            equation = self.korvaa(equation, suodatettu)

            # Equation did not change so it is ready.
            if equation == suodatettu:
                break

        return equation

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

            # Expression contains optional subexpressions.
            # TODO: ei kaytossa missaan mutta testattu
            if part.name == variable and variable in self.options:
                variables.append(part.name)

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

        # Remove duplicates before returning.
        return list(dict.fromkeys(variables))

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
            raise AssertionError("Equation was empty.")

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
            raise AssertionError("Multiple stations: %s" % ", ".join(stations))

        return stations[0]

    def calculate_recursive(self, equation: Equation) -> Iterator[Equation]:
        def create_equation_tree(
            root: EquationTree, equation: Equation
        ) -> EquationTree:
            equation = equation.evaluate()
            for resource in equation:
                node = EquationTree(resource)
                root.children.append(node)
                if resource.name in self.resources:
                    nodes = Equation([resource])
                    nodes = self.korvaa(nodes, nodes)
                    create_equation_tree(node, nodes)
            return root

        root = EquationTree()
        return iter(create_equation_tree(root, equation))


class Validator:
    pattern_num = "[1-9]+[0-9]*(?:/[1-9]+[0-9]*)*"
    pattern_var = "(?:[0-9]+[-_])*[a-z/0-9]+(?:[-_][a-z/0-9]+)*"

    def __init__(self, calc: Calculator):
        self.calc = calc

    def validate_syntax_assignment(self, assignment: str) -> None:
        num = Validator.pattern_num
        var = Validator.pattern_var

        pattern = re.compile(f"{var} : {num} {var} = {num} {var}( [+-] {num} {var})*")
        if not pattern.fullmatch(assignment):
            raise SyntaxError("SyntaxError: " + assignment)

    def validate_syntax_calculation(self, equation: str) -> None:
        num = Validator.pattern_num
        var = Validator.pattern_var

        pattern = re.compile(f"[-]?{num} {var}( [+-] {num} {var})*")
        if not pattern.fullmatch(equation):
            raise SyntaxError("SyntaxError: " + equation)

    def validate_value_calculation(self, equation: Equation) -> None:
        errors: list[str] = []
        for resource in equation:

            # Resource should be mentioned in tech tree.
            if resource.name not in self.calc.resources:
                if resource.name not in self.calc.variables:
                    errors.append(resource.name)

            # Attempt to create raw materials is pointless.
            if resource.name in self.calc.variables:
                if resource.amount >= 0:
                    errors.append(f"{resource.amount} {resource.name}")

        if errors != []:
            error: str = ", ".join(errors)
            raise ValueError("ValueError: " + error)
