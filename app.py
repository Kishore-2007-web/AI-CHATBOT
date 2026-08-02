#from flask import Flask, render_template

#app = Flask(__name__)


#@app.route("/")
#def home():
#    return render_template("index.html")


#if __name__ == "__main__":
#    app.run(debug=True)
#from flask import Flask, render_template, request, jsonify

#app = Flask(__name__)


#@app.route("/")
#def home():
#    return render_template("index.html")


#@app.route("/chat", methods=["POST"])
#def chat():

    #data = request.get_json()

    #user_message = data.get("message")


    #response = {
        #"reply": f"You said: {user_message}"
    #}


    #return jsonify(response)


#if __name__ == "__main__":
    #app.run(debug=True)

import os

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from groq import Groq


load_dotenv()


app = Flask(__name__)


client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)


SYSTEM_PROMPT = """
You are a helpful AI assistant.
Your name is Varina.
Answer clearly and politely.
"""


@app.route("/")
def home():

    return render_template("index.html")



@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    user_message = data.get("message")


    try:

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[

                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },

                {
                    "role": "user",
                    "content": user_message
                }

            ]

        )


        bot_reply = response.choices[0].message.content


        return jsonify({

            "reply": bot_reply

        })


    except Exception as e:


        return jsonify({

            "error": str(e)

        }), 500



if __name__ == "__main__":

    app.run(debug=True)