import uuid
from datetime import datetime, timezone
from firebase_admin import firestore

class DatabaseService:
    def __init__(self, db_client):
        self.db = db_client

    def _get_timestamp(self):
        """Generates UTC ISO 8601 timestamp string for document auditing."""
        return datetime.now(timezone.utc).isoformat()

    def ensure_user_profile(self, uid, email, display_name=None):
        """
        Creates or updates a user document in 'users' collection.
        Document ID: uid
        """
        if not self.db:
            return None

        user_ref = self.db.collection("users").document(uid)
        user_doc = user_ref.get()
        now = self._get_timestamp()

        if not user_doc.exists:
            user_data = {
                "uid": uid,
                "email": email,
                "displayName": display_name or email.split("@")[0],
                "createdAt": now,
                "updatedAt": now
            }
            user_ref.set(user_data)
            print(f"[Firestore] Created new user profile for UID: {uid}")
            return user_data
        else:
            user_ref.update({"updatedAt": now})
            return user_doc.to_dict()

    def create_conversation(self, user_id, title="New Conversation"):
        """
        Creates a new conversation document in 'conversations' collection.
        Document ID: conversation_id (UUID4 string)
        """
        if not self.db:
            conversation_id = str(uuid.uuid4())
            now = self._get_timestamp()
            return {
                "id": conversation_id,
                "userId": user_id,
                "title": title,
                "createdAt": now,
                "updatedAt": now
            }

        conversation_id = str(uuid.uuid4())
        now = self._get_timestamp()

        conversation_data = {
            "id": conversation_id,
            "userId": user_id,
            "title": title,
            "createdAt": now,
            "updatedAt": now
        }

        self.db.collection("conversations").document(conversation_id).set(conversation_data)
        print(f"[Firestore] Created conversation {conversation_id} for user {user_id}")
        return conversation_data

    def get_user_conversations(self, user_id):
        """
        Retrieves all conversations belonging to a user, ordered by latest activity.
        """
        if not self.db:
            return []

        query = self.db.collection("conversations")\
            .where("userId", "==", user_id)\
            .order_by("updatedAt", direction=firestore.Query.DESCENDING)

        docs = query.stream()
        return [doc.to_dict() for doc in docs]

    def get_conversation(self, conversation_id):
        """Retrieves a single conversation by ID."""
        if not self.db:
            return None

        doc = self.db.collection("conversations").document(conversation_id).get()
        return doc.to_dict() if doc.exists else None

    def rename_conversation(self, conversation_id, user_id, new_title):
        """Renames a conversation if owned by the user."""
        if not self.db:
            return False

        conv_ref = self.db.collection("conversations").document(conversation_id)
        doc = conv_ref.get()

        if doc.exists and doc.to_dict().get("userId") == user_id:
            conv_ref.update({
                "title": new_title,
                "updatedAt": self._get_timestamp()
            })
            return True
        return False

    def delete_conversation(self, conversation_id, user_id):
        """Deletes a conversation and its messages if owned by the user."""
        if not self.db:
            return False

        conv_ref = self.db.collection("conversations").document(conversation_id)
        doc = conv_ref.get()

        if not doc.exists or doc.to_dict().get("userId") != user_id:
            return False

        # Delete associated messages
        messages = self.db.collection("messages").where("conversationId", "==", conversation_id).stream()
        for msg in messages:
            msg.reference.delete()

        # Delete conversation document
        conv_ref.delete()
        print(f"[Firestore] Deleted conversation {conversation_id} and its messages.")
        return True

    def add_message(self, conversation_id, user_id, role, content):
        """
        Adds a message document to 'messages' collection and updates conversation timestamp.
        """
        message_id = str(uuid.uuid4())
        now = self._get_timestamp()

        message_data = {
            "id": message_id,
            "conversationId": conversation_id,
            "userId": user_id,
            "role": role,  # 'user' or 'assistant'
            "content": content,
            "createdAt": now
        }

        if self.db:
            self.db.collection("messages").document(message_id).set(message_data)
            
            # Update conversation timestamp
            self.db.collection("conversations").document(conversation_id).update({
                "updatedAt": now
            })
            print(f"[Firestore] Saved {role} message {message_id} in conversation {conversation_id}")

        return message_data

    def get_conversation_messages(self, conversation_id, user_id):
        """
        Retrieves all messages for a specific conversation ordered chronologically by createdAt.
        """
        if not self.db:
            return []

        # Ensure conversation belongs to user
        conv = self.get_conversation(conversation_id)
        if not conv or conv.get("userId") != user_id:
            return []

        query = self.db.collection("messages")\
            .where("conversationId", "==", conversation_id)\
            .order_by("createdAt", direction=firestore.Query.ASCENDING)

        docs = query.stream()
        return [doc.to_dict() for doc in docs]
