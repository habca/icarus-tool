from flask import Flask, make_response, redirect, render_template, send_from_directory

from application import Application
from calculator import Equation

app = Flask(__name__)

# TODO: Global variable is not thread-save.
application = Application()
application.init(["webapp.py", "-i", "-r", "data/tech_tree.txt"])


@app.route("/plaintext/tech_tree.txt")
def get_data():
    return send_from_directory("../data", "tech_tree.txt")


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


if __name__ == "__main__":
    app.run(debug=True)
