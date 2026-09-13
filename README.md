# Kisa AI Assistant v2.5

A production-grade, full-stack personal AI assistant featuring **Firebase Authentication**, **Cloud Firestore Database**, **Python Flask Backend**, **Groq AI (Llama 3.3 70B)**, persistent conversation memory, long-term user memory extraction, and a modern responsive dark UI.

---

## 🌟 Key Features

* **🔐 Firebase User Authentication**: Email/Password Sign Up & Sign In, Google OAuth 2.0 Popup Sign-In, and session persistence (`onAuthStateChanged`).
* **📁 Multi-Conversation Drawer**: ChatGPT-style sidebar grouped by date (*Today*, *Yesterday*, *Older*) with inline search, rename, and delete actions.
* **🧠 Context Memory Engine**: Context Pipeline assembling `System Prompt + Relevant User Memories + Conversation Summary + Recent 20 Messages + Current Message`.
* **💡 Automatic Title Generation**: Generates 3–6 word concise conversation titles on the first turn.
* **📝 Conversation Summarization**: Auto-summarizes long discussions (>10 messages) to maintain historical context without overloading token limits.
* **📌 Long-Term User Memory**: Extracts user preferences, skills, projects, and goals across chat sessions with safety filters (excludes passwords, tokens, API keys, and sensitive data).
* **⚙️ Memory Management UI**: Dedicated Settings modal allowing users to view stored memories, delete individual items, clear all memories, or toggle memory extraction on/off.
* **💻 Markdown & Code Highlighting**: Full Markdown parsing via `Marked.js`, syntax highlighting via `Highlight.js` (GitHub Dark theme), and 1-click **Copy Code** / **Copy Response** buttons.
* **✏️ Message Editing & Response Regeneration**: Edit earlier user messages (with clean branch truncation) or regenerate assistant replies without duplicating messages.
* **🔒 Production Data Security**: Enforces user data isolation on Flask backend (`@require_auth` verifying Firebase JWT ID tokens) and Firestore security rules (`firestore.rules`).

---

## 🏗️ Technology Stack

* **Frontend**: HTML5, CSS3 (Modern Glassmorphism Dark Theme), JavaScript (ES6 Modules), Marked.js, Highlight.js.
* **Backend**: Python 3, Flask, Firebase Admin SDK.
* **Database**: Cloud Firestore (`users`, `conversations`, `messages`, `memories` collections).
* **AI Engine**: Groq API (`llama-3.3-70b-versatile`).
* **Authentication**: Firebase Auth (Email/Password & Google Provider).

---

## 📁 Project Structure

```text
AI-Chatbot/
├── app.py                     # Main Flask Application & REST API Endpoints
├── db_service.py              # Database Service Layer (Firestore Operations)
├── firestore.rules            # Production Firestore Security Rules
├── requirements.txt           # Python Dependencies
├── .env                       # Environment Variables (Secrets)
│
├── prompts/
│   └── kisa_system_prompt.txt # Kisa AI Persona & System Instructions
│
├── static/
│   ├── css/
│   │   └── style.css          # Responsive Dark Glassmorphism Stylesheet
│   └── js/
│       ├── firebase-config.js # Firebase Web Client SDK Initialization
│       ├── auth.js            # Auth Controllers & Session Observer
│       ├── conversations.js   # Sidebar Conversation Manager
│       ├── memory.js          # Settings & Long-Term Memory Controller
│       └── script.js          # Main Chat UI, Markdown, Code Copy, Edit/Regen
│
├── templates/
│   └── index.html             # Main Single Page Application Layout
│
└── docs/                      # Technical Documentation Guides
```

---

## 🚀 REST API Specification

### Authentication Header
All protected endpoints require:
`Authorization: Bearer <Firebase_ID_Token>`

### Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Diagnostic status check for Firebase credentials |
| `POST` | `/api/chat` | Send message & get AI reply (creates conversation if omitted) |
| `POST` | `/api/chat/edit` | Edit user message & truncate subsequent history branch |
| `POST` | `/api/chat/regenerate` | Regenerate last assistant reply |
| `GET` | `/api/conversations` | List user's conversations ordered by `updatedAt` |
| `POST` | `/api/conversations` | Create a new conversation |
| `GET` | `/api/conversations/<id>` | Fetch single conversation details |
| `PATCH` | `/api/conversations/<id>` | Rename conversation title |
| `DELETE` | `/api/conversations/<id>` | Delete conversation and its messages |
| `GET` | `/api/conversations/<id>/messages` | Fetch chronological message list for conversation |
| `GET` | `/api/memories` | Fetch user's stored long-term memories |
| `DELETE` | `/api/memories/<id>` | Delete single long-term memory |
| `DELETE` | `/api/memories` | Clear all long-term memories for user |
| `GET` | `/api/settings/memory` | Get user memory toggle settings |
| `PATCH` | `/api/settings/memory` | Toggle memory extraction (`enabled: boolean`) |

---

## ⚙️ Environment Variables Setup

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
FIREBASE_CREDENTIALS_PATH=firebase-key.json
```

> **Note**: Place your Firebase Admin SDK Service Account key at `firebase-key.json` in the root folder.

---

## 💻 Local Development Setup

1. **Clone Repository**:
   ```bash
   git clone <repository-url>
   cd AI-Chatbot
   ```

2. **Setup Virtual Environment**:
   ```bash
   python -m venv .venv
   
   # Windows (PowerShell)
   .\.venv\Scripts\activate
   
   # Linux/macOS
   source .venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Application**:
   ```bash
   python app.py
   ```
   Open [http://localhost:5000](http://localhost:5000) in your web browser.

---

## 🛡️ Security & Privacy Notes

1. **API Key Protection**: Groq API Key and Firebase Admin secret credentials are strictly server-side.
2. **User Data Isolation**: Every Firestore query validates ownership (`userId == request.auth.uid`). Frontend-supplied user IDs are ignored; authenticated UID is derived directly from verified JWT tokens.
3. **Memory Safety Filters**: Sensitive items (passwords, tokens, credentials, financial numbers) are strictly excluded from memory storage.

---

## 📄 License

This project is licensed under the MIT License.
