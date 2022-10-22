import sys

from flask import Flask, make_response, render_template, send_from_directory

from application import Application
from calculator import Equation

app = Flask(__name__)

# TODO: Global variable is not thread-save.
application = Application()
application.init(["webapp.py", "-i", "-r", "server/data/tech_tree.txt"])

# Test case for debugging.
print("Try me: http://localhost:5000/plaintext/1%20fabricator", file=sys.stdout)
print("Try me: http://localhost:5000/api/data", file=sys.stdout)
print("Try me: http://localhost:5000/", file=sys.stdout)


@app.route("/plaintext/<user_input>")
def plaintext(user_input: str):
    try:
        equation: Equation = application.parse_input(user_input)
        equation = application.preprocessor.process(equation)
        output: list[str] = application.algorithm.calculate(equation)
    except SyntaxError as err:
        output = application.help()
        output.insert(0, str(err))
    except ValueError as err:
        output = application.recover(user_input)
        output.insert(0, str(err))

    response = make_response("\n".join(output))
    response.mimetype = "text/plain"
    return response


@app.route("/")
def index():
    lines = ["one", "two", "three"]
    return render_template(
        "index.html",
        title="title",
        output=lines,
    )


@app.route("/api/data")
def get_data():
    return send_from_directory("../data", "tech_tree.txt")


if __name__ == "__main__":
    app.run(debug=True)
