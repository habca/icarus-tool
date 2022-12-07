import unittest

from ddt import data, ddt

from app import app
from application import Application


@ddt
class TestApp(unittest.TestCase):
    @data("1 fabricator", "1 fabricator + 1 fabricator")
    def test_plaintext(self, value: str):

        # Create a local application to compare output of web server.
        application = Application()
        application.init(["app.py", "-i", "-r", "data/tech_tree.txt"])

        # Get the output from the CLI application.
        expected = "\n".join(application.process(value))

        # Get the output from the Web server.
        encoded = value.replace(" ", "%20")
        url = "http://localhost:5000/plaintext/%s" % encoded
        with app.test_client() as client:
            actual = client.get(url).data.decode("utf-8")

        # Output should not differ between CLI and Web application.
        self.assertEqual(expected, actual)

    @data("1 fabricator", "1 fabricator + 1 fabricator")
    def test_json(self, value: str):

        # Create a local application to compare output of web server.
        application = Application()
        application.init(["app.py", "-i", "-j", "data/tech_tree.txt"])

        # Get the output from the CLI application.
        expected = "\n".join(application.process(value))

        # Get the output from the Web server.
        encoded = value.replace(" ", "%20")
        url = "http://localhost:5000/json/%s" % encoded
        with app.test_client() as client:
            actual = client.get(url).data.decode("utf-8")

        # Output should not differ between CLI and Web application.
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
