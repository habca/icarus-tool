import json
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
        url = "/api/plaintext/%s" % encoded
        with app.test_client() as client:
            actual = client.get(url).data.decode("utf-8")

        # Output should not differ between CLI and Web application.
        self.assertEqual(expected, actual)

    @data("1 fabricator", "1 fabricator + 1 fabricator")
    def test_make_json(self, value: str):

        # Create a local application to compare output of web server.
        application = Application()
        application.init(["app.py", "-i", "-j", "data/tech_tree.txt"])

        # Get the output from the CLI application.
        expected = "\n".join(application.process(value))

        # Get the output from the Web server.
        encoded = value.replace(" ", "%20")
        url = "/api/json/%s" % encoded
        with app.test_client() as client:
            actual = client.get(url).data.decode("utf-8")

        # Output should not differ between CLI and Web application.
        self.assertEqual(expected, actual)

    def test_index(self):
        """Client build should exist on deployment server."""

        with open("../client/build/index.html") as reader:
            expected = reader.read()

        with app.test_client() as client:
            actual = client.get("/index.html").data.decode("utf-8")

        self.assertEqual(expected, actual)

    def test_json_all(self):

        application = Application()
        application.init(["app.py", "-i", "-j", "data/tech_tree.txt"])

        with app.test_client() as client:
            data = client.get("/api/json").data.decode("utf-8")

        expected: list[str] = list(application.calculator.resources)
        actual: list[str] = json.loads(data)

        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
