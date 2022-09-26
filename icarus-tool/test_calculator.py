from fractions import Fraction
from application import FileSystem
from calculator import Calculator, Equation, Resource
from test_application import FileSystemTest

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

    def test_evaluate_1(self):
        r1 = Resource(Fraction(124 / 5), "wood")
        r2 = Resource(Fraction(160), "stone")
        r3 = Resource(Fraction(24), "leather")

        e1 = Equation([r1, r2, r3]).evaluate()

        self.assertEqual("25 wood + 160 stone + 24 leather", str(e1))

        r1 = Resource(Fraction(1, 3), "wood")
        r2 = Resource(Fraction(160), "stone")
        r3 = Resource(Fraction(1, 3), "wood")

        e1 = Equation([r1, r2, r3]).evaluate()

        self.assertEqual("1 wood + 160 stone", str(e1))

    def test_evaluate_2(self):
        """Equation should sum resources of same name."""
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


class CalculatorTest(unittest.TestCase):
    def setUp(self) -> None:
        """Create a calculator before any test method."""
        self.calc = Calculator()
        file = FileSystem(FileSystemTest.filename)
        file.read(self.calc)

    def test_get_keywords(self):
        """Keywords consit of assigned variable names."""
        calc = Calculator()

        self.assertEqual([], calc.get_keywords())

        calc.assign_equation("character : 1 wood_spear = 12 fiber + 18 stick")
        calc.assign_equation("character : 10 stick = 1 wood")

        self.assertEqual(["wood_spear", "stick"], calc.get_keywords())

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
        A duplicate equation should raise an exception.
        Resources or variables should not have duplicate entries.
        """
        calc = Calculator()

        calc.assign_equation("crafting_bench : 1 rope = 12 fiber")
        with self.assertRaises(ValueError) as err1:
            calc.assign_equation("crafting_bench : 1 rope = 12 fiber")
        with self.assertRaises(ValueError) as err2:
            calc.assign_equation("character : 1 rope = 5 leather")

        self.assertEqual("Name is already in use: rope", str(err1.exception))
        self.assertEqual("Name is already in use: rope", str(err2.exception))

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

    def test_replace_variables(self):
        calc = self.calc

        r1 = Resource(Fraction(2), "hunting_rifle")
        r2 = Resource(Fraction(16), "steel_screw")
        r3 = Resource(Fraction(10), "stick")

        e1 = calc.substitute_variables(Equation([r1]))
        e2 = calc.substitute_variables(Equation([r2]))
        e3 = calc.substitute_variables(Equation([r3]))

        self.assertEqual(
            "24 wood + 16 leather + 80 titanium_ingot + 8 epoxy + 32 steel_screw",
            str(e1),
        )
        self.assertEqual("4/25 steel_ingot", str(e2))
        self.assertEqual("1 wood", str(e3))

    def test_search_variable(self):
        calc = self.calc

        l1 = calc.resources["hunting_rifle"]
        l2 = calc.resources["steel_ingot"]
        l3 = calc.resources["steel_bloom"]

        self.assertEqual(["steel_screw"], calc.search_variable("iron_ore", l1))
        self.assertEqual(["steel_bloom"], calc.search_variable("iron_ore", l2))
        self.assertEqual([], calc.search_variable("iron_ore", l3))

    def test_calculate_1(self):
        """The final form of an equation should contain known variables."""
        calc = self.calc

        e1 = Equation.parse("60 fiber + 50 wood + 12 stone + 20 leather")
        e2 = Equation.parse("80 iron_ore + 20 wood + 10 stone")
        e3 = Equation.parse("25 wood + 160 stone + 24 leather")
        e4 = Equation.parse("80 iron_ore")
        e5 = Equation.parse("1 wood")

        self.assertEqual(e1, calc.calculate("1 crafting_bench")[-1])
        self.assertEqual(e2, calc.calculate("1 anvil_bench")[-1])
        self.assertEqual(e3, calc.calculate("2 stone_furnace")[-1])
        self.assertEqual(e4, calc.calculate("40 iron_ingot")[-1])
        self.assertEqual(e5, calc.calculate("8 stick")[-1])

    def test_calculate_electric_extractor(self):
        """Crafting cost of an electric extractor."""
        calc = self.calc

        iron_ingot1 = Equation.parse("40 iron_ore")

        self.assertEqual(
            calc.calculate("40 iron_ore")[-1], calc.calculate(str(iron_ingot1))[-1]
        )
        self.assertEqual(calc.calculate("40 iron_ore")[-1], iron_ingot1)

        electronics1 = Equation.parse(
            "5 refined_gold + 15 copper_ingot + 10 organic_resin + 10 epoxy"
        )
        electronics2 = Equation.parse(
            "10 gold_ore + 30 copper_ore + 10 wood + 10 oxite + 20 sulfur + 40 tree_sap"
        )
        electronics3 = Equation.parse(
            "10 gold_ore + 30 copper_ore + 10 wood + 10 oxite + 20 sulfur + 160 stick"
        )
        electronics4 = Equation.parse(
            "10 gold_ore + 30 copper_ore + 26 wood + 10 oxite + 20 sulfur"
        )

        self.assertEqual(
            calc.calculate("5 electronics")[-1], calc.calculate(str(electronics1))[-1]
        )
        self.assertEqual(
            calc.calculate("5 electronics")[-1], calc.calculate(str(electronics2))[-1]
        )
        self.assertEqual(
            calc.calculate("5 electronics")[-1], calc.calculate(str(electronics3))[-1]
        )
        self.assertEqual(
            calc.calculate("5 electronics")[-1], calc.calculate(str(electronics4))[-1]
        )
        self.assertEqual(calc.calculate("5 electronics")[-1], electronics4)

        electric_extractor1 = Equation.parse("60 iron_ingot + 15 electronics")
        electric_extractor2 = Equation.parse(
            "120 iron_ore + 30 gold_ore + 90 copper_ore + 78 wood + 30 oxite + 60 sulfur"
        )

        self.assertEqual(
            calc.calculate("3 electric_extractor")[-1],
            calc.calculate(str(electric_extractor1))[-1],
        )
        self.assertEqual(
            calc.calculate("3 electric_extractor")[-1],
            calc.calculate(str(electric_extractor2))[-1],
        )
        self.assertEqual(
            calc.calculate("3 electric_extractor")[-1], electric_extractor2
        )

    def test_calculate_hunting_rifle(self):
        """Crafting cost of a hunting rifle."""
        calc = self.calc

        titanium_ingot1 = Equation.parse("200 titanium_ore")

        self.assertEqual(
            calc.calculate("40 titanium_ingot")[-1],
            calc.calculate(str(titanium_ingot1))[-1],
        )
        self.assertEqual(calc.calculate("40 titanium_ingot")[-1], titanium_ingot1)

        epoxy_1 = Equation.parse("8 sulfur + 16 tree_sap")
        epoxy_2 = Equation.parse("8 sulfur + 64 stick")
        epoxy_3 = Equation.parse("8 sulfur + 7 wood")

        self.assertEqual(
            calc.calculate("4 epoxy")[-1], calc.calculate(str(epoxy_1))[-1]
        )
        self.assertEqual(
            calc.calculate("4 epoxy")[-1], calc.calculate(str(epoxy_2))[-1]
        )
        self.assertEqual(
            calc.calculate("4 epoxy")[-1], calc.calculate(str(epoxy_3))[-1]
        )
        self.assertEqual(calc.calculate("4 epoxy")[-1], epoxy_3)

        steel_screw1 = Equation.parse("1 steel_ingot")
        steel_screw2 = Equation.parse("6 iron_ore + 1 coal_ore")

        self.assertEqual(
            calc.calculate("16 steel_screw")[-1], calc.calculate(str(steel_screw1))[-1]
        )
        self.assertEqual(
            calc.calculate("16 steel_screw")[-1], calc.calculate(str(steel_screw2))[-1]
        )
        self.assertEqual(calc.calculate("16 steel_screw")[-1], steel_screw2)

        hunting_rifle1 = Equation.parse(
            "12 wood + 8 leather + 40 titanium_ingot + 4 epoxy + 16 steel_screw"
        )
        hunting_rifle2 = Equation.parse(
            "19 wood + 8 leather + 200 titanium_ore + 8 sulfur + 6 iron_ore + 1 coal_ore"
        )

        self.assertEqual(
            calc.calculate("1 hunting_rifle")[-1],
            calc.calculate(str(hunting_rifle1))[-1],
        )
        self.assertEqual(
            calc.calculate("1 hunting_rifle")[-1],
            calc.calculate(str(hunting_rifle2))[-1],
        )
        self.assertEqual(calc.calculate("1 hunting_rifle")[-1], hunting_rifle2)

    def test_calculate_4(self):
        """
        More than one equation may have the same resource cost.
        Same amount of resources should have same crafting cost.
        """
        calc = self.calc

        self.assertEqual(
            calc.calculate("1 stone_axe")[-1], calc.calculate("1 stone_pickaxe")[-1]
        )

        anvil_bench1 = Equation.parse("1 anvil_bench + 1 anvil_bench")
        anvil_bench2 = Equation.parse("2 anvil_bench")

        self.assertEqual(
            calc.calculate(str(anvil_bench1))[-1], calc.calculate(str(anvil_bench2))[-1]
        )

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

    def test_group_by_station(self):
        calc = self.calc

        r1 = Resource(Fraction(20), "steel_ingot")
        r2 = Resource(Fraction(20), "steel_screw")

        e1 = Equation([r1, r2])

        groups = calc.group_by_station(e1)

        r3 = Resource(Fraction(21), "steel_ingot")
        r4 = Resource(Fraction(21), "steel_bloom")

        self.assertEqual(Equation([r2]), groups["machining_bench"])
        self.assertEqual(Equation([r3]), groups["concrete_furnace"])
        self.assertEqual(Equation([r4]), groups["mortar_and_pestle"])

    def test_resources_per_station_1(self):
        calc = self.calc

        e1 = Equation([Resource(Fraction(1), "biofuel_generator")])

        r1 = Resource(Fraction(20), "steel_ingot")
        r2 = Resource(Fraction(8), "copper_ingot")
        r3 = Resource(Fraction(12), "electronics")
        r4 = Resource(Fraction(20), "steel_screw")
        r5 = Resource(Fraction(2), "glass")

        expected = Equation([r1, r2, r3, r4, r5])

        self.assertEqual(expected, calc.resources_per_station(e1))

    def test_resources_per_station_2(self):
        """
        Return the original equation since the
        raw materials belong to the same group.
        """
        calc = self.calc

        r1 = Resource(Fraction(40), "iron_ore")
        r2 = Resource(Fraction(245), "fiber")

        e1 = Equation([r1, r2])

        self.assertEqual(e1, calc.resources_per_station(e1))

    def test_order_by_station(self):
        calc = self.calc

        e1 = Equation.parse("1 biofuel_extractor + 1 biofuel_generator")
        groups = calc.group_by_station(e1)

        expected = [
            "fabricator",
            "machining_bench",
            "concrete_furnace",
            "mortar_and_pestle",
            "character",
            "anvil_bench",
            "stone_furnace",
        ]

        self.assertEqual(expected, calc.order_by_station(groups))

    def test_order_by_station_revisit_workbench(self):
        """
        Some resources require more than one visit to the workbench.

        Problem:
        - concrete_furnace: carbon_fiber
        - mortar_and_pestle: carbon_paste
        - concrete_furnace: aluminium_ingot
        """
        calc = self.calc

        r1 = Resource(Fraction(8), "carbon_fiber")
        r2 = Resource(Fraction(1), "steel_ingot")
        e1 = Equation([r1, r2])

        grouped = calc.group_by_station(e1)
        ordered = calc.order_by_station(grouped)

        expected = ["concrete_furnace", "mortar_and_pestle", "character"]

        self.assertEqual(expected, ordered)

    def test_suodata(self):
        calc = self.calc

        e1 = Equation.parse("1 biofuel_extractor + 1 biofuel_generator")
        e2 = Equation.parse("1 iron_ore + 1 wood")

        r1 = Resource(Fraction(1), "biofuel_generator")

        self.assertEqual(str(r1), str(calc.suodata(e1)))
        self.assertEqual(e2, calc.suodata(e2))

    def test_suodata_does_not_change_parameter(self):
        calc = self.calc

        mjono = "1 anvil_bench + 1 anvil_bench"
        e1 = Equation.parse(mjono)

        calc.suodata(e1)

        self.assertEqual(mjono, str(e1))

    def test_korvaa(self):
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

    def test_get_station(self):
        calc = self.calc

        e1 = Equation.parse("1 biofuel_generator")
        e2 = Equation.parse("1 iron_ore")
        e3 = Equation([])

        self.assertEqual("fabricator", calc.get_station(e1))
        self.assertEqual("total_resources", calc.get_station(e2))
        with self.assertRaises(ValueError) as err:
            calc.get_station(e3)
        self.assertEqual("Equation was empty", str(err.exception))


if __name__ == "__main__":
    unittest.main()
