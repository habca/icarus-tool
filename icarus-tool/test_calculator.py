from fractions import Fraction
from application import FileSystem
from calculator import Calculator, Equation, Resource

import unittest

class ResourceTest(unittest.TestCase):
    # TODO voiko korvata tuplella
    def test_str(self):
        self.assertEqual("1 anvil_bench", str(Resource(1, "anvil_bench")))
        self.assertEqual("10 iron_ingot", str(Resource(10, "iron_ingot")))

class EquationTest(unittest.TestCase):
    def test_str(self):
        r1 = Resource(1, "wood_spear")
        r2 = Resource(12, "fiber")
        r3 = Resource(18, "stick")

        e1 = Equation(r1, [r2])
        e2 = Equation(r1, [r2, r3])

        self.assertEqual("1 wood_spear = 12 fiber", str(e1))
        self.assertEqual("1 wood_spear = 12 fiber + 18 stick", str(e2))

    def test_parse(self):
        e1 = Equation.parse("1 wood_spear = 12 fiber + 18 stick")
        e2 = Equation.parse("10 stick = 1 wood")
        e3 = Equation.parse("100 steel_screw = 1 steel_ingot")

        self.assertEqual("1 wood_spear = 12 fiber + 18 stick", str(e1))
        self.assertEqual("1 stick = 1/10 wood", str(e2))
        self.assertEqual("1 steel_screw = 1/100 steel_ingot", str(e3))

    def test_parse_list(self):
        r1, r2 = Equation.parse_list("12 fiber + 18 stick")

        self.assertEqual("fiber", r1.name)
        self.assertEqual(12, int(r1.amount))

        self.assertEqual("stick", r2.name)
        self.assertEqual(18, int(r2.amount))

class CalculatorTest(unittest.TestCase):
    filename = "tech_tree.txt"

    def setUp(self) -> None:
        # TODO mieti onko tarpeen lukea tiedostosta
        self.calc = Calculator()
        file = FileSystem(CalculatorTest.filename)
        file.read(self.calc)

    def test_get_keywords(self):
        calc = Calculator()

        calc.assign_equation("1 wood_spear = 12 fiber + 18 stick")
        calc.assign_equation("10 stick = 1 wood")
        calc.assign_equation("1 steel_screw = 1/100 steel_ingot")

        expected = ["wood_spear", "stick", "steel_screw"]
        
        self.assertIsInstance(calc.get_keywords(), list)
        self.assertTrue(type(calc.get_keywords()) is list)
        self.assertEquals(expected, calc.get_keywords())

    def test_assign_equation1(self):
        calc = Calculator()

        calc.assign_equation("1 wood_spear = 12 fiber + 18 stick")
        calc.assign_equation("10 stick = 1 wood")
        calc.assign_equation("1 steel_screw = 1/100 steel_ingot")

        e1 = calc.resources["wood_spear"]
        e2 = calc.resources["stick"]
        e3 = calc.resources["steel_screw"]

        self.assertEqual("1 wood_spear = 12 fiber + 18 stick", str(e1))
        self.assertEqual("1 stick = 1/10 wood", str(e2))
        self.assertEqual("1 steel_screw = 1/100 steel_ingot", str(e3))

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

        # TODO keksi naille jotain
        l1 = calc.replace_variables([r1])
        l1 = " + ".join(map(str, l1))

        l2 = calc.replace_variables([r2])
        l2 = " + ".join(map(str, l2))

        l3 = calc.replace_variables([r3])
        l3 = " + ".join(map(str, l3))

        self.assertEqual("24 wood + 16 leather + 80 titanium_ingot + 8 epoxy + 32 steel_screw", l1)
        self.assertEqual("4/25 steel_ingot", l2)
        self.assertEqual("1 wood", l3)

    def test_search_variable(self):
        calc = Calculator()

        calc.assign_equation("1 hunting_rifle = 12 wood + 8 leather + 40 titanium_ingot + 4 epoxy + 16 steel_screw")
        calc.assign_equation("100 steel_screw = 1 steel_ingot")
        calc.assign_equation("1 steel_ingot = 1 steel_bloom")
        calc.assign_equation("1 steel_bloom = 6 iron_ore + 1 coal_ore")

        l1 = calc.resources["hunting_rifle"].resources
        l2 = calc.resources["steel_ingot"].resources
        l3 = calc.resources["steel_bloom"].resources

        self.assertEqual(["steel_screw"], calc.search_variable("iron_ore", l1))
        self.assertEqual(["steel_bloom"], calc.search_variable("iron_ore", l2))
        self.assertEqual([], calc.search_variable("iron_ore", l3))

    def test_calculate1(self):
        calc = self.calc

        calc.calculate("1 iron_ingot")

        with self.assertRaises(ValueError) as err:
            calc.calculate("1 iron_ore")
        self.assertEqual(f"ValueError: iron_ore", str(err.exception))
        
        with self.assertRaises(ValueError) as err:
            calc.calculate("1 null + 1 none")
        self.assertEqual(f"ValueError: null, none", str(err.exception))

    def test_calculate_hunting_rifle(self):
        calc = self.calc

        titanium_ingot1 = "200 titanium_ore"

        self.assertEqual(calc.calculate("40 titanium_ingot")[-1], calc.calculate(titanium_ingot1)[-1])
        self.assertEqual(calc.calculate("40 titanium_ingot")[-1], titanium_ingot1)

        epoxy_1 = "8 sulfur + 16 tree_sap"
        epoxy_2 = "8 sulfur + 64 stick"
        epoxy_3 = "8 sulfur + 7 wood"

        self.assertEqual(calc.calculate("4 epoxy")[-1], calc.calculate(epoxy_1)[-1])
        self.assertEqual(calc.calculate("4 epoxy")[-1], calc.calculate(epoxy_2)[-1])
        self.assertEqual(calc.calculate("4 epoxy")[-1], calc.calculate(epoxy_3)[-1])
        self.assertEqual(calc.calculate("4 epoxy")[-1], epoxy_3)

        steel_screw1 = "1 steel_ingot"
        steel_screw2 = "6 iron_ore + 1 coal_ore"

        self.assertEqual(calc.calculate("16 steel_screw")[-1], calc.calculate(steel_screw1)[-1])
        self.assertEqual(calc.calculate("16 steel_screw")[-1], calc.calculate(steel_screw2)[-1])
        self.assertEqual(calc.calculate("16 steel_screw")[-1], steel_screw2)

        hunting_rifle1 = "12 wood + 8 leather + 40 titanium_ingot + 4 epoxy + 16 steel_screw"
        hunting_rifle2 = "19 wood + 8 leather + 200 titanium_ore + 8 sulfur + 6 iron_ore + 1 coal_ore"

        self.assertEqual(calc.calculate("1 hunting_rifle")[-1], calc.calculate(hunting_rifle1)[-1])
        self.assertEqual(calc.calculate("1 hunting_rifle")[-1], calc.calculate(hunting_rifle2)[-1])
        self.assertEqual(calc.calculate("1 hunting_rifle")[-1], hunting_rifle2)

    def test_calculate_electric_extractor(self):
        calc = self.calc

        iron_ingot1 = "40 iron_ore"

        self.assertEqual(calc.calculate("20 iron_ingot")[-1], calc.calculate(iron_ingot1)[-1])
        self.assertEqual(calc.calculate("20 iron_ingot")[-1], iron_ingot1)

        electronics1 = "5 refined_gold + 15 copper_ingot + 10 organic_resin + 10 epoxy"
        electronics2 = "10 gold_ore + 30 copper_ore + 10 wood + 10 oxite + 20 sulfur + 40 tree_sap"
        electronics3 = "10 gold_ore + 30 copper_ore + 10 wood + 10 oxite + 20 sulfur + 160 stick"
        electronics4 = "10 gold_ore + 30 copper_ore + 26 wood + 10 oxite + 20 sulfur"

        self.assertEqual(calc.calculate("5 electronics")[-1], calc.calculate(electronics1)[-1])
        self.assertEqual(calc.calculate("5 electronics")[-1], calc.calculate(electronics2)[-1])
        self.assertEqual(calc.calculate("5 electronics")[-1], calc.calculate(electronics3)[-1])
        self.assertEqual(calc.calculate("5 electronics")[-1], calc.calculate(electronics4)[-1])
        self.assertEqual(calc.calculate("5 electronics")[-1], electronics4)
        
        electric_extractor1 = "60 iron_ingot + 15 electronics"
        electric_extractor2 = "120 iron_ore + 30 gold_ore + 90 copper_ore + 78 wood + 30 oxite + 60 sulfur"

        self.assertEqual(calc.calculate("3 electric_extractor")[-1], calc.calculate(electric_extractor1)[-1])
        self.assertEqual(calc.calculate("3 electric_extractor")[-1], calc.calculate(electric_extractor2)[-1])
        self.assertEqual(calc.calculate("3 electric_extractor")[-1], electric_extractor2)

    def test_subtract(self):
        r1 = Resource(Fraction(124/5), "wood")
        r2 = Resource(Fraction(160), "stone")
        r3 = Resource(Fraction(24), "leather")

        e1 = Calculator.subtract([r1, r2, r3])
        e1 = " + ".join(map(str, e1))

        self.assertEqual("25 wood + 160 stone + 24 leather", e1)

        r1 = Resource(Fraction(1, 3), "wood")
        r2 = Resource(Fraction(160), "stone")
        r3 = Resource(Fraction(1, 3), "wood")

        e1 = Calculator.subtract([r1, r2, r3])
        e1 = " + ".join(map(str, e1))

        self.assertEqual("1 wood + 160 stone", e1)

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

    def test_sort_resources(self):
        pass # TODO

    def test_format_resources(self):
        pass # TODO

    def test_get_amount(self):
        pass # TODO

    def test_get_name(self):
        pass # TODO

if __name__ == "__main__":
    unittest.main()
