import os
import json
import re
from functools import wraps
from flask import Flask, render_template, request, jsonify, g
from dotenv import load_dotenv
from groq import Groq
import firebase_admin
from firebase_admin import credentials, firestore, auth
from db_service import DatabaseService

load_dotenv()

app = Flask(__name__)

# Configurable limits
RECENT_MESSAGE_LIMIT = 20
SUMMARY_THRESHOLD = 10

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
    print(f"[Firebase] Notice: Credentials file '{cred_path}' not found. Place your firebase-key.json in project root.")

# Instantiate Database Service
db_service = DatabaseService(db)

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

        # Ensure user profile document exists in Firestore
        if g.user and g.user.get("uid"):
            db_service.ensure_user_profile(g.user.get("uid"), g.user.get("email", ""))

        return f(*args, **kwargs)

    return decorated_function


client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)


def load_system_prompt():
    prompt_path = os.path.join("prompts", "kisa_system_prompt.txt")
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as file:
            return file.read()
    return "You are Kisa, a helpful AI assistant."


SYSTEM_PROMPT = load_system_prompt()


def build_ai_context(user_uid, conversation_id, new_user_message):
    """
    Context Pipeline:
    SYSTEM PROMPT + RELEVANT LONG-TERM MEMORY + CONVERSATION SUMMARY + RECENT PREVIOUS MESSAGES + CURRENT USER MESSAGE
    """
    messages_payload = []

    # 1. System Prompt & Memories & Summary
    system_text = SYSTEM_PROMPT.strip()

    # Long-term memory context
    settings = db_service.get_user_settings(user_uid)
    if settings.get("memoryEnabled", True):
        memories = db_service.get_memories(user_uid)
        if memories:
            mem_lines = [f"- {m['content']}" for m in memories[:10]]
            system_text += "\n\nUSER MEMORIES (Long-term user preferences & facts):\n" + "\n".join(mem_lines)

    # Conversation summary context
    conv = db_service.get_conversation(conversation_id)
    if conv and conv.get("summary"):
        system_text += f"\n\nCONVERSATION SUMMARY (Prior discussion overview):\n{conv.get('summary')}"

    messages_payload.append({"role": "system", "content": system_text})

    # 2. Recent Conversation Messages (Excluding the new user message to prevent duplication)
    existing_messages = db_service.get_conversation_messages(conversation_id, user_uid)
    recent_messages = existing_messages[-RECENT_MESSAGE_LIMIT:] if len(existing_messages) > RECENT_MESSAGE_LIMIT else existing_messages

    for msg in recent_messages:
        role = msg.get("role")
        if role in ["user", "assistant"]:
            messages_payload.append({
                "role": role,
                "content": msg.get("content", "")
            })

    # 3. Append current user message
    messages_payload.append({"role": "user", "content": new_user_message})

    return messages_payload


def generate_title_if_needed(user_uid, conversation_id, user_message):
    """Generates a concise 3-7 word title for new conversations."""
    conv = db_service.get_conversation(conversation_id)
    if not conv:
        return

    # Generate if title is default
    if conv.get("title") in ["New Conversation", "New Chat", ""]:
        try:
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You generate short chat titles. Respond ONLY with a 3 to 6 word concise title. Do NOT use quotes, punctuation, or preamble."},
                    {"role": "user", "content": f"Create a short title for a chat starting with: {user_message[:150]}"}
                ],
                max_tokens=20
            )
            title = res.choices[0].message.content.strip().strip('"').strip("'")
            if title:
                db_service.rename_conversation(conversation_id, user_uid, title)
        except Exception as e:
            print(f"[Title Gen Error] {e}")


def update_summary_if_needed(user_uid, conversation_id):
    """Updates conversation summary if message count exceeds threshold."""
    messages = db_service.get_conversation_messages(conversation_id, user_uid)
    if len(messages) >= SUMMARY_THRESHOLD and len(messages) % 6 == 0:
        try:
            transcript = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in messages[-16:]])
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Summarize the key topics, user preferences, and goals discussed in this chat transcript in 2-3 concise sentences."},
                    {"role": "user", "content": transcript}
                ],
                max_tokens=150
            )
            summary = res.choices[0].message.content.strip()
            if summary:
                db_service.update_conversation_summary(conversation_id, user_uid, summary)
        except Exception as e:
            print(f"[Summary Gen Error] {e}")


def extract_memory_safely(user_uid, user_message, assistant_reply):
    """Extracts long-term user memories while guarding sensitive data."""
    settings = db_service.get_user_settings(user_uid)
    if not settings.get("memoryEnabled", True):
        return

    # Sensitive key filter
    sensitive_patterns = [r"password", r"api[_\s]?key", r"secret", r"token", r"bearer", r"credit[_\s]?card", r"ssn", r"auth"]
    for pat in sensitive_patterns:
        if re.search(pat, user_message, re.IGNORECASE):
            return

    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": (
                    "You are a memory extraction component. Analyze if the user statement contains long-term personal preferences, "
                    "skills, ongoing projects, or goals worth remembering. Do NOT store temporary questions, code debug requests, or sensitive info.\n"
                    "Respond strictly in JSON format:\n"
                    "{\"should_save\": boolean, \"memory\": \"string\", \"category\": \"project|preference|skill|goal|workflow|general\", \"importance\": \"high|medium|low\"}"
                )},
                {"role": "user", "content": f"User said: {user_message[:300]}"}
            ],
            response_format={"type": "json_object"},
            max_tokens=100
        )
        data = json.loads(res.choices[0].message.content)
        if data.get("should_save") and data.get("memory"):
            db_service.add_memory(
                user_id=user_uid,
                content=data.get("memory"),
                category=data.get("category", "general"),
                importance=data.get("importance", "medium")
            )
    except Exception as e:
        print(f"[Memory Extract Error] {e}")


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


# --- Chat Endpoints ---

@app.route("/chat", methods=["POST"])
@app.route("/api/chat", methods=["POST"])
@require_auth
def chat():
    data = request.get_json() or {}
    user_message = data.get("message", "").strip()
    conversation_id = data.get("conversation_id")
    user_uid = g.user.get("uid")

    if not user_message:
        return jsonify({"error": "Message content cannot be empty."}), 400

    # Ensure valid conversation ID
    if not conversation_id:
        conv = db_service.create_conversation(user_uid)
        conversation_id = conv["id"]
    else:
        conv = db_service.get_conversation(conversation_id)
        if not conv or conv.get("userId") != user_uid:
            conv = db_service.create_conversation(user_uid)
            conversation_id = conv["id"]

    # 1. Build context BEFORE adding the new user message (prevents duplicate user message in prompt payload)
    messages_payload = build_ai_context(user_uid, conversation_id, user_message)

    # 2. Save user message to database
    user_msg_doc = db_service.add_message(conversation_id, user_uid, "user", user_message)

    try:
        # 3. Call Groq API
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages_payload
        )

        bot_reply = response.choices[0].message.content

        # 4. Save assistant response to database
        bot_msg_doc = db_service.add_message(conversation_id, user_uid, "assistant", bot_reply)

        # 5. Background tasks: Title generation, summary update, memory extraction
        generate_title_if_needed(user_uid, conversation_id, user_message)
        update_summary_if_needed(user_uid, conversation_id)
        extract_memory_safely(user_uid, user_message, bot_reply)

        # Fetch updated conversation for title
        updated_conv = db_service.get_conversation(conversation_id)

        return jsonify({
            "reply": bot_reply,
            "conversation_id": conversation_id,
            "title": updated_conv.get("title") if updated_conv else "New Conversation",
            "user_message_id": user_msg_doc.get("id"),
            "bot_message_id": bot_msg_doc.get("id"),
            "user_id": user_uid
        })

    except Exception as e:
        print(f"[Groq Chat Error] {e}")
        return jsonify({"error": f"AI service error: {str(e)}"}), 500


@app.route("/api/chat/edit", methods=["POST"])
@require_auth
def edit_message():
    data = request.get_json() or {}
    conversation_id = data.get("conversation_id")
    message_id = data.get("message_id")
    new_message = data.get("new_message", "").strip()
    user_uid = g.user.get("uid")

    if not conversation_id or not message_id or not new_message:
        return jsonify({"error": "Missing conversation_id, message_id, or new_message."}), 400

    # Truncate messages in conversation after message_id
    db_service.delete_messages_after(conversation_id, user_uid, message_id)
    # Delete the target message itself so we re-send as new edited message
    db_service.delete_message(message_id, user_uid)

    # Trigger chat processing with new message content
    return chat()


@app.route("/api/chat/regenerate", methods=["POST"])
@require_auth
def regenerate_message():
    data = request.get_json() or {}
    conversation_id = data.get("conversation_id")
    assistant_message_id = data.get("message_id")
    user_uid = g.user.get("uid")

    if not conversation_id or not assistant_message_id:
        return jsonify({"error": "Missing conversation_id or message_id."}), 400

    # Delete the specific assistant message to be regenerated
    db_service.delete_message(assistant_message_id, user_uid)

    # Get conversation messages up to latest user message
    messages = db_service.get_conversation_messages(conversation_id, user_uid)
    if not messages:
        return jsonify({"error": "No messages found in conversation to regenerate."}), 400

    last_user_msg = None
    for msg in reversed(messages):
        if msg.get("role") == "user":
            last_user_msg = msg
            break

    if not last_user_msg:
        return jsonify({"error": "No user message found to regenerate from."}), 400

    # Truncate any stray messages after this last user message
    db_service.delete_messages_after(conversation_id, user_uid, last_user_msg["id"])

    # Re-run AI response generation for last user message content without creating duplicate user message
    messages_payload = build_ai_context(user_uid, conversation_id, last_user_msg["content"])

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages_payload
        )
        bot_reply = response.choices[0].message.content
        bot_msg_doc = db_service.add_message(conversation_id, user_uid, "assistant", bot_reply)

        return jsonify({
            "reply": bot_reply,
            "conversation_id": conversation_id,
            "bot_message_id": bot_msg_doc.get("id"),
            "user_id": user_uid
        })
    except Exception as e:
        return jsonify({"error": f"AI service error: {str(e)}"}), 500


# --- Conversation Management Endpoints ---

@app.route("/api/conversations", methods=["GET"])
@require_auth
def list_conversations():
    user_uid = g.user.get("uid")
    conversations = db_service.get_user_conversations(user_uid)
    return jsonify({"conversations": conversations})


@app.route("/api/conversations", methods=["POST"])
@require_auth
def create_new_conversation():
    user_uid = g.user.get("uid")
    data = request.get_json() or {}
    title = data.get("title", "New Conversation")
    conv = db_service.create_conversation(user_uid, title=title)
    return jsonify(conv), 201


@app.route("/api/conversations/<conversation_id>", methods=["GET"])
@require_auth
def get_single_conversation(conversation_id):
    user_uid = g.user.get("uid")
    conv = db_service.get_conversation(conversation_id)
    if not conv or conv.get("userId") != user_uid:
        return jsonify({"error": "Conversation not found or access denied."}), 404
    return jsonify(conv)


@app.route("/api/conversations/<conversation_id>", methods=["PATCH"])
@require_auth
def rename_conv(conversation_id):
    user_uid = g.user.get("uid")
    data = request.get_json() or {}
    new_title = data.get("title", "").strip()
    if not new_title:
        return jsonify({"error": "Title cannot be empty."}), 400

    success = db_service.rename_conversation(conversation_id, user_uid, new_title)
    if success:
        return jsonify({"message": "Conversation renamed successfully."})
    return jsonify({"error": "Failed to rename conversation."}), 400


@app.route("/api/conversations/<conversation_id>", methods=["DELETE"])
@require_auth
def delete_conv(conversation_id):
    user_uid = g.user.get("uid")
    success = db_service.delete_conversation(conversation_id, user_uid)
    if success:
        return jsonify({"message": "Conversation deleted successfully."})
    return jsonify({"error": "Failed to delete conversation."}), 400


@app.route("/api/conversations/<conversation_id>/messages", methods=["GET"])
@require_auth
def get_messages_route(conversation_id):
    user_uid = g.user.get("uid")
    messages = db_service.get_conversation_messages(conversation_id, user_uid)
    return jsonify({"messages": messages})


# --- Memories & Settings Endpoints ---

@app.route("/api/memories", methods=["GET"])
@require_auth
def get_user_memories():
    user_uid = g.user.get("uid")
    memories = db_service.get_memories(user_uid)
    return jsonify({"memories": memories})


@app.route("/api/memories/<memory_id>", methods=["DELETE"])
@require_auth
def delete_user_memory(memory_id):
    user_uid = g.user.get("uid")
    success = db_service.delete_memory(memory_id, user_uid)
    if success:
        return jsonify({"message": "Memory deleted successfully."})
    return jsonify({"error": "Memory not found or access denied."}), 400


@app.route("/api/memories", methods=["DELETE"])
@require_auth
def clear_all_user_memories():
    user_uid = g.user.get("uid")
    db_service.clear_memories(user_uid)
    return jsonify({"message": "All memories cleared."})


@app.route("/api/settings/memory", methods=["GET"])
@require_auth
def get_memory_setting_route():
    user_uid = g.user.get("uid")
    settings = db_service.get_user_settings(user_uid)
    return jsonify(settings)


@app.route("/api/settings/memory", methods=["PATCH"])
@require_auth
def update_memory_setting_route():
    user_uid = g.user.get("uid")
    data = request.get_json() or {}
    enabled = data.get("enabled", True)
    db_service.update_memory_setting(user_uid, bool(enabled))
    return jsonify({"message": "Memory settings updated.", "memoryEnabled": bool(enabled)})


if __name__ == "__main__":
    app.run(debug=True)