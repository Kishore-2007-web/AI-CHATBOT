import os
from functools import wraps
from flask import Flask, render_template, request, jsonify, g
from dotenv import load_dotenv
from groq import Groq
import firebase_admin
from firebase_admin import credentials, firestore, auth

load_dotenv()

app = Flask(__name__)

# Initialize Firebase Admin SDK
cred_path = os.environ.get("FIREBASE_CREDENTIALS_PATH", "firebase-key.json")
firebase_initialized = False
db = None

if os.path.exists(cred_path):
    try:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        firebase_initialized = True
        print("[Firebase] Admin SDK initialized successfully.")
    except Exception as e:
        print(f"[Firebase] Error initializing Admin SDK: {e}")
else:
    print(f"[Firebase] Notice: Credentials file '{cred_path}' not found. Place your firebase-key.json in the project root.")


# Authentication Middleware Decorator
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Unauthorized: Missing or invalid Authorization token."}), 401
        
        id_token = auth_header.split("Bearer ")[1].strip()
        
        if firebase_initialized:
            try:
                decoded_token = auth.verify_id_token(id_token)
                g.user = decoded_token
            except Exception as e:
                print(f"[Auth Error] Token verification failed: {e}")
                return jsonify({"error": "Unauthorized: Invalid or expired authentication token."}), 401
        else:
            # Fallback for development before credentials key is attached
            g.user = {"uid": "dev-user-id", "email": "dev@local.com"}

        return f(*args, **kwargs)

    return decorated_function


client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)


def load_system_prompt():
    with open("prompts/kisa_system_prompt.txt", "r", encoding="utf-8") as file:
        return file.read()


SYSTEM_PROMPT = load_system_prompt()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "online",
        "firebase_connected": firebase_initialized,
        "credentials_path": cred_path,
        "credentials_found": os.path.exists(cred_path)
    })


@app.route("/chat", methods=["POST"])
@require_auth
def chat():
    data = request.get_json()
    user_message = data.get("message")
    user_uid = g.user.get("uid")

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
            "reply": bot_reply,
            "user_id": user_uid
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)