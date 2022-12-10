from flask import Flask, jsonify, make_response, send_from_directory
from flask_cors import CORS, cross_origin

from application import Application
from calculator import Equation

app = Flask(__name__, static_url_path="/", static_folder="../../client/build")
app.config["CORS_HEADERS"] = "Content-Type"

cors = CORS(app)


@app.route("/")
@cross_origin()
def index():
    return app.send_static_file("index.html")


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


@app.route("/api/json")
@cross_origin()
def json_all():
    application = Application()
    application.init(["app.py", "-i", "-r", "data/tech_tree.txt"])
    array = list(application.calculator.resources)
    return jsonify(array)


@app.route("/api/json/<user_input>")
@cross_origin()
def make_json(user_input: str):
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
