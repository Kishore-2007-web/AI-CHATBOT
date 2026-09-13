# Firestore Database Schema & Architecture

This document defines the Cloud Firestore database architecture for **AI Chatbot v2.0**, detailing collections, document fields, relationship modeling, and timestamp indexing.

---

## 1. Entity-Relationship Diagram

```text
+-----------------------+           +-----------------------------+
|        users          |           |        conversations        |
+-----------------------+           +-----------------------------+
| uid (Doc ID)    [PK]  | 1       * | id (Doc ID)           [PK]  |
| email                 |-----------| userId                [FK]  |
| displayName           |           | title                       |
| createdAt             |           | createdAt                   |
| updatedAt             |           | updatedAt             [IDX] |
+-----------------------+           +-----------------------------+
                                                   | 1
                                                   |
                                                   | *
                                    +-----------------------------+
                                    |          messages           |
                                    +-----------------------------+
                                    | id (Doc ID)           [PK]  |
                                    | conversationId        [FK]  |
                                    | userId                [FK]  |
                                    | role ('user'|'assistant')   |
                                    | content                     |
                                    | createdAt             [IDX] |
                                    +-----------------------------+
```

---

## 2. Collections & Document Specs

### 2.1 `users` Collection
- **Path**: `users/{userId}`
- **Purpose**: Stores user profile metadata and audit timestamps.
- **Fields**:
  - `uid` (String): Firebase Auth unique identifier.
  - `email` (String): User email address.
  - `displayName` (String): Display name or username derived from email.
  - `createdAt` (String): ISO 8601 UTC timestamp of registration.
  - `updatedAt` (String): ISO 8601 UTC timestamp of last activity.

### 2.2 `conversations` Collection
- Path: `conversations/{conversationId}`
- **Purpose**: Tracks user chat threads (ChatGPT-style multiple conversations).
- **Fields**:
  - `id` (String): Unique conversation UUID.
  - `userId` (String): FK referencing `users/{userId}`.
  - `title` (String): Title of conversation (e.g. "New Chat" or generated summary).
  - `createdAt` (String): ISO 8601 UTC timestamp.
  - `updatedAt` (String): ISO 8601 UTC timestamp (used to sort conversations by latest activity).

### 2.3 `messages` Collection
- Path: `messages/{messageId}`
- **Purpose**: Stores individual prompt messages and generated AI responses.
- **Fields**:
  - `id` (String): Unique message UUID.
  - `conversationId` (String): FK referencing `conversations/{conversationId}`.
  - `userId` (String): FK referencing owner `users/{userId}`.
  - `role` (String): `user` for user inputs, `assistant` for Kisa AI responses.
  - `content` (String): The markdown formatted text message.
  - `createdAt` (String): ISO 8601 UTC timestamp (used to render messages chronologically).

---

## 3. Indexing & Query Rules

1. **Conversations Query**:
   `conversations.where('userId', '==', user_id).order_by('updatedAt', direction='DESCENDING')`
   - Requiring a composite index on `(userId ASC, updatedAt DESC)`.

2. **Messages Query**:
   `messages.where('conversationId', '==', conversation_id).order_by('createdAt', direction='ASCENDING')`
   - Requiring a composite index on `(conversationId ASC, createdAt ASC)`.
