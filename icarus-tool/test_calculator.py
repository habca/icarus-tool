from fractions import Fraction
from application import FileSystem
from calculator import Calculator

import unittest

class TestCalculator(unittest.TestCase):
    filename = "tech_tree.txt"

    def setUp(self) -> None:
        """
        Create a calculator before any test method.
        """
        self.calc = Calculator()
        file = FileSystem(TestCalculator.filename)
        file.read(self.calc)

    def test_get_keywords(self):
        """
        Test fires off to notify changes on getters.
        """
        calc = self.calc
        self.assertIsInstance(calc.get_keywords(), list)
        self.assertTrue(type(calc.get_keywords()) is list)

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

    def test_assign_equation(self):
        """
        An equation should be stored in a dictionary as follows.
        """
        calc = self.calc
        self.assertEqual(calc.resources["steel_screw"], "1/100 ( 1 steel_ingot )")
        self.assertEqual(calc.resources["stick"], "1/10 ( 1 wood )")
        self.assertEqual(calc.resources["iron_ingot"], "1 ( 2 iron_ore )")
        self.assertEqual(calc.resources["steel_bloom"], "1 ( 6 iron_ore + 1 coal_ore )")

    def test_assign_equation_duplicate(self):
        """
        A duplicate equation should raise an exception.
        Resources or variables should not have duplicate entries.
        """
        calc = self.calc
        with self.assertRaisesRegex(ValueError, "Name is already in use: rope"):
           calc.assign_equation("1 rope = 12 fiber")
        with self.assertRaisesRegex(ValueError, "Name is already in use: rope"):
           calc.assign_equation("1 rope = 5 leather")

        resources = list(calc.resources)
        variables = list(calc.variables)

        for resource in resources:
            self.assertEqual(1, resources.count(resource))
            self.assertFalse(resource in variables)
        for variable in variables:
            self.assertEqual(1, variables.count(variable))
            self.assertFalse(variable in resources)

    def test_assign_equation_aliases(self):
        """
        More than one equation may have the same resource cost.
        """
        calc = self.calc
        chest_armor = calc.resources["ghillie_chest_armor"]
        leg_armor = calc.resources["ghillie_leg_armor"]

        self.assertEqual(chest_armor, leg_armor)
        self.assertEqual(chest_armor, "1 ( 160 fiber + 8 stick + 6 rope )")

    def test_assign_equation_syntax_error(self):
        """
        A wrong equation should raise an exception.
        """
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

    def test_calculate_reject_unknown_resources(self):
        """
        The final form of an equation should contain known variables.
        """
        calc = self.calc
        calc.calculate("1 iron_ingot")
        with self.assertRaises(ValueError) as err:
            calc.calculate("1 not_exist")
        self.assertEqual(f"ValueError: not_exist", str(err.exception))

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

    def test_search_variable(self):
        calc = self.calc

        self.assertEqual(["steel_screw"], calc.search_variable("iron_ore", "12 wood + 8 leather + 40 titanium_ingot + 4 epoxy + 16 steel_screw"))
        self.assertEqual(["steel_bloom"], calc.search_variable("iron_ore", "1 steel_bloom"))
        self.assertEqual([], calc.search_variable("iron_ore", "6 iron_ore + 1 coal_ore"))
        self.assertEqual([], calc.search_variable("iron_ore", "iron_ore"))
        self.assertEqual([], calc.search_variable("iron_ore", "coal_ore"))

    def test_replace_variables(self):
        self.assertEqual(self.calc.replace_variables("1 hunting_rifle"), "1 1 ( 12 wood + 8 leather + 40 titanium_ingot + 4 epoxy + 16 steel_screw )")
        self.assertEqual(self.calc.replace_variables("16 steel_screw"), "16 1/100 ( 1 steel_ingot )")
        self.assertEqual(self.calc.replace_variables("10 stick"), "10 1/10 ( 1 wood )")

    def test_multiply(self):
        iterator = iter("1 1 ( 40 1 ( 2 iron_ore ) + 20 wood + 10 stone )".split())
        actual1 = Calculator.multiply(iterator, Fraction(1))

        self.assertEqual(actual1, "80 iron_ore + 20 wood + 10 stone")

    def test_subtract(self):
        actual1 = Calculator.subtract("124/5 wood + 160 stone + 24 leather")

        self.assertEqual(actual1, "25 wood + 160 stone + 24 leather")

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
