from flask import Flask, render_template
import sys
from application import Application
from calculator import Equation

app = Flask(__name__)

# TODO: Global variable is not thread-save.
application = Application()
application.init(["app.py", "-i", "-r", "data/tech_tree.txt"])

# Test case for debugging.
print("Try me: http://localhost:5000/plaintext/1%20fabricator", file=sys.stdout)


@app.route("/plaintext/<user_input>")
def hello_world(user_input: str):
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
    return render_template("index.html", title=user_input, output=output)


if __name__ == "__main__":
    app.run()
