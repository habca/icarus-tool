from flask import Flask, make_response, send_from_directory

from application import Application
from calculator import Equation

app = Flask(__name__, static_url_path="", static_folder="../../client/build")


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/plaintext/tech_tree.txt")
def get_data():
    return send_from_directory("../data", "tech_tree.txt")


@app.route("/api/plaintext/<user_input>")
def plaintext(user_input: str):
    config: list[str] = ["app.py", "-i", "-r", "data/tech_tree.txt"]
    output: list[str] = handle_request(config, user_input)

    response = make_response("\n".join(output))
    response.mimetype = "text/plain"
    return response


@app.route("/api/json/<user_input>")
def json(user_input: str):
    config: list[str] = ["app.py", "-i", "-j", "data/tech_tree.txt"]
    output: list[str] = handle_request(config, user_input)

    response = make_response("\n".join(output))
    response.mimetype = "application/json"
    return response


def handle_request(config: list[str], user_input: str) -> list[str]:
    application = Application()
    application.init(config)

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

    return output


if __name__ == "__main__":
    app.run(debug=True)
