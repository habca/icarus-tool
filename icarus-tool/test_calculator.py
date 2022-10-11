from fractions import Fraction
from collections import deque
from application import FileSystem, JsonSystem
from calculator import Calculator, Equation, Resource, EquationTree
from test_application import FileSystemTest, JsonSystemTest

import unittest


class ResourceTest(unittest.TestCase):
    def test_to_string(self):
        r1 = Resource(1, "anvil_bench")
        r2 = Resource(10, "iron_ingot")

        self.assertEqual("1 anvil_bench", str(r1))
        self.assertEqual("10 iron_ingot", str(r2))

    def test_parse(self):
        r1 = Resource.parse("1 anvil_bench")
        r2 = Resource.parse("10 iron_ingot")

        self.assertEqual("1 anvil_bench", str(r1))
        self.assertEqual("10 iron_ingot", str(r2))

    def test_parse_negative(self):
        r1 = Resource.parse("-1 anvil_bench")
        r2 = Resource.parse("-10 iron_ingot")

        self.assertEqual("-1 anvil_bench", str(r1))
        self.assertEqual("-10 iron_ingot", str(r2))

    def test_equals(self):
        r1 = Resource(2, "biofuel_extractor")
        r2 = Resource(2, "biofuel_extractor")
        r3 = Resource(2, "biofuel_generator")
        r4 = Resource(4, "biofuel_generator")

        self.assertEqual(r1, r2)
        self.assertNotEqual(r2, r3)

        self.assertTrue(r1 == r2 != r3 != r4)
        self.assertFalse(r1 != r2 == r3 == r4)


class EquationTest(unittest.TestCase):
    def test_to_string(self):
        e1 = Equation([Resource(12, "fiber")])
        e2 = Equation([Resource(12, "fiber"), Resource(18, "stick")])

        self.assertEqual("12 fiber", str(e1))
        self.assertEqual("12 fiber + 18 stick", str(e2))

    def test_parse(self):
        e1 = Equation.parse("12 fiber + 18 stick")
        e2 = Equation.parse("1 wood")

        self.assertEqual("12 fiber + 18 stick", str(e1))
        self.assertEqual("1 wood", str(e2))

    def test_parse_negative(self):
        e1 = Equation.parse("-12 fiber - -18 stick")
        e2 = Equation.parse("-12 fiber - 18 stick")
        e3 = Equation.parse("-1 wood")

        self.assertEqual("-12 fiber + 18 stick", str(e1))
        self.assertEqual("-12 fiber - 18 stick", str(e2))
        self.assertEqual("-1 wood", str(e3))

    def test_equals(self):
        r1 = Resource(2, "biofuel_generator")
        r2 = Resource(4, "biofuel_generator")
        r3 = Resource(2, "biofuel_extractor")
        r4 = Resource(2, "biofuel_extractor")

        e1 = Equation([r1, r2, r3, r4])
        e2 = Equation([r1, r2, r3, r4])

        e3 = Equation([r4, r3, r2, r1])
        e4 = Equation([r1, r3, r2, r4])

        e5 = Equation([r1, r2, r3])
        e6 = Equation([r2, r3, r4])

        self.assertEqual(e1, e2)
        self.assertNotEqual(e2, e3)

        self.assertTrue(e1 == e2 != e3 != e4 != e5 != e6)
        self.assertFalse(e1 != e2 == e3 == e4 == e5 == e6)

    def test_evaluate_ceil(self):
        """
        Equation should round up fractions.

        > 124/5 wood + 160 stone + 0/24 leather
        = 25 wood + 160 stone + 0 leather

        > 1/3 wood + 0 stone + 1/3 wood
        = 1 wood + 0 stone
        """

        r1 = Resource(Fraction(124, 5), "wood")
        r2 = Resource(Fraction(160), "stone")
        r3 = Resource(Fraction(0, 24), "leather")

        e1 = Equation([r1, r2, r3]).evaluate()

        self.assertEqual("25 wood + 160 stone + 0 leather", str(e1))

        r1 = Resource(Fraction(1, 3), "wood")
        r2 = Resource(Fraction(0), "stone")
        r3 = Resource(Fraction(1, 3), "wood")

        e1 = Equation([r1, r2, r3]).evaluate()

        self.assertEqual("1 wood + 0 stone", str(e1))

    def test_evaluate_sum(self):
        """
        Equation should sum resources of same name.

        > 10 gold_ore + 30 copper_ore + 10 wood + 10 oxite + 20 sulfur + 16 wood
        = 10 gold_ore + 30 copper_ore + 26 wood + 10 oxite + 20 sulfur
        """

        r1 = Resource(Fraction(10), "gold_ore")
        r2 = Resource(Fraction(30), "copper_ore")
        r3 = Resource(Fraction(10), "wood")
        r4 = Resource(Fraction(10), "oxite")
        r5 = Resource(Fraction(20), "sulfur")
        r6 = Resource(Fraction(16), "wood")

        e1 = Equation([r1, r2, r3, r4, r5, r6]).evaluate()

        self.assertEqual(5, len(e1.resources))

        iterator = iter(e1)

        self.assertEqual("10 gold_ore", str(next(iterator)))
        self.assertEqual("30 copper_ore", str(next(iterator)))
        self.assertEqual("26 wood", str(next(iterator)))
        self.assertEqual("10 oxite", str(next(iterator)))
        self.assertEqual("20 sulfur", str(next(iterator)))

    def test_evaluate_subtract(self):
        """
        Equation should subtract negative amounts.

        > 1 wood - 2 wood + 0 stone + 0/2 sulfur
        = 0 wood + 0 stone + 0 sulfur
        """

        r1 = Resource(Fraction(1), "wood")
        r2 = Resource(Fraction(-2), "wood")
        r3 = Resource(Fraction(-2), "stone")
        r4 = Resource(Fraction(-3, 2), "sulfur")

        e1 = Equation([r1, r2, r3, r4]).evaluate()

        self.assertEqual("-1 wood - 2 stone - 1 sulfur", str(e1))

    def test_sort_resources(self):
        """Sort by an amount then by a name."""
        r1 = Resource(Fraction(10), "gold_ore")
        r2 = Resource(Fraction(30), "copper_ore")
        r3 = Resource(Fraction(26), "wood")
        r4 = Resource(Fraction(10), "oxite")
        r5 = Resource(Fraction(26), "sulfur")

        e1 = Equation([r1, r2, r3, r4, r5])
        e2 = Equation([r2, r5, r3, r1, r4])

        self.assertEqual(str(e2), str(e1.sort_resources()))
        self.assertEqual(str(e2), str(e2.sort_resources()))

    def test_format_resources(self):
        r1 = Resource(10, "copper_ingot")
        r2 = Resource(2, "iron_ingot")
        r3 = Resource(100, "gold_ore")
        r4 = Resource(10, "aluminium_ingot")

        l1 = Equation([r1, r2, r3, r4]).format_resources()

        iterator = iter(l1)

        self.assertEqual("100 gold_ore", next(iterator))
        self.assertEqual(" 10 aluminium_ingot", next(iterator))
        self.assertEqual(" 10 copper_ingot", next(iterator))
        self.assertEqual("  2 iron_ingot", next(iterator))
        self.assertRaises(StopIteration, next, iterator)

    def test_suodata(self):
        equation = Equation.parse("-1 stone + 1 wood - 12 wood")

        expected = Equation.parse("1 wood")
        self.assertEqual(expected, equation.suodata(all=False, round=False))

        expected = Equation.parse("-1 stone + 1 wood - 12 wood")
        self.assertEqual(expected, equation.suodata(all=True, round=False))

        expected = Equation.parse("0 stone + 1 wood + 0 wood")
        self.assertEqual(expected, equation.suodata(all=True, round=True))


class CalculatorTest(unittest.TestCase):
    def setUp(self) -> None:
        """Create a calculator before any test method."""
        self.calc = Calculator()
        file = FileSystem(FileSystemTest.filename)
        file.read(self.calc)

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
        e1 = Equation.parse("1 rifle_hunting")
        e2 = Equation.parse(
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
        e1 = Equation.parse("1 epoxy + 1 epoxy + 1 rope + 1 rope")
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

        self.assertIn("0 stone", self.get_last_element(e2))
        self.assertIn("0 wood", self.get_last_element(e2))

        self.assertIn("2 stone", self.get_last_element(e3))
        self.assertIn("-1 wood", self.get_last_element(e3))

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

    def test_calculate_2nd(self):
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
        self.assertEqual(e1, list(self.calc.calculate_2nd("3 electric_extractor")))

    def test_find_similar(self):
        """There may be none, one or many good enough matches."""
        calc = self.calc

        e1 = Equation([Resource(1, "anvil")])
        e2 = Equation([Resource(1, "anvil_bvve")])
        e3 = Equation([Resource(1, "anvil_benchs")])
        e4 = Equation([Resource(1, "anvi")])

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

        e1 = Equation.parse("1 machining_bench - 10 epoxy")
        words = list(self.calculator.find_similar(e1))
        self.assertEquals(["machining_bench"], words)

    def test_order_by_station(self):
        r1 = Resource(Fraction(1), "biofuel_extractor")
        r2 = Resource(Fraction(1), "biofuel_generator")

        self.assertEqual("fabricator", self.calc.order_by_station([r1, r2]))

    def test_order_by_station_revisit_workbench(self):
        """
        Some resources require more than one visit to the workbench.

        Problem:
        - concrete_furnace: carbon_fiber
        - mortar_and_pestle: carbon_paste
        - concrete_furnace: aluminium_ingot
        """
        r1 = Resource(Fraction(8), "carbon_fiber")
        r2 = Resource(Fraction(1), "steel_ingot")

        self.assertEqual("concrete_furnace", self.calc.order_by_station([r1, r2]))

    def test_get_station_value(self):
        self.assertEqual(1, self.calc.get_station_value("character_crafting"))
        self.assertEqual(2, self.calc.get_station_value("crafting_bench"))
        self.assertEqual(3, self.calc.get_station_value("machining_bench"))
        self.assertEqual(4, self.calc.get_station_value("fabricator"))
        self.assertEqual(3, self.calc.get_station_value("mortar_and_pestle"))
        self.assertEqual(4, self.calc.get_station_value("concrete_furnace"))

    def test_suodata_practical_1(self):
        equation = Equation.parse("1 biofuel_extractor + 1 biofuel_generator")
        expected = Equation([Resource(Fraction(1), "biofuel_generator")])
        self.assertEqual(expected, self.calc.suodata(equation))

    def test_suodata_practical_2(self):
        equation = Equation.parse("1 cement_mixer + 1 concrete_furnace")
        expected = Equation([Resource(Fraction(1), "concrete_furnace")])
        self.assertEqual(expected, self.calc.suodata(equation))

    def test_suodata_practical_3(self):
        equation = Equation.parse("1 stone_furnace + 1 anvil_bench + 1 machining_bench")
        expected = Equation([Resource(Fraction(1), "machining_bench")])
        self.assertEqual(expected, self.calc.suodata(equation))

    def test_suodata_practical_4(self):
        equation = Equation.parse(
            "1 anvil_bench + 1 machining_bench + 1 cement_mixer + 1 concrete_furnace + 1 fabricator"
        )
        expected = Equation([Resource(Fraction(1), "fabricator")])
        self.assertEqual(expected, self.calc.suodata(equation))

    def test_suodata_raw_materials(self):
        equation = Equation.parse("1 iron_ore + 1 wood")
        expected = equation.make_copy()
        self.assertEqual(expected, self.calc.suodata(equation))

    def test_suodata_does_not_change_parameter(self):
        equation = Equation.parse("1 anvil_bench + 1 anvil_bench")
        expected = equation.make_copy()
        self.assertEqual(expected, self.calc.suodata(equation))

    def test_korvaa_1(self):
        calc = self.calc

        e1 = Equation.parse("1 biofuel_extractor + 1 biofuel_generator")
        e2 = Equation.parse("1 biofuel_generator")
        e3 = Equation.parse(
            "1 biofuel_extractor + 20 steel_ingot + 8 copper_ingot + 12 electronics + 20 steel_screw + 2 glass"
        )

        self.assertEqual(e3, calc.korvaa(e1, e2))

        e1 = Equation.parse("1 biofuel_extractor + 2 biofuel_generator")
        e2 = Equation.parse("2 biofuel_generator")
        e3 = Equation.parse(
            "1 biofuel_extractor + 40 steel_ingot + 16 copper_ingot + 24 electronics + 40 steel_screw + 4 glass"
        )

        self.assertEqual(e3, calc.korvaa(e1, e2))

    def test_korvaa_2(self):
        calc = self.calc

        e1 = Equation.parse("40 iron_ingot + 20 wood + 10 stone")
        e2 = Equation.parse("40 iron_ingot")
        e3 = Equation.parse("80 iron_ore + 20 wood + 10 stone")

        self.assertEqual(e3, calc.korvaa(e1, e2))

    def test_korvaa_3(self):
        calc = self.calc

        r1 = Equation([Resource(Fraction(2), "hunting_rifle")])
        r2 = Equation([Resource(Fraction(16), "steel_screw")])
        r3 = Equation([Resource(Fraction(10), "stick")])

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

        calc = self.calc

        e1 = Equation([Resource(Fraction(1), "biofuel_generator")])

        r1 = Resource(Fraction(20), "steel_ingot")
        r2 = Resource(Fraction(8), "copper_ingot")
        r3 = Resource(Fraction(12), "electronics")
        r4 = Resource(Fraction(20), "steel_screw")
        r5 = Resource(Fraction(2), "glass")

        expected = Equation([r1, r2, r3, r4, r5])

        self.assertEqual(expected, calc.resources_per_station(e1))

    def test_resources_per_station_raw_materials(self):
        """
        Return the original equation since raw materials don't have any recipes.
        > 40 iron_ore + 245 fiber = 40 iron_ore + 245 fiber
        """

        calc = self.calc

        r1 = Resource(Fraction(40), "iron_ore")
        r2 = Resource(Fraction(245), "fiber")

        e1 = Equation([r1, r2])

        expected = e1.make_copy()

        self.assertEqual(expected, calc.resources_per_station(e1))

    def test_resources_per_station_multiple_stations(self):
        """
        Returns a material cost of an equation.
        Equation may have recipes for multiple stations.
        """
        calc = self.calc

        e1 = Equation.parse("1 biofuel_generator + 40 iron_ore + 245 fiber")

        r1 = Resource(Fraction(20), "steel_ingot")
        r2 = Resource(Fraction(8), "copper_ingot")
        r3 = Resource(Fraction(12), "electronics")
        r4 = Resource(Fraction(20), "steel_screw")
        r5 = Resource(Fraction(2), "glass")
        r6 = Resource(Fraction(40), "iron_ore")
        r7 = Resource(Fraction(245), "fiber")

        expected = Equation([r1, r2, r3, r4, r5, r6, r7])

        self.assertEqual(expected, calc.resources_per_station(e1))

    def test_get_station(self):
        """Returns a name of station where items can be crafted."""
        calc = self.calc

        e1 = Equation.parse("1 biofuel_generator")
        e2 = Equation.parse("40 iron_ore + 245 fiber")

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

        e1 = Equation.parse("1 biofuel_generator + 1 iron_ore")
        with self.assertRaises(AssertionError) as err:
            calc.get_station(e1)
        self.assertEqual(
            "Multiple stations: fabricator, total_resources", str(err.exception)
        )

    def get_first_element(self, equation: str) -> str:
        return str(next(self.calc.calculate(Equation.parse(equation))))

    def get_last_element(self, equation: str) -> str:
        gen = self.calc.calculate(Equation.parse(equation))
        return str(deque(gen, maxlen=1).pop())


class ValidatorTest(unittest.TestCase):
    def setUp(self) -> None:
        """Create a calculator before any test method."""

        self.calculator = Calculator()
        file = JsonSystem(JsonSystemTest.filename)
        file.read(self.calculator)

    def test_validate_value_calculation_negative_recipes(self):
        equation = Equation.parse("100 stone - 100 wood")
        expected = "ValueError: 100 stone"

        with self.assertRaises(ValueError) as err:
            self.calculator.validator.validate_value_calculation(equation)
        self.assertEqual(expected, str(err.exception))

    def test_validate_value_calculation_optional_recipe(self):
        """Optional recipe is valid input should not raise an error."""

        e1 = Equation.parse("1 concrete_mix")
        self.calculator.validator.validate_value_calculation(e1)


class EquationTreeTest(unittest.TestCase):
    def test_equation_tree(self):
        e1 = EquationTree(Resource.parse("1 crafting_bench"))
        e2 = EquationTree(Resource.parse("60 fiber"))
        e3 = EquationTree(Resource.parse("50 wood"))
        e4 = EquationTree(Resource.parse("12 stone"))
        e5 = EquationTree(Resource.parse("20 leather"))

        e6 = EquationTree(Resource.parse("1 anvil_bench"))
        e7 = EquationTree(Resource.parse("40 iron_ingot"))
        e8 = EquationTree(Resource.parse("80 iron_ore"))
        e9 = EquationTree(Resource.parse("20 wood"))
        e10 = EquationTree(Resource.parse("10 stone"))

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
        filesystem = FileSystem(FileSystemTest.filename)
        filesystem.read(calculator := Calculator())

        e1 = Equation.parse("1 crafting_bench + 1 anvil_bench")
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

        actual = list(calculator.calculate_recursive(e1))
        actual = [str(r) for r in actual]
        self.assertEqual(expected, actual)

    def test_calculate_recursive_ignore_negative(self):
        """Tree data structure should have only positive numbers."""

        filesystem = FileSystem(FileSystemTest.filename)
        filesystem.read(calculator := Calculator())

        e1 = Equation.parse("1 machining_bench - 10 epoxy")
        e2 = Equation.parse("1 machining_bench + 0 epoxy")
        e3 = Equation.parse("1 machining_bench")

        a1 = list(calculator.calculate_recursive(e1))
        a2 = list(calculator.calculate_recursive(e2))
        a3 = list(calculator.calculate_recursive(e3))

        self.assertEqual(a1, a2)
        self.assertEqual(a1, a3)


if __name__ == "__main__":
    unittest.main()
