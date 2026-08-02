#from flask import Flask, render_template

#app = Flask(__name__)


#@app.route("/")
#def home():
#    return render_template("index.html")


#if __name__ == "__main__":
#    app.run(debug=True)
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    user_message = data.get("message")


    response = {
        "reply": f"You said: {user_message}"
    }


    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)