import unittest

from webapp import app, application


class TestWebapp(unittest.TestCase):
    def test_plaintext(self):
        url = "http://localhost:5000/plaintext/1%20fabricator"
        with app.test_client() as client:
            actual = client.get(url).data.decode("utf-8")
        expected = "\n".join(application.process("1 fabricator"))
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
