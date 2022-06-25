import utils
import unittest

class TestUtils(unittest.TestCase):

    def test_extract(self):
        self.assertEqual(("12", "34 6"), utils.extract("12 34 6"))
        self.assertEqual(("34", "6"), utils.extract("34 6"))
        self.assertEqual(("6", ""), utils.extract("6"))
        self.assertEqual(("", ""), utils.extract(""))

        self.assertEqual(("6", "12 34"), utils.extract("12 34 6", reverse=True))
        self.assertEqual(("34", "12"), utils.extract("12 34", reverse=True))
        self.assertEqual(("12", ""), utils.extract("12", reverse=True))
        self.assertEqual(("", ""), utils.extract("", reverse=True))

        self.assertEqual(("12", "34 6"), utils.extract(" 12 34 6 "))
        self.assertEqual(("12", "34 6"), utils.extract(" 12  34  6 "))
        self.assertEqual(("6", "12 34"), utils.extract(" 12 34 6 ", reverse=True))
        self.assertEqual(("6", "12 34"), utils.extract(" 12  34  6 ", reverse=True))

        self.assertEqual(("", "12 34 6"), utils.extract("12 34 6", sep=""))
        self.assertEqual(("", "12 34 6"), utils.extract(" 12  34  6 ", sep=""))
        self.assertEqual(("", "12 34 6"), utils.extract("12 34 6", sep="", reverse=True))
        self.assertEqual(("", "12 34 6"), utils.extract(" 12  34  6 ", sep="", reverse=True))

if __name__ == "__main__":
    unittest.main()
