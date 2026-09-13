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
        conversation_id = str(uuid.uuid4())
        now = self._get_timestamp()

        conversation_data = {
            "id": conversation_id,
            "userId": user_id,
            "title": title,
            "summary": "",
            "createdAt": now,
            "updatedAt": now
        }

        if self.db:
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

    def update_conversation_summary(self, conversation_id, user_id, summary_text):
        """Updates the summary of a conversation if owned by user."""
        if not self.db:
            return False

        conv_ref = self.db.collection("conversations").document(conversation_id)
        doc = conv_ref.get()

        if doc.exists and doc.to_dict().get("userId") == user_id:
            conv_ref.update({
                "summary": summary_text,
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

    def add_message(self, conversation_id, user_id, role, content, metadata=None):
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
        if metadata:
            message_data["metadata"] = metadata

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

    def delete_messages_after(self, conversation_id, user_id, target_message_id):
        """
        For message editing: Deletes all messages in conversation created after target_message_id.
        """
        if not self.db:
            return False

        conv = self.get_conversation(conversation_id)
        if not conv or conv.get("userId") != user_id:
            return False

        target_doc = self.db.collection("messages").document(target_message_id).get()
        if not target_doc.exists:
            return False

        target_created_at = target_doc.to_dict().get("createdAt")

        # Query messages after target_created_at
        messages = self.db.collection("messages")\
            .where("conversationId", "==", conversation_id)\
            .where("createdAt", ">", target_created_at)\
            .stream()

        count = 0
        for msg in messages:
            msg.reference.delete()
            count += 1

        print(f"[Firestore] Truncated {count} messages after {target_message_id}")
        return True

    def delete_message(self, message_id, user_id):
        """Deletes a single message document if owned by user."""
        if not self.db:
            return False

        msg_ref = self.db.collection("messages").document(message_id)
        doc = msg_ref.get()
        if doc.exists and doc.to_dict().get("userId") == user_id:
            msg_ref.delete()
            return True
        return False

    # --- Long-Term User Memories & Settings ---

    def add_memory(self, user_id, content, category="general", importance="medium"):
        """
        Adds a new long-term user memory document.
        """
        memory_id = str(uuid.uuid4())
        now = self._get_timestamp()

        # Check for duplicates or near-duplicates
        existing = self.get_memories(user_id)
        for mem in existing:
            if mem.get("content", "").strip().lower() == content.strip().lower():
                print(f"[Firestore] Memory already exists for user {user_id}, skipping duplicate.")
                return mem

        memory_data = {
            "id": memory_id,
            "userId": user_id,
            "content": content.strip(),
            "category": category,
            "importance": importance,
            "createdAt": now,
            "updatedAt": now
        }

        if self.db:
            self.db.collection("memories").document(memory_id).set(memory_data)
            print(f"[Firestore] Saved long-term memory {memory_id} for user {user_id}")

        return memory_data

    def get_memories(self, user_id):
        """Retrieves all active memories for a user."""
        if not self.db:
            return []

        query = self.db.collection("memories")\
            .where("userId", "==", user_id)\
            .order_by("createdAt", direction=firestore.Query.DESCENDING)

        docs = query.stream()
        return [doc.to_dict() for doc in docs]

    def delete_memory(self, memory_id, user_id):
        """Deletes a specific memory document."""
        if not self.db:
            return False

        mem_ref = self.db.collection("memories").document(memory_id)
        doc = mem_ref.get()
        if doc.exists and doc.to_dict().get("userId") == user_id:
            mem_ref.delete()
            print(f"[Firestore] Deleted memory {memory_id} for user {user_id}")
            return True
        return False

    def clear_memories(self, user_id):
        """Deletes all memories for a user."""
        if not self.db:
            return False

        mems = self.db.collection("memories").where("userId", "==", user_id).stream()
        count = 0
        for m in mems:
            m.reference.delete()
            count += 1

        print(f"[Firestore] Cleared {count} memories for user {user_id}")
        return True

    def get_user_settings(self, user_id):
        """Retrieves user settings (e.g. memory_enabled). Default memory_enabled=True."""
        if not self.db:
            return {"memoryEnabled": True}

        doc = self.db.collection("users").document(user_id).get()
        if doc.exists:
            user_data = doc.to_dict()
            return {
                "memoryEnabled": user_data.get("memoryEnabled", True)
            }
        return {"memoryEnabled": True}

    def update_memory_setting(self, user_id, enabled: bool):
        """Toggles user memory_enabled setting."""
        if not self.db:
            return False

        user_ref = self.db.collection("users").document(user_id)
        user_ref.set({"memoryEnabled": enabled, "updatedAt": self._get_timestamp()}, merge=True)
        print(f"[Firestore] Updated memoryEnabled={enabled} for user {user_id}")
        return True

