import difflib
import math
import re
from fractions import Fraction
from functools import reduce
from typing import Any, Callable, Iterator, Optional, Type

from mapping import recipe_sets_to_outputs


class Resource:
    """
    Resource class has only properties and no setters.
    Variables should be changed by making a new instance.
    Do not make factory methods, use the constructor!
    """

    def __init__(self, resource: tuple[Fraction, str] | tuple[int, str] | str | Any):

        self.__amount: Fraction = Fraction(0)
        self.__name: str = ""

        if isinstance(resource, Resource):
            copy = Resource.__clone(resource)
            self.__amount = copy.amount
            self.__name = copy.name
        elif isinstance(resource, tuple):
            self.__amount, self.__name = resource
        elif isinstance(resource, str):
            self.__amount, self.__name = Resource.__parse(resource)
        else:
            raise TypeError(type(resource))

    @property
    def amount(self) -> Fraction:
        return self.__amount

    @amount.setter
    def amount(self, amount: Fraction) -> None:
        # Fraction class is immutable.
        self.__amount = amount

    @property
    def name(self) -> str:
        return self.__name

    def __eq__(self, other: object) -> bool:
        result = False
        if isinstance(other, Resource):
            result = self.amount == other.amount and self.name == other.name
        return result

    def __str__(self) -> str:
        return f"{self.amount} {self.name}"

    def __repr__(self) -> str:
        return str(self)

    @classmethod
    def __parse(cls, resource: str) -> tuple[Fraction, str]:
        amount, name = resource.split(" ")
        return Fraction(amount), name

    @classmethod
    def __clone(cls, resource: "Resource") -> "Resource":
        return cls((resource.amount, resource.name))

    def format_resource(self, margin: int) -> str:
        amount: int = int(self.amount)
        return f"{amount:{margin}d} {self.name}"


class Equation:
    def __init__(self, resources: list[Resource] | list[str] | str | Any) -> None:
        self.__resources: list[Resource] = []

        def make_resource(item: Resource | str) -> Resource:
            if isinstance(item, Resource):
                return Resource(item)  # Copy constructor.
            elif isinstance(item, str):
                return Resource(item)
            else:
                raise TypeError(type(item))

        def make_resources(items: Equation | list[Resource] | list[str] | str):
            if isinstance(items, Equation):
                return Equation.__clone(items).resources  # Copy constructor.
            if isinstance(items, list):
                return [make_resource(item) for item in resources]
            elif isinstance(items, str):
                return Equation.__parse(items)
            else:
                raise TypeError(type(items))

        self.__resources = make_resources(resources)

    @property
    def resources(self) -> list[Resource]:
        # Resources are immutable thanks to the copy constructor.
        return list(map(lambda x: Resource(x), self.__resources))

    def __eq__(self, other: object) -> bool:
        result = False
        if isinstance(other, Equation):
            if len(self.resources) == len(other.resources):
                zipped = zip(self.resources, other.resources)
                mapped = map(lambda pair: pair[0] == pair[1], zipped)
                return reduce(lambda acc, cur: acc and cur, mapped, True)
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

    @classmethod
    def __parse(cls, equation: str) -> list[Resource]:
        resources: list[Resource] = []

        if parts := equation.split():
            amount = Fraction(parts[0])
            name = parts[1]
            resources.append(Resource((amount, name)))

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
            resources.append(Resource((amount, name)))

        return resources

    @classmethod
    def __clone(cls, equation: "Equation") -> "Equation":
        return cls([Resource((r.amount, r.name)) for r in equation])

    def multiply(self, fraction: Fraction) -> "Equation":
        resources = [Resource((fraction * r.amount, r.name)) for r in self.resources]
        return Equation(resources)

    def evaluate(self) -> "Equation":
        variables: dict[str, Resource] = dict()

        for resource in Equation(self):
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

            if (resource.amount <= 0 and all) or resource.amount > 0:
                new_resources.append(resource)

        return Equation(new_resources)

    def get_quantity(self, name: str) -> Fraction:
        copy = self.evaluate()
        for resource in copy.resources:
            if resource.name == name:
                return resource.amount
        return Fraction(0)


class EquationTree:
    def __init__(self, data: Optional[Resource] = None, station=None) -> None:
        self.children: list[EquationTree] = []
        self.data: Optional[Resource] = data
        self.station: Optional[str] = station

    def __iter__(self) -> Iterator[Equation]:
        """Helper function for unit tests"""
        if self.data:
            yield Equation([self.data])
        for tree_data in self.children:
            yield from tree_data

    def __str__(self) -> str:
        return str(self.data)


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

        resource = Resource(left)
        equation = Equation(right)
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
                if resource.name not in self.options:
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
                next_equation: Equation = self.resources[resource.name]
                stack += next_equation.resources.copy()

    def calculate(self, equation: Equation) -> Iterator[Equation]:
        """
        Function is intended to calculate required materials only.
        Non-positive materials will be filtered out of the final result.
        Do not use SURJECTIVE function to assert equivalence between two inputs.
        """
        while True:
            equation = equation.evaluate()
            positive = equation.suodata(False, False)
            exchange = self.suodata(positive)
            yield exchange

            equation = self.korvaa(equation, exchange)

            # Equation did not change so it is ready.
            if all([r.name in self.variables for r in positive]):
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

        new_resources = []
        for resource in equation:
            temp = Equation([r for r in equation if r.name != resource.name])
            # Recipes are not dependent on non-craftable recipes.
            temp = Equation([r for r in temp if r.amount > 0])
            found: list[str] = self.search_variable(resource.name, temp)
            if found == [] and resource.name in self.resources:
                # Reduce positive resources only.
                if resource.amount > 0:
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
                mapped = recipe_sets_to_outputs(station)
                if variable in (station, mapped):
                    variables.append(part.name)

            # Recursive function call for a derivative expression.
            if part.name in self.resources.keys():
                expression = self.resources[part.name]
                found = self.search_variable(variable, expression, True)
                if found != []:
                    variables.append(part.name)

        # Remove duplicates before returning.
        return list(dict.fromkeys(variables))

    def find_similar(self, equation: Equation) -> dict[str, list[str]]:
        assert isinstance(equation, Equation)

        word_list = self.get_keywords()
        similar_words: dict[str, list[str]] = dict()
        for resource in equation:
            words = difflib.get_close_matches(resource.name, word_list)
            if words != [] and resource.name not in word_list:
                similar_words[resource.name] = words

        assert isinstance(similar_words, dict)
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
            if max_value < value or (max_value == value and max_station < station):
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

        crafting_cost = []
        for resource in equation:
            if resource.name in self.resources:

                # Never alter the original copy.
                new_equation = self.resources[resource.name]

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

    def calculate_recursive(self, equation: Equation) -> EquationTree:
        """
        Equation tree represents the process of crafting items.
        Equation may have non-positive values but they will be ignored.
        Non-positive values make no sense when visualizing a crafting process.
        """

        equation = self.arrange_resources(equation)
        equation = equation.evaluate()
        nonpositive = Equation([r for r in equation if r.amount < 0])
        equation = Equation([r for r in equation if r.amount > 0])

        def create_equation_tree(
            root: EquationTree, equation: Equation, nonpositive: Equation
        ) -> tuple[EquationTree, Equation]:

            # Resources are read-only.
            resources = equation.resources
            resources += nonpositive

            # Equation is immutable.
            equation = Equation(resources)
            equation = equation.evaluate()

            nonpositive = Equation([r for r in equation if r.amount < 0])
            equation = Equation([r for r in equation if r.amount > 0])

            for resource in equation:
                # Wrap into tree data structure.
                node = EquationTree(resource)

                # Skip non-positive values.
                root.children.append(node)

                # Where resource should be crafted at.
                if resource.name in self.stations:
                    node.station = self.stations[resource.name]

                # Repeat for the remaining recipes.
                if resource.name in self.resources:
                    nodes = Equation([resource])
                    nodes = self.korvaa(nodes, nodes)
                    _, nonpositive = create_equation_tree(node, nodes, nonpositive)

            return root, nonpositive

        root = EquationTree()
        root, nonpositive = create_equation_tree(root, equation, nonpositive)
        return root

    def arrange_resources(self, equation: Equation) -> Equation:
        new_resources: list[Resource] = []
        while equation.resources:
            resources = self.suodata(equation).resources
            resources = sorted(resources, key=lambda r: r.amount, reverse=True)
            new_resources += resources
            equation = Equation([r for r in equation if r not in resources])
        return Equation(new_resources[::-1])

    def find_resources(self, equation: Equation) -> Iterator[str]:
        """
        Second version of function calculate.
        Generates recipe names one at a time.
        User may then repeat the process.
        """

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

    def find_workstations(self, equation: Equation) -> Equation:
        """List the required workstations."""

        equation = equation.evaluate()
        stations: list[str] = []
        names = self.find_resources(equation)
        for name in names:
            if name in self.stations:
                station = self.stations[name]
                if station not in self.resources:
                    # Recipes will be read directly from the game file.
                    # There's no need to support any other mapping function.
                    station = recipe_sets_to_outputs(station)
                if station in self.resources:
                    stations.append(station)
        stations = list(dict.fromkeys(stations))
        workstations: list[Resource] = []
        for station in stations[:]:
            quantity: Fraction = equation.get_quantity(station)
            if quantity == 0:
                # TODO: maybe destroy workstation?
                amount = Fraction(1)  # 1 + abs(quantity)
                resource = Resource((amount, station))
                workstations.append(resource)

        if workstations:
            # Resources are read-only.
            resources = equation.resources
            resources += workstations

            # Equation is immutable.
            equation = Equation(resources)
            equation = equation.evaluate()

            return self.find_workstations(equation)
        else:
            return equation

    def resolve_recipes_implicit(self, equation: Equation, callback: Callable) -> None:
        """
        Ask the user which recipe to use.
        Take into account all intermediate steps.
        """

        memory: list[str] = []
        equation = equation.evaluate()
        stack: list[str] = [r.name for r in equation]
        while stack != []:
            resource: str = stack.pop(0)
            if resource in memory:
                continue

            memory.append(resource)

            if resource in self.options:
                options = self.options[resource]

                choice: int = callback(options)

                line: str = options[choice]
                del self.options[resource]
                self.assign_equation(line)

            if resource in self.stations:
                station = self.stations[resource]
                if station not in memory and station not in stack:
                    stack.append(station)

            if resource in self.resources:
                new_resources = self.resources[resource]
                for new_resource in new_resources:
                    name = new_resource.name
                    if name not in memory and name not in stack:
                        stack.append(name)

    def convert_to_dictionaries(self, equation: EquationTree):
        """
        Converts an equation tree into a list of dictionaries
        where a single dictionary represents a resource class.
        Use this with json.dumps to stringify an equation tree.
        """

        def traverse(equations: list[EquationTree]):
            return list(
                map(
                    lambda root: {
                        "name": root.data.name,  # type: ignore
                        "amount": int(root.data.amount),  # type: ignore
                        "count": 1,  # TODO
                        "station": root.station,
                        "children": traverse(root.children),  # type: ignore
                    },
                    equations,
                )
            )

        return traverse(equation.children)


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
                if resource.name not in self.calc.options:
                    if resource.name not in self.calc.variables:
                        errors.append(resource.name)

            # Attempt to create raw materials is pointless.
            if resource.name in self.calc.variables and resource.amount >= 0:
                errors.append(f"{resource.amount} {resource.name}")

        if errors != []:
            error: str = ", ".join(errors)
            raise ValueError("ValueError: " + error)
