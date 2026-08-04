## v2.0.0-phase2 - Firebase Authentication (2026-08-04)

### Added
* Frontend Firebase Web JS SDK configuration ([static/js/firebase-config.js](file:///d:/from-c-drive/OneDrive/Desktop/AI%20chatbot/static/js/firebase-config.js))
* Auth controller module ([static/js/auth.js](file:///d:/from-c-drive/OneDrive/Desktop/AI%20chatbot/static/js/auth.js)) with Email & Password Sign Up, Login, and Logout
* Auth Modal overlay and User Profile Bar in [templates/index.html](file:///d:/from-c-drive/OneDrive/Desktop/AI%20chatbot/templates/index.html)
* Dark glassmorphism modal styles and responsive layout in [static/css/style.css](file:///d:/from-c-drive/OneDrive/Desktop/AI%20chatbot/static/css/style.css)
* HTTP `Authorization: Bearer <idToken>` header support in [static/js/script.js](file:///d:/from-c-drive/OneDrive/Desktop/AI%20chatbot/static/js/script.js)
* `@require_auth` decorator in [app.py](file:///d:/from-c-drive/OneDrive/Desktop/AI%20chatbot/app.py) verifying tokens with Firebase Admin SDK
* Detailed Authentication guide in [docs/Authentication.md](file:///d:/from-c-drive/OneDrive/Desktop/AI%20chatbot/docs/Authentication.md)

---

## v2.0.0-phase1 - Firebase Setup & Initialization (2026-08-04)

### Added
* Firebase Admin SDK (`firebase-admin`) integration in Flask (`app.py`)
* Environment variable configuration for Service Account credentials (`FIREBASE_CREDENTIALS_PATH`)
* Protection for credential key files (`firebase-key.json`, `*.json`) in `.gitignore`
* Diagnostic `/api/health` route in `app.py` to inspect Firebase connection status
* Firebase Architecture and Setup Guide (`docs/Firebase.md`)

---

## v1.0.0 - Initial AI Chatbot Release

### Added
* Python Flask backend with Groq API client integration (`llama-3.3-70b-versatile`)
* External system prompt loading (`prompts/kisa_system_prompt.txt`)
* Single-page chat user interface with markdown rendering and enter-key submission

---

## v0.1.0 - Project Initialization

### Added
* Git repository & folder structure
* Base documentation (`README.md`, `Architecture.md`, `Roadmap.md`)
