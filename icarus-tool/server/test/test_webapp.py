import unittest

from ddt import data, ddt

from webapp import app, application


@ddt
class TestWebapp(unittest.TestCase):
    @data("1 fabricator", "1 fabricator + 1 fabricator")
    def test_plaintext(self, value: str):
        encoded = value.replace(" ", "%20")
        url = "http://localhost:5000/plaintext/%s" % encoded
        with app.test_client() as client:
            actual = client.get(url).data.decode("utf-8")
        expected = "\n".join(application.process(value))
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
