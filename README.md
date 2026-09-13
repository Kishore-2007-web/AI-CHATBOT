# AI Chatbot v2.0

A production-style full-stack AI web application featuring **Firebase Authentication**, **Cloud Firestore Database**, **Python Flask**, and **Groq AI**.

> **Project Status:** 🚧 In Development (Version 2.0.0 - Phase 3: Firestore Database Architecture Complete)

---

## Project Goal

The purpose of this project is to build a scalable, secure AI chat platform featuring:

* User Authentication (Email & Password via Firebase Auth)
* Persistent Chat Database (Cloud Firestore)
* Multi-conversation ChatGPT-style drawer & history management
* Backend Security (Token verification & API key isolation)
* Professional REST API communication (Python & Flask)
* High-speed AI inference (Groq API with Llama 3.3 model)

---

## Features

### Version 2.0.0 (Phase 3 Complete)

* **Cloud Firestore Database Layer**: Database service module ([db_service.py](file:///d:/from-c-drive/OneDrive/Desktop/AI%20chatbot/db_service.py)) for `users`, `conversations`, and `messages` collections
* **Automatic Profile Creation**: Auto-syncing user profiles in Firestore upon authentication
* **Audit Timestamps**: UTC ISO timestamps (`createdAt`, `updatedAt`) for document tracking
* **Database Documentation**: Full schema specifications in [docs/Firestore-Structure.md](file:///d:/from-c-drive/OneDrive/Desktop/AI%20chatbot/docs/Firestore-Structure.md)

### Version 2.0.0 (Phase 2 Complete)

* **Firebase Authentication UI**: Email & Password Sign Up, Login, and Logout modal interface
* **Session Persistence**: Automatic login state observer (`onAuthStateChanged`)
* **Token Security**: ID Token transmission via `Authorization: Bearer <idToken>` HTTP header
* **Flask Protection**: `@require_auth` middleware verifying ID Tokens with Firebase Admin SDK
* **Documentation**: Comprehensive auth guide (`docs/Authentication.md`)

### Version 2.0.0 (Phase 1 Complete)

* Firebase Admin SDK initialization in Flask backend
* Secure credential configuration via environment variables
* Git protection for Firebase service keys
* Diagnostic `/api/health` status route
* Firebase setup documentation (`docs/Firebase.md`)


### Version 1.0.0

* AI Chatbot interface (HTML/CSS/JS)
* Flask REST backend with Groq API integration
* Markdown rendering & loading indicators


---

## Technology Stack

### Frontend

* HTML5
* CSS3
* JavaScript (ES6)

### Backend

* Python
* Flask

### AI

* Groq API
* Llama 3.3 70B Versatile

### Development Tools

* VS Code
* Git
* GitHub

---

## Project Structure

```text
AI-Chatbot/
│
├── app.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md
├── LICENSE
│
├── docs/
├── static/
├── templates/
├── tests/
└── screenshots/
```

---

## Development Workflow

1. Plan
2. Document
3. Develop
4. Test
5. Commit
6. Push to GitHub

---

## Installation

```bash
git clone <repository-url>

cd AI-Chatbot

python -m venv .venv

# Windows
.\.venv\Scripts\activate

pip install -r requirements.txt
```

---

## Current Version

**v0.1.0**

Status: Planning & Project Initialization

---

## Roadmap

* [x] Initialize repository
* [x] Create folder structure
* [x] Connect GitHub
* [ ] Create Flask backend
* [ ] Build frontend
* [ ] Connect frontend to backend
* [ ] Integrate Groq API
* [ ] Improve UI
* [ ] Add chat history
* [ ] Deploy project

---

## License

This project is licensed under the MIT License.

---

## Author

Developed as a learning project to understand modern full-stack web development and AI integration.
