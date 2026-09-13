# Database Documentation

The project uses **Cloud Firestore**, a flexible, scalable NoSQL document database provided by Google Firebase.

## Overview
Persistent storage is organized into three primary collections:
1. **`users`**: User profile information and registration audit data.
2. **`conversations`**: Multi-chat thread headers owned by individual users.
3. **`messages`**: Chronological prompt and response history per conversation.

For complete field specifications, ER diagrams, and indexing rules, refer to [docs/Firestore-Structure.md](file:///d:/from-c-drive/OneDrive/Desktop/AI%20chatbot/docs/Firestore-Structure.md).