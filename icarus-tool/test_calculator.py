from fractions import Fraction
from application import FileSystem
from calculator import Calculator, Equation, Resource

import unittest

class ResourceTest(unittest.TestCase):
    def test_str(self):
        r1 = Resource(1, "anvil_bench")
        r2 = Resource(10, "iron_ingot")

        self.assertEqual("1 anvil_bench", str(r1))
        self.assertEqual("10 iron_ingot", str(r2))

    def test_parse1(self):
        r1 = Resource.parse("1 anvil_bench")
        r2 = Resource.parse("10 iron_ingot")

        self.assertEqual("1 anvil_bench", str(r1))
        self.assertEqual("10 iron_ingot", str(r2))

class EquationTest(unittest.TestCase):
    def test_str(self):
        e1 = Equation([Resource(12, "fiber")])
        e2 = Equation([Resource(12, "fiber"), Resource(18, "stick")])

        self.assertEqual("12 fiber", str(e1))
        self.assertEqual("12 fiber + 18 stick", str(e2))

    def test_parse(self):
        e1 = Equation.parse("12 fiber + 18 stick")
        e2 = Equation.parse("1 wood")

        self.assertEqual("12 fiber + 18 stick", str(e1))
        self.assertEqual("1 wood", str(e2))

    def test_evaluate(self):
        r1 = Resource(Fraction(124/5), "wood")
        r2 = Resource(Fraction(160), "stone")
        r3 = Resource(Fraction(24), "leather")

        e1 = Equation([r1, r2, r3]).evaluate()

        self.assertEqual("25 wood + 160 stone + 24 leather", str(e1))

        r1 = Resource(Fraction(1, 3), "wood")
        r2 = Resource(Fraction(160), "stone")
        r3 = Resource(Fraction(1, 3), "wood")

        e1 = Equation([r1, r2, r3]).evaluate()

        self.assertEqual("1 wood + 160 stone", str(e1))

    def test_evaluate2(self):
        """ Equation should sum resources of same name. """

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

class CalculatorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.calc = Calculator()
        file = FileSystem("tech_tree.txt")
        file.read(self.calc)

    def test_get_keywords(self):
        calc = Calculator()

        self.assertEqual([], calc.get_keywords())

        calc.assign_equation("1 wood_spear = 12 fiber + 18 stick")
        calc.assign_equation("10 stick = 1 wood")

        self.assertEquals(["wood_spear", "stick"], calc.get_keywords())

    def test_assign_equation1(self):
        calc = Calculator()

        calc.assign_equation("1 wood_spear = 12 fiber + 18 stick")
        calc.assign_equation("10 stick = 1 wood")
        calc.assign_equation("1 steel_screw = 1/100 steel_ingot")

        e1 = calc.resources["wood_spear"]
        e2 = calc.resources["stick"]
        e3 = calc.resources["steel_screw"]

        self.assertEqual("12 fiber + 18 stick", str(e1))
        self.assertEqual("1/10 wood", str(e2))
        self.assertEqual("1/100 steel_ingot", str(e3))

    def test_assign_equation2(self):
        calc = Calculator()

        calc.assign_equation("1 rope = 12 fiber")
        with self.assertRaises(ValueError) as err1:
            calc.assign_equation("1 rope = 12 fiber")
        with self.assertRaises(ValueError) as err2:
            calc.assign_equation("1 rope = 5 leather")

        self.assertEqual("Name is already in use: rope", str(err1.exception))
        self.assertEqual("Name is already in use: rope", str(err2.exception))

    def test_assign_equation3(self):
        calc = self.calc

        resources = list(calc.resources)
        variables = list(calc.variables)

        for resource in resources:
            self.assertEqual(1, resources.count(resource))
            self.assertFalse(resource in variables)
        for variable in variables:
            self.assertEqual(1, variables.count(variable))
            self.assertFalse(variable in resources)

    def test_assign_equation4(self):
        calc = Calculator()

        error_input = [
            "1 lightning_rod = 10 copper ingot",
            "1 lightning rod = 10 copper_ingot",
            "lightning_rod = 10 copper_ingot",
            "1 lightning_rod = copper_ingot",
            "1 1 lightning_rod = 10 copper_ingot",
            "1 lightning_rod = 10 10 copper_ingot",
            "1 lightning_rod = 10 copper_ingot +",
            "1 lightning_rod = + 10 copper_ingot",
            "1 lightning_rod 10 copper_ingot",
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

        e1 = calc.replace_variables(Equation([r1]))
        e2 = calc.replace_variables(Equation([r2]))
        e3 = calc.replace_variables(Equation([r3]))

        self.assertEqual("24 wood + 16 leather + 80 titanium_ingot + 8 epoxy + 32 steel_screw", str(e1))
        self.assertEqual("4/25 steel_ingot", str(e2))
        self.assertEqual("1 wood", str(e3))

    def test_search_variable(self):
        calc = Calculator()

        calc.assign_equation("1 hunting_rifle = 12 wood + 8 leather + 40 titanium_ingot + 4 epoxy + 16 steel_screw")
        calc.assign_equation("100 steel_screw = 1 steel_ingot")
        calc.assign_equation("1 steel_ingot = 1 steel_bloom")
        calc.assign_equation("1 steel_bloom = 6 iron_ore + 1 coal_ore")

        l1 = calc.resources["hunting_rifle"]
        l2 = calc.resources["steel_ingot"]
        l3 = calc.resources["steel_bloom"]

        self.assertEqual(["steel_screw"], calc.search_variable("iron_ore", l1))
        self.assertEqual(["steel_bloom"], calc.search_variable("iron_ore", l2))
        self.assertEqual([], calc.search_variable("iron_ore", l3))

    def test_calculate1(self):
        """ Comprehensive test for the crafting cost of the electric extractor. """
        calc = self.calc

        iron_ingot1 = "40 iron_ore"

        self.assertEqual(str(calc.calculate("40 iron_ore")[-1]), str(calc.calculate(iron_ingot1)[-1]))
        self.assertEqual(str(calc.calculate("40 iron_ore")[-1]), str(iron_ingot1))

        electronics1 = "5 refined_gold + 15 copper_ingot + 10 organic_resin + 10 epoxy"
        electronics2 = "10 gold_ore + 30 copper_ore + 10 wood + 10 oxite + 20 sulfur + 40 tree_sap"
        electronics3 = "10 gold_ore + 30 copper_ore + 10 wood + 10 oxite + 20 sulfur + 160 stick"
        electronics4 = "10 gold_ore + 30 copper_ore + 26 wood + 10 oxite + 20 sulfur"

        self.assertEqual(str(calc.calculate("5 electronics")[-1]), str(calc.calculate(electronics1)[-1]))
        self.assertEqual(str(calc.calculate("5 electronics")[-1]), str(calc.calculate(electronics2)[-1]))
        self.assertEqual(str(calc.calculate("5 electronics")[-1]), str(calc.calculate(electronics3)[-1]))
        self.assertEqual(str(calc.calculate("5 electronics")[-1]), str(calc.calculate(electronics4)[-1]))
        self.assertEqual(str(calc.calculate("5 electronics")[-1]), str(electronics4))
        
        electric_extractor1 = "60 iron_ingot + 15 electronics"
        electric_extractor2 = "120 iron_ore + 30 gold_ore + 90 copper_ore + 78 wood + 30 oxite + 60 sulfur"

        self.assertEqual(str(calc.calculate("3 electric_extractor")[-1]), str(calc.calculate(electric_extractor1)[-1]))
        self.assertEqual(str(calc.calculate("3 electric_extractor")[-1]), str(calc.calculate(electric_extractor2)[-1]))
        self.assertEqual(str(calc.calculate("3 electric_extractor")[-1]), str(electric_extractor2))

    def test_calculate2(self):
        """ Comprehensive test for the crafting cost of the hunting rifle. """
        calc = self.calc

        titanium_ingot1 = "200 titanium_ore"

        self.assertEqual(str(calc.calculate("40 titanium_ingot")[-1]), str(calc.calculate(titanium_ingot1)[-1]))
        self.assertEqual(str(calc.calculate("40 titanium_ingot")[-1]), titanium_ingot1)

        epoxy_1 = "8 sulfur + 16 tree_sap"
        epoxy_2 = "8 sulfur + 64 stick"
        epoxy_3 = "8 sulfur + 7 wood"

        self.assertEqual(str(calc.calculate("4 epoxy")[-1]), str(calc.calculate(epoxy_1)[-1]))
        self.assertEqual(str(calc.calculate("4 epoxy")[-1]), str(calc.calculate(epoxy_2)[-1]))
        self.assertEqual(str(calc.calculate("4 epoxy")[-1]), str(calc.calculate(epoxy_3)[-1]))
        self.assertEqual(str(calc.calculate("4 epoxy")[-1]), str(epoxy_3))

        steel_screw1 = "1 steel_ingot"
        steel_screw2 = "6 iron_ore + 1 coal_ore"

        self.assertEqual(str(calc.calculate("16 steel_screw")[-1]), str(calc.calculate(steel_screw1)[-1]))
        self.assertEqual(str(calc.calculate("16 steel_screw")[-1]), str(calc.calculate(steel_screw2)[-1]))
        self.assertEqual(str(calc.calculate("16 steel_screw")[-1]), str(steel_screw2))

        hunting_rifle1 = "12 wood + 8 leather + 40 titanium_ingot + 4 epoxy + 16 steel_screw"
        hunting_rifle2 = "19 wood + 8 leather + 200 titanium_ore + 8 sulfur + 6 iron_ore + 1 coal_ore"

        self.assertEqual(str(calc.calculate("1 hunting_rifle")[-1]), str(calc.calculate(hunting_rifle1)[-1]))
        self.assertEqual(str(calc.calculate("1 hunting_rifle")[-1]), str(calc.calculate(hunting_rifle2)[-1]))
        self.assertEqual(str(calc.calculate("1 hunting_rifle")[-1]), str(hunting_rifle2))

    def test_find_similar(self):
        """
        There may be none, one or many good enough matches.
        The dictionary omits searches that have no matches.
        """
        calc = self.calc
        self.assertEqual(["anvil_bench"], calc.find_similar("anvil")["anvil"])
        self.assertEqual(["anvil_bench"], calc.find_similar("anvil_bvve")["anvil_bvve"])
        self.assertIn("anvil_bench", calc.find_similar("anvil_benchs")["anvil_benchs"])
        with self.assertRaises(KeyError):
            calc.find_similar("anvi")["anvi"]

if __name__ == "__main__":
    unittest.main()
