import json
import unittest
from collections import deque
from fractions import Fraction

from ddt import data, ddt, unpack
from test_application import FileSystemTest, JsonSystemTest

from application import FileSystem, JsonSystem
from calculator import Calculator, Equation, EquationTree, Resource


@ddt
class ResourceTest(unittest.TestCase):
    @data(
        (1, "anvil_bench"),
        (10, "iron_ingot"),
        (-1, "anvil_bench"),
        (-10, "iron_ingot"),
    )
    @unpack
    def test_resource_init(self, amount: int, name: str):
        r1 = Resource((amount, name))
        r2 = Resource((Fraction(amount), name))

        self.assertEqual(r1, r2)

        r1 = Resource._Resource__parse(str(r1))
        r2 = Resource._Resource__parse(str(r2))

        self.assertEqual(r1, r2)

    @data(
        "1 anvil_bench",
        "10 iron_ingot",
        "-1 anvil_bench",
        "-10 iron_ingot",
    )
    def test_resource_parse(self, value: str):
        r1 = Resource(Resource._Resource__parse(value))
        r2 = Resource(Resource._Resource__parse(str(r1)))

        self.assertEqual(value, str(r1))
        self.assertEqual(r1, r2)

    def test_resource_clone(self):
        r1 = Resource("1 fiber")
        r2 = Resource._Resource__clone(r1)

        self.assertEqual(r1, r2)

        with self.assertRaises(AttributeError):
            r1.amount = Fraction(2)

        self.assertEqual(1, r1.amount)
        self.assertEqual(1, r2.amount)
        self.assertEqual(r1, r2)

    @data(
        ("2 biofuel_extractor", True),
        ("2 biofuel_generator", False),
        ("4 biofuel_generator", False),
    )
    @unpack
    def test_eq(self, value: str, expected: bool):
        r = Resource("2 biofuel_extractor")
        self.assertEqual(expected, r == Resource(value))


@ddt
class EquationTest(unittest.TestCase):
    @data(
        ("12 fiber", ["12 fiber"]),
        ("12 fiber + 18 stick", ["12 fiber", "18 stick"]),
        ("-12 fiber", ["-12 fiber"]),
        ("-12 fiber - 18 stick", ["-12 fiber", "-18 stick"]),
    )
    @unpack
    def test_equation_init(self, first: str, second: list[str]):
        e1 = Equation(first)
        e2 = Equation(second)

        self.assertEqual(e1, e2)

    @data(
        ("12 fiber", "12 fiber"),
        ("12 fiber + 18 stick", "12 fiber + 18 stick"),
        ("-12 fiber", "-12 fiber"),
        ("-12 fiber - 18 stick", "-12 fiber - 18 stick"),
        ("-12 fiber - -18 stick", "-12 fiber + 18 stick"),
    )
    @unpack
    def test_equation_parse(self, first: str, second: str):
        e1 = Equation(Equation._Equation__parse(first))
        e2 = Equation(Equation._Equation__parse(str(e1)))

        self.assertEqual(second, str(e1))
        self.assertEqual(e1, e2)

    def test_equation_clone(self):
        """Equation should be immutable."""

        e1 = Equation("12 fiber")
        e2 = Equation._Equation__clone(e1)

        self.assertEqual(e1, e2)

        with self.assertRaises(AttributeError):
            r1 = e2.resources[0]
            r1.amount = Fraction(13)

        self.assertEqual(e1, e2)

    @data(
        ("2 fiber + 4 fiber + 2 wood + 2 wood", True),
        ("2 fiber + 4 fiber + 4 wood + 0 wood", False),
        ("2 fiber + 4 fiber + 6 wood - 2 wood", False),
        ("2 fiber + 4 fiber + 2 wood", False),
        ("-2 fiber - 2 wood - 4 fiber - 2 wood", False),
        ("2 wood + 2 wood + 4 fiber + 2 fiber", False),
    )
    @unpack
    def test_equation_eq(self, value: str, expected: bool):
        e = Equation("2 fiber + 4 fiber + 2 wood + 2 wood")
        self.assertEqual(expected, e == Equation(value))

    @data(
        ("124/5 wood + 160 stone + 0/24 leather", "25 wood + 160 stone + 0 leather"),
        ("1/3 wood + 0 stone + 1/3 wood", "1 wood + 0 stone"),
        (
            "10 gold_ore + 30 copper_ore + 10 wood + 10 oxite + 20 sulfur + 16 wood",
            "10 gold_ore + 30 copper_ore + 26 wood + 10 oxite + 20 sulfur",
        ),
        ("1 wood - 2 wood - 2 stone - 3/2 sulfur", "-1 wood - 2 stone - 1 sulfur"),
    )
    @unpack
    def test_evaluate(self, value: str, expected: str):
        e = Equation(value).evaluate()
        self.assertEqual(expected, str(e))

    def test_sort_resources(self):
        """Sort by an amount then by a name."""

        e1 = "10 gold_ore + 30 copper_ore + 26 wood + 10 oxite + 26 sulfur"
        e2 = "30 copper_ore + 26 sulfur + 26 wood + 10 gold_ore + 10 oxite"

        self.assertEqual(e2, str(Equation(e1).sort_resources()))
        self.assertEqual(e2, str(Equation(e2).sort_resources()))

    def test_format_resources(self):
        e = "10 copper_ingot + 2 iron_ingot + 100 gold_ore + 10 aluminium_ingot"
        iterator = iter(Equation(e).format_resources())

        self.assertEqual("100 gold_ore", next(iterator))
        self.assertEqual(" 10 aluminium_ingot", next(iterator))
        self.assertEqual(" 10 copper_ingot", next(iterator))
        self.assertEqual("  2 iron_ingot", next(iterator))
        self.assertRaises(StopIteration, next, iterator)

    # TODO: erota eri funktioiksi
    def test_suodata(self):
        equation = Equation("-1 stone + 1 wood - 12 wood")

        expected = Equation("1 wood")
        self.assertEqual(expected, equation.suodata(all=False, round=False))

        expected = Equation("-1 stone + 1 wood - 12 wood")
        self.assertEqual(expected, equation.suodata(all=True, round=False))

        expected = Equation("0 stone + 1 wood + 0 wood")
        self.assertEqual(expected, equation.suodata(all=True, round=True))


@ddt
class CalculatorTest(unittest.TestCase):
    def setUp(self) -> None:
        """Create a calculator before any test method."""
        self.calc = Calculator()
        filesystem = FileSystem(FileSystemTest.filename)
        filesystem.read(self.calc)

        self.calculator = Calculator()
        filesystem = JsonSystem(JsonSystemTest.filename)
        filesystem.read(self.calculator)

    def test_get_keywords(self):
        """Keywords consit of assigned variable names."""
        calc = Calculator()

        self.assertEqual([], calc.get_keywords())

        calc.assign_equation("character : 1 wood_spear = 12 fiber + 18 stick")
        calc.assign_equation("character : 10 stick = 1 wood")

        self.assertEqual(["wood_spear", "stick", "fiber", "wood"], calc.get_keywords())

    def test_get_keywords_read_json(self):
        filesystem = JsonSystem(JsonSystemTest.filename)
        filesystem.read(calculator := Calculator())

        keywords = calculator.get_keywords()

        # Keywords should contain unique recipes.
        self.assertIn("crafting_bench", calculator.resources.keys())
        self.assertIn("crafting_bench", keywords)
        for resource in calculator.resources.keys():
            self.assertIn(resource, keywords)

        # Keywords should contain optional recipes
        self.assertIn("refined_metal", calculator.options.keys())
        self.assertIn("refined_metal", keywords)
        for option in calculator.options.keys():
            self.assertIn(option, keywords)

        # Keywords should contain unique and optional variables
        self.assertIn("stringy_meat", calculator.variables)
        self.assertIn("stringy_meat", keywords)
        for variable in calculator.variables:
            self.assertIn(variable, keywords)

        # Keywords should not contain duplicates.
        self.assertEqual(keywords, list(dict.fromkeys(keywords)))

    def test_assign_equation_1(self):
        """An equation should be stored in a dictionary as follows."""
        calc = Calculator()

        calc.assign_equation("character : 1 wood_spear = 12 fiber + 18 stick")
        calc.assign_equation("character : 10 stick = 1 wood")
        calc.assign_equation("machining_bench : 1 steel_screw = 1/100 steel_ingot")

        e1 = calc.resources["wood_spear"]
        e2 = calc.resources["stick"]
        e3 = calc.resources["steel_screw"]

        self.assertEqual("12 fiber + 18 stick", str(e1))
        self.assertEqual("1/10 wood", str(e2))
        self.assertEqual("1/100 steel_ingot", str(e3))

    def test_assign_equation_2(self):
        """
        Resources or variables should not have duplicate entries.
        A duplicate equation should stage optional equations.
        An user should choose a correct equation themselves.
        """
        calc = Calculator()

        calc.assign_equation("crafting_bench : 1 rope = 12 fiber")
        calc.assign_equation("crafting_bench : 1 rope = 12 fiber")
        calc.assign_equation("character : 1 rope = 5 leather")

        with self.assertRaises(KeyError) as err:
            calc.resources["rope"]

        equations = calc.options["rope"]

        self.assertEqual(3, len(equations))
        self.assertEqual("crafting_bench : 1 rope = 12 fiber", equations[0])
        self.assertEqual("crafting_bench : 1 rope = 12 fiber", equations[1])
        self.assertEqual("character : 1 rope = 5 leather", equations[2])

    def test_assign_equation_3(self):
        calc = self.calc

        resources = list(calc.resources)
        variables = list(calc.variables)

        for resource in resources:
            self.assertEqual(1, resources.count(resource))
            self.assertFalse(resource in variables)
        for variable in variables:
            self.assertEqual(1, variables.count(variable))
            self.assertFalse(variable in resources)

    def test_assign_equation_4(self):
        """A wrong equation should raise an exception."""
        calc = Calculator()

        error_input = [
            "crafting_bench : 1 lightning_rod = 10 copper ingot",
            "crafting_bench : 1 lightning rod = 10 copper_ingot",
            "crafting_bench : lightning_rod = 10 copper_ingot",
            "crafting_bench : 1 lightning_rod = copper_ingot",
            "crafting_bench : 1 1 lightning_rod = 10 copper_ingot",
            "crafting_bench : 1 lightning_rod = 10 10 copper_ingot",
            "crafting_bench : 1 lightning_rod = 10 copper_ingot +",
            "crafting_bench : 1 lightning_rod = + 10 copper_ingot",
            "crafting_bench : 1 lightning_rod 10 copper_ingot",
            "crafting_bench : 1 lightning_rod + 10 copper_ingot",
            "1 lightning_rod = 10 copper_ingot",
            "1 lightning_rod + 10 copper_ingot",
        ]

        for error in error_input:
            with self.assertRaises(SyntaxError) as err:
                calc.assign_equation(error)
            self.assertEqual(f"SyntaxError: {error}", str(err.exception))

    def test_search_variable(self):
        e1 = self.calc.resources["hunting_rifle"]
        e2 = self.calc.resources["steel_ingot"]
        e3 = self.calc.resources["steel_bloom"]

        self.assertEqual([], self.calc.search_variable("steel_screw", e1))
        self.assertEqual(["steel_screw"], self.calc.search_variable("steel_ingot", e1))
        self.assertEqual(["steel_screw"], self.calc.search_variable("steel_ingot", e1))
        self.assertEqual(["steel_screw"], self.calc.search_variable("steel_bloom", e1))
        self.assertEqual([], self.calc.search_variable("iron_ingot", e1))
        self.assertEqual(["steel_screw"], self.calc.search_variable("iron_ore", e1))

        self.assertEqual([], self.calc.search_variable("steel_bloom", e2))
        self.assertEqual([], self.calc.search_variable("iron_ingot", e2))
        self.assertEqual(["steel_bloom"], self.calc.search_variable("iron_ore", e2))
        self.assertEqual([], self.calc.search_variable("iron_ingot", e3))
        self.assertEqual([], self.calc.search_variable("iron_ore", e3))

    def test_search_optional_expression(self):
        e1 = Equation("1 rifle_hunting")
        e2 = Equation(
            "12 wood + 8 leather + 40 titanium_ingot + 4 epoxy + 16 steel_screw"
        )

        self.assertIn("metal_ore", self.calculator.variables)
        self.assertNotIn("metal_ore", self.calculator.resources)
        self.assertEqual([], self.calculator.search_variable("metal_ore", e1))
        self.assertEqual([], self.calculator.search_variable("metal_ore", e2))

        self.assertIn("epoxy", self.calculator.options)
        self.assertNotIn("epoxy", self.calculator.resources)
        self.assertEqual(
            ["rifle_hunting"], self.calculator.search_variable("epoxy", e1)
        )
        self.assertEqual(["epoxy"], self.calculator.search_variable("epoxy", e2))

    def test_search_variable_remove_duplicates(self):
        e1 = Equation("1 epoxy + 1 epoxy + 1 rope + 1 rope")
        self.assertEqual(["epoxy"], self.calculator.search_variable("epoxy", e1))
        self.assertEqual(["rope"], self.calculator.search_variable("rope", e1))

    def test_calculate_last_element(self):
        """Equation should contain only raw materials as the last element."""

        e1 = "60 fiber + 50 wood + 12 stone + 20 leather"
        e2 = "80 iron_ore + 20 wood + 10 stone"
        e3 = "25 wood + 160 stone + 24 leather"
        e4 = "80 iron_ore"
        e5 = "1 wood"

        self.assertEqual(e1, self.get_last_element("1 crafting_bench"))
        self.assertEqual(e2, self.get_last_element("1 anvil_bench"))
        self.assertEqual(e3, self.get_last_element("2 stone_furnace"))
        self.assertEqual(e4, self.get_last_element("40 iron_ingot"))
        self.assertEqual(e5, self.get_last_element("8 stick"))

    def test_calculate_first_element(self):
        """Equation should evaluate subtraction in the first element as well."""

        e1 = "120 00_buckshot_shell - 40 00_buckshot_shell"
        e2 = "1 biofuel_extractor + 1 biofuel_generator"

        self.assertEqual("80 00_buckshot_shell", self.get_first_element(e1))
        self.assertEqual("1 biofuel_generator", self.get_first_element(e2))

    def test_calculate_negative_amount(self):
        """
        Removing a total amount of a particular resource should total to zero.
        Total amount should always be positive regardless of the number of iterations.
        """

        e1 = "1 stone_furnace + 1 anvil_bench + 1 machining_bench"
        e2 = "1 stone_furnace + 1 anvil_bench + 1 machining_bench - 102 stone - 69 wood"
        e3 = "1 stone_furnace + 1 anvil_bench + 1 machining_bench - 100 stone - 70 wood"

        self.assertIn("102 stone", self.get_last_element(e1))
        self.assertIn("69 wood", self.get_last_element(e1))

        self.assertNotIn("0 stone", self.get_last_element(e2))
        self.assertNotIn("0 wood", self.get_last_element(e2))

        self.assertIn("2 stone", self.get_last_element(e3))
        self.assertNotIn("-1 wood", self.get_last_element(e3))

    def test_calculate_two_times(self):
        """Same amount of resources should have same crafting cost."""

        self.assertEqual(
            self.get_last_element("1 anvil_bench + 1 anvil_bench"),
            self.get_last_element("2 anvil_bench"),
        )

        self.assertEqual(
            self.get_last_element("1 anvil_bench - 1 anvil_bench"),
            self.get_last_element("0 anvil_bench"),
        )

    def test_calculate_electric_extractor(self):
        """Crafting cost of an electric extractor."""

        # 20 iron_ingot = 40 iron_ore
        e0 = "20 iron_ingot"
        e1 = "40 iron_ore"

        self.assertEqual(self.get_last_element(e0), self.get_last_element(e1))
        self.assertEqual(self.get_last_element(e0), e1)

        # 5 electronics = 10 gold_ore + 30 copper_ore + 26 wood + 10 oxite + 20 sulfur
        e0 = "5 electronics"
        e1 = "5 refined_gold + 15 copper_ingot + 10 organic_resin + 10 epoxy"
        e2 = (
            "10 gold_ore + 30 copper_ore + 10 wood + 10 oxite + 20 sulfur + 40 tree_sap"
        )
        e3 = "10 gold_ore + 30 copper_ore + 10 wood + 10 oxite + 20 sulfur + 160 stick"
        e4 = "10 gold_ore + 30 copper_ore + 26 wood + 10 oxite + 20 sulfur"

        self.assertEqual(self.get_last_element(e0), self.get_last_element(e1))
        self.assertEqual(self.get_last_element(e0), self.get_last_element(e2))
        self.assertEqual(self.get_last_element(e0), self.get_last_element(e3))
        self.assertEqual(self.get_last_element(e0), self.get_last_element(e4))
        self.assertEqual(self.get_last_element(e0), e4)

        # 3 electric_extractor = 120 iron_ore + 30 gold_ore + 90 copper_ore + 78 wood + 30 oxite + 60 sulfur
        e0 = "3 electric_extractor"
        e1 = "60 iron_ingot + 15 electronics"
        e2 = "120 iron_ore + 30 gold_ore + 90 copper_ore + 78 wood + 30 oxite + 60 sulfur"

        self.assertEqual(self.get_last_element(e0), self.get_last_element(e1))
        self.assertEqual(self.get_last_element(e0), self.get_last_element(e2))
        self.assertEqual(self.get_last_element(e0), e2)

    def test_calculate_hunting_rifle(self):
        """Crafting cost of a hunting rifle."""

        # 40 titanium_ingot = 200 titanium_ore
        e0 = "40 titanium_ingot"
        e1 = "200 titanium_ore"

        self.assertEqual(self.get_last_element(e0), self.get_last_element(e1))
        self.assertEqual(self.get_last_element(e0), e1)

        # 4 epoxy = 8 sulfur + 7 wood
        e0 = "4 epoxy"
        e1 = "8 sulfur + 16 tree_sap"
        e2 = "8 sulfur + 64 stick"
        e3 = "8 sulfur + 7 wood"

        self.assertEqual(self.get_last_element(e0), self.get_last_element(e1))
        self.assertEqual(self.get_last_element(e0), self.get_last_element(e2))
        self.assertEqual(self.get_last_element(e0), self.get_last_element(e3))
        self.assertEqual(self.get_last_element(e0), e3)

        # 16 steel_screw = 6 iron_ore + 1 coal_ore
        e0 = "16 steel_screw"
        e1 = "1 steel_ingot"
        e2 = "6 iron_ore + 1 coal_ore"

        self.assertEqual(self.get_last_element(e0), self.get_last_element(e1))
        self.assertEqual(self.get_last_element(e0), self.get_last_element(e2))
        self.assertEqual(self.get_last_element(e0), e2)

        # 1 hunting_rifle = 19 wood + 8 leather + 200 titanium_ore + 8 sulfur + 6 iron_ore + 1 coal_ore
        e0 = "1 hunting_rifle"
        e1 = "12 wood + 8 leather + 40 titanium_ingot + 4 epoxy + 16 steel_screw"
        e2 = "19 wood + 8 leather + 200 titanium_ore + 8 sulfur + 6 iron_ore + 1 coal_ore"

        self.assertEqual(self.get_last_element(e0), self.get_last_element(e1))
        self.assertEqual(self.get_last_element(e0), self.get_last_element(e2))
        self.assertEqual(self.get_last_element(e0), e2)

    def test_calculate_subtraction_zero(self):
        e1 = "1 machining_bench - 1 fabricator"
        e2 = "1 machining_bench"

        a1 = "36 wood + 12 stone + 104 iron_ore + 20 sulfur + 288 fiber"

        self.assertEqual(a1, self.get_last_element(e1))
        self.assertEqual(a1, self.get_last_element(e2))

    def test_calculate_subtraction_negative(self):
        e1 = "1 machining_bench - 30 epoxy"
        e2 = "1 machining_bench - 10 epoxy"

        a1 = "20 wood + 12 stone + 104 iron_ore + 288 fiber"
        a2 = "20 wood + 12 stone + 104 iron_ore + 288 fiber"

        self.assertEqual(a1, self.get_last_element(e1))
        self.assertEqual(a2, self.get_last_element(e2))

    def test_find_similar(self):
        """There may be none, one or many good enough matches."""
        calc = self.calc

        e1 = Equation("1 anvil")
        e2 = Equation("1 anvil_bvve")
        e3 = Equation("1 anvil_benchs")
        e4 = Equation("1 anvi")

        self.assertEqual(["anvil_bench"], calc.find_similar(e1)["anvil"])
        self.assertIn("anvil_bench", calc.find_similar(e2)["anvil_bvve"])
        self.assertIn("anvil_bench", calc.find_similar(e3)["anvil_benchs"])

        # The dictionary omits searches that have no matches.
        with self.assertRaises(KeyError):
            calc.find_similar(e4)["anvi"]

        # The dictionary omits exact matches.
        with self.assertRaises(KeyError):
            calc.find_similar(e1)["anvil_bench"]

    def test_find_similar_optional_recipes(self):
        """There was a bug and test assures it's gone."""

        e1 = Equation("1 machining_bench - 10 epoxy")
        words = list(self.calculator.find_similar(e1))
        self.assertEqual(["machining_bench"], words)

    def test_order_by_station(self):
        r1 = Resource("1 biofuel_extractor")
        r2 = Resource("1 biofuel_generator")

        self.assertEqual("fabricator", self.calc.order_by_station([r1, r2]))

    def test_order_by_station_revisit_workbench(self):
        """
        Some resources require more than one visit to the workbench.

        Problem:
        - concrete_furnace: carbon_fiber
        - mortar_and_pestle: carbon_paste
        - concrete_furnace: aluminium_ingot
        """
        r1 = Resource("8 carbon_fiber")
        r2 = Resource("1 steel_ingot")

        self.assertEqual("concrete_furnace", self.calc.order_by_station([r1, r2]))

    def test_get_station_value(self):
        self.assertEqual(1, self.calc.get_station_value("character_crafting"))
        self.assertEqual(2, self.calc.get_station_value("crafting_bench"))
        self.assertEqual(3, self.calc.get_station_value("machining_bench"))
        self.assertEqual(4, self.calc.get_station_value("fabricator"))
        self.assertEqual(3, self.calc.get_station_value("mortar_and_pestle"))
        self.assertEqual(4, self.calc.get_station_value("concrete_furnace"))

    def test_suodata_practical_1(self):
        equation = Equation("1 biofuel_extractor + 1 biofuel_generator")
        expected = Equation("1 biofuel_generator")
        self.assertEqual(expected, self.calc.suodata(equation))

    def test_suodata_practical_2(self):
        equation = Equation("1 cement_mixer + 1 concrete_furnace")
        expected = Equation("1 concrete_furnace")
        self.assertEqual(expected, self.calc.suodata(equation))

    def test_suodata_practical_3(self):
        equation = Equation("1 stone_furnace + 1 anvil_bench + 1 machining_bench")
        expected = Equation("1 machining_bench")
        self.assertEqual(expected, self.calc.suodata(equation))

    def test_suodata_practical_4(self):
        equation = Equation(
            "1 anvil_bench + 1 machining_bench + 1 cement_mixer + 1 concrete_furnace + 1 fabricator"
        )
        expected = Equation("1 fabricator")
        self.assertEqual(expected, self.calc.suodata(equation))

    def test_suodata_practical_5(self):
        equation = Equation(
            "4 stick + 52 wood + 102 stone + 12 leather + 184 iron_ore + 0 epoxy + 288 fiber"
        )
        expected = Equation("4 stick")
        self.assertEqual(expected, self.calc.suodata(equation))

    def test_suodata_practical_6(self):
        equation = Equation(
            "48 aluminium_ore + 60 gold_ore + 180 copper_ore + 386 wood + 92 oxite + 176 sulfur + 542 stone + 208 silica + 6 iron_ore + 1 coal_ore + 73 iron_ingot + 252 fiber + 32 leather"
        )
        expected = Equation("73 iron_ingot")
        self.assertEqual(expected, self.calc.suodata(equation))

    def test_suodata_raw_materials(self):
        equation = Equation("1 iron_ore + 1 wood")
        expected = Equation(equation)
        self.assertEqual(expected, self.calc.suodata(equation))

    def test_suodata_does_not_change_parameter(self):
        equation = Equation("1 anvil_bench + 1 anvil_bench")
        expected = Equation(equation)
        self.assertEqual(expected, self.calc.suodata(equation))

    def test_korvaa_1(self):
        calc = self.calc

        e1 = Equation("1 biofuel_extractor + 1 biofuel_generator")
        e2 = Equation("1 biofuel_generator")
        e3 = Equation(
            "1 biofuel_extractor + 20 steel_ingot + 8 copper_ingot + 12 electronics + 20 steel_screw + 2 glass"
        )

        self.assertEqual(e3, calc.korvaa(e1, e2))

        e1 = Equation("1 biofuel_extractor + 2 biofuel_generator")
        e2 = Equation("2 biofuel_generator")
        e3 = Equation(
            "1 biofuel_extractor + 40 steel_ingot + 16 copper_ingot + 24 electronics + 40 steel_screw + 4 glass"
        )

        self.assertEqual(e3, calc.korvaa(e1, e2))

    def test_korvaa_2(self):
        calc = self.calc

        e1 = Equation("40 iron_ingot + 20 wood + 10 stone")
        e2 = Equation("40 iron_ingot")
        e3 = Equation("80 iron_ore + 20 wood + 10 stone")

        self.assertEqual(e3, calc.korvaa(e1, e2))

    def test_korvaa_3(self):
        calc = self.calc

        r1 = Equation("2 hunting_rifle")
        r2 = Equation("16 steel_screw")
        r3 = Equation("10 stick")

        e1 = calc.korvaa(r1, r1)
        e2 = calc.korvaa(r2, r2)
        e3 = calc.korvaa(r3, r3)

        self.assertEqual(
            "24 wood + 16 leather + 80 titanium_ingot + 8 epoxy + 32 steel_screw",
            str(e1),
        )
        self.assertEqual("4/25 steel_ingot", str(e2))
        self.assertEqual("1 wood", str(e3))

    def test_resources_per_station(self):
        """
        Return the exact material cost as is written in the tech tree.
        > 1 biofuel_generator = 20 steel_ingot + 8 copper_ingot + 12 electronics + 20 steel_screw + 2 glass
        """

        e1 = Equation("1 biofuel_generator")

        r1 = Resource("20 steel_ingot")
        r2 = Resource("8 copper_ingot")
        r3 = Resource("12 electronics")
        r4 = Resource("20 steel_screw")
        r5 = Resource("2 glass")

        expected = Equation([r1, r2, r3, r4, r5])

        self.assertEqual(expected, self.calc.resources_per_station(e1))

    def test_resources_per_station_raw_materials(self):
        """
        Return the original equation since raw materials don't have any recipes.
        > 40 iron_ore + 245 fiber = 40 iron_ore + 245 fiber
        """

        r1 = Resource("40 iron_ore")
        r2 = Resource("245 fiber")
        e1 = Equation([r1, r2])

        self.assertEqual(e1, self.calc.resources_per_station(e1))

    def test_resources_per_station_multiple_stations(self):
        """
        Returns a material cost of an equation.
        Equation may have recipes for multiple stations.
        """
        calc = self.calc

        e1 = Equation("1 biofuel_generator + 40 iron_ore + 245 fiber")

        r1 = Resource("20 steel_ingot")
        r2 = Resource("8 copper_ingot")
        r3 = Resource("12 electronics")
        r4 = Resource("20 steel_screw")
        r5 = Resource("2 glass")
        r6 = Resource("40 iron_ore")
        r7 = Resource("245 fiber")

        expected = Equation([r1, r2, r3, r4, r5, r6, r7])

        self.assertEqual(expected, calc.resources_per_station(e1))

    def test_get_station(self):
        """Returns a name of station where items can be crafted."""
        calc = self.calc

        e1 = Equation("1 biofuel_generator")
        e2 = Equation("40 iron_ore + 245 fiber")

        self.assertEqual("fabricator", calc.get_station(e1))
        self.assertEqual("total_resources", calc.get_station(e2))

    def test_get_station_empty_equation(self):
        """
        Trying to get crafting station for empty equation is an error.
        Responsibility lies on the function caller.
        """
        calc = self.calc

        with self.assertRaises(AssertionError) as err:
            calc.get_station(Equation([]))
        self.assertEqual("Equation was empty.", str(err.exception))

    def test_get_station_multiple_stations(self):
        """
        Trying to get one return value for multiple suitable stations is an error.
        Responsibility lies on the function caller.
        """
        calc = self.calc

        e1 = Equation("1 biofuel_generator + 1 iron_ore")
        with self.assertRaises(AssertionError) as err:
            calc.get_station(e1)
        self.assertEqual(
            "Multiple stations: fabricator, total_resources", str(err.exception)
        )

    def get_first_element(self, equation: str) -> str:
        return str(next(self.calc.calculate(Equation(equation))))

    def get_last_element(self, equation: str) -> str:
        gen = self.calc.calculate(Equation(equation))
        return str(deque(gen, maxlen=1).pop())

    def test_convert_to_dictionaries(self):
        equation = Equation("1 fabricator + 40 iron_ingot")
        equation_tree = self.calc.calculate_recursive(equation)
        dictionaries = self.calc.convert_to_dictionaries(equation_tree)
        actual = json.dumps(dictionaries, indent=2)

        with open("test/testdata/test_json_api_01.json") as reader:
            expect: str = reader.read().strip()

        self.maxDiff = None
        self.assertEqual(expect, actual)

    def test_find_resources(self):
        e1 = [
            "electric_extractor",
            "iron_ingot",
            "electronics",
            "refined_gold",
            "copper_ingot",
            "organic_resin",
            "epoxy",
            "tree_sap",
            "stick",
        ]
        a1 = Equation("3 electric_extractor")
        self.assertEqual(e1, list(self.calc.find_resources(a1)))

    @data(
        {
            "user_input": [
                "1 fabricator",
            ],
            "expected_output": [
                "1 fabricator",
                "1 machining_bench",
                "1 concrete_furnace",
                "1 cement_mixer",
                "1 mortar_and_pestle",
                "1 stone_furnace",
                "1 crafting_bench",
                "1 anvil_bench",
            ],
        },
        {
            "user_input": [
                "1 concrete_furnace",
                "-1 machining_bench",
            ],
            "expected_output": [
                "1 concrete_furnace",
                "-1 machining_bench",
                "1 cement_mixer",
                "1 stone_furnace",
                "1 mortar_and_pestle",
                "1 crafting_bench",
                "1 anvil_bench",
            ],
        },
        {
            "user_input": [
                "1 fabricator",
                "1 machining_bench",
                "-3 stone_furnace",
                "0 concrete_furnace",
            ],
            "expected_output": [
                "1 fabricator",
                "1 machining_bench",
                "-3 stone_furnace",
                "1 concrete_furnace",
                "1 cement_mixer",
                "1 mortar_and_pestle",
                "1 crafting_bench",
                "1 anvil_bench",
            ],
        },
    )
    @unpack
    def test_find_workstations(self, user_input, expected_output):
        equation = Equation(user_input)
        expected = Equation(expected_output)
        actual = self.calc.find_workstations(equation)

        self.assertEqual(expected, actual)


class ValidatorTest(unittest.TestCase):
    def setUp(self) -> None:
        """Create a calculator before any test method."""

        self.calculator = Calculator()
        file = JsonSystem(JsonSystemTest.filename)
        file.read(self.calculator)

    def test_validate_value_calculation_negative_recipes(self):
        equation = Equation("100 stone - 100 wood")
        expected = "ValueError: 100 stone"

        with self.assertRaises(ValueError) as err:
            self.calculator.validator.validate_value_calculation(equation)
        self.assertEqual(expected, str(err.exception))

    def test_validate_value_calculation_optional_recipe(self):
        """Optional recipe is valid input should not raise an error."""

        e1 = Equation("1 concrete_mix")
        self.calculator.validator.validate_value_calculation(e1)


class EquationTreeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.calculator = Calculator()
        filesystem = FileSystem(FileSystemTest.filename)
        filesystem.read(self.calculator)

    def test_equation_tree(self):
        e1 = EquationTree(Resource("1 crafting_bench"))
        e2 = EquationTree(Resource("60 fiber"))
        e3 = EquationTree(Resource("50 wood"))
        e4 = EquationTree(Resource("12 stone"))
        e5 = EquationTree(Resource("20 leather"))

        e6 = EquationTree(Resource("1 anvil_bench"))
        e7 = EquationTree(Resource("40 iron_ingot"))
        e8 = EquationTree(Resource("80 iron_ore"))
        e9 = EquationTree(Resource("20 wood"))
        e10 = EquationTree(Resource("10 stone"))

        root = EquationTree()
        root.children = [e1, e6]

        e1.children = [e2, e3, e4, e5]
        e6.children = [e7, e9, e10]
        e7.children = [e8]

        actual = [str(r) for r in root]
        expected = [
            "1 crafting_bench",
            "60 fiber",
            "50 wood",
            "12 stone",
            "20 leather",
            "1 anvil_bench",
            "40 iron_ingot",
            "80 iron_ore",
            "20 wood",
            "10 stone",
        ]

        self.assertEqual(expected, actual)

    def test_calculate_recursive(self):
        e1 = Equation("1 crafting_bench + 1 anvil_bench")
        expected = [
            "1 crafting_bench",
            "60 fiber",
            "50 wood",
            "12 stone",
            "20 leather",
            "1 anvil_bench",
            "40 iron_ingot",
            "80 iron_ore",
            "20 wood",
            "10 stone",
        ]

        actual = list(self.calculator.calculate_recursive(e1))
        actual = [str(r) for r in actual]
        self.assertEqual(expected, actual)

    def test_calculate_recursive_subtract_negative(self):
        """Tree data structure should have valid quantities."""

        # TODO: laske epoxyt puun eri haarassa vahennyslaskun takia
        e1 = Equation("1 machining_bench - 10 epoxy")
        e2 = Equation("1 machining_bench - 12 epoxy")
        e3 = Equation("1 machining_bench - 8 epoxy")
        e4 = Equation("2 machining_bench - 10 epoxy")
        e5 = Equation("2 machining_bench - 12 epoxy")

        a1 = list(self.calculator.calculate_recursive(e1))
        a2 = list(self.calculator.calculate_recursive(e2))
        a3 = list(self.calculator.calculate_recursive(e3))
        a4 = list(self.calculator.calculate_recursive(e4))
        a5 = list(self.calculator.calculate_recursive(e5))

        self.assertEqual(a1, a2)
        self.assertNotEqual(a4, a5)

        expected_1 = [
            "1 machining_bench",
            "20 wood",
            "12 stone",
            "120 iron_nail",
            "12 iron_ingot",
            "24 iron_ore",
            "40 iron_ingot",
            "80 iron_ore",
            "24 rope",
            "288 fiber",
        ]

        expected_3 = [
            "1 machining_bench",
            "20 wood",
            "12 stone",
            "120 iron_nail",
            "12 iron_ingot",
            "24 iron_ore",
            "40 iron_ingot",
            "80 iron_ore",
            "2 epoxy",
            "4 sulfur",
            "8 tree_sap",
            "32 stick",
            "4 wood",
            "24 rope",
            "288 fiber",
        ]

        expected_4 = [
            "2 machining_bench",
            "40 wood",
            "24 stone",
            "240 iron_nail",
            "24 iron_ingot",
            "48 iron_ore",
            "80 iron_ingot",
            "160 iron_ore",
            "10 epoxy",
            "20 sulfur",
            "40 tree_sap",
            "160 stick",
            "16 wood",
            "48 rope",
            "576 fiber",
        ]

        self.assertEqual(expected_1, [str(r) for r in a1])
        self.assertEqual(expected_3, [str(r) for r in a3])
        self.assertEqual(expected_4, [str(r) for r in a4])

    def test_calculate_recursive_same_quantity(self):
        e1 = Equation("1 machining_bench")
        e2 = Equation("1 machining_bench + 0 epoxy")
        e3 = Equation("2 machining_bench")
        e4 = Equation("1 machining_bench + 1 machining_bench")
        e5 = Equation("1 machining_bench + 2 epoxy")
        e6 = Equation("1 machining_bench + 12 epoxy - 10 epoxy")
        e7 = Equation("-2 epoxy")
        e8 = Equation("10 epoxy - 12 epoxy")

        a1 = list(self.calculator.calculate_recursive(e1))
        a2 = list(self.calculator.calculate_recursive(e2))
        a3 = list(self.calculator.calculate_recursive(e3))
        a4 = list(self.calculator.calculate_recursive(e4))
        a5 = list(self.calculator.calculate_recursive(e5))
        a6 = list(self.calculator.calculate_recursive(e6))
        a7 = list(self.calculator.calculate_recursive(e7))
        a8 = list(self.calculator.calculate_recursive(e8))

        self.assertEqual(a1, a2)
        self.assertEqual(a3, a4)
        self.assertEqual(a5, a6)
        self.assertEqual(a7, a8)

    def test_calculate_recursive_crafting_order(self):
        e1 = Equation("1 biofuel_generator + 1 biofuel_extractor")
        a1 = self.calculator.calculate_recursive(e1)

        self.assertEqual("1 biofuel_extractor", str(a1.children[0].data))
        self.assertEqual("1 biofuel_generator", str(a1.children[1].data))

    def test_arrange_resources(self):
        # test_biofuel_extractor_biofuel_generator
        e1 = Equation("1 biofuel_generator + 1 biofuel_extractor")
        a1 = "1 biofuel_extractor + 1 biofuel_generator"

        # test_stone_furnace_anvil_bench_machining_bench.txt
        e2 = Equation("1 machining_bench + 1 stone_furnace + 1 anvil_bench")
        a2 = "1 stone_furnace + 1 anvil_bench + 1 machining_bench"

        # test_cement_mixer_concrete_furnace_thermos.txt
        e3 = Equation("3 concrete_furnace + 1 thermos + 2 cement_mixer")
        a3 = "2 cement_mixer + 3 concrete_furnace + 1 thermos"

        self.assertEqual(a1, str(self.calculator.arrange_resources(e1)))
        self.assertEqual(a2, str(self.calculator.arrange_resources(e2)))
        self.assertEqual(a3, str(self.calculator.arrange_resources(e3)))


if __name__ == "__main__":
    unittest.main()
