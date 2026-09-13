# AI Chatbot v2.0 Roadmap

## Version 1.0.0 (Legacy Single-User MVP)
* [x] Flask backend setup
* [x] Single-page HTML/CSS/JS frontend
* [x] Groq API integration (Llama 3.3 model)
* [x] Prompt management (`prompts/kisa_system_prompt.txt`)
* [x] Markdown rendering & loading indicators

---

## Version 2.0.0 (Firebase Multi-User Platform)

### Phase 1 – Firebase Setup & Configuration
* [x] Firebase Console Project Setup
* [x] Enable Email/Password Auth & Cloud Firestore
* [x] Secure Service Account Credentials in `.env`
* [x] Initialize Firebase Admin SDK in Flask (`app.py`)
* [x] Document Firebase integration (`docs/Firebase.md`)

### Phase 2 – Firebase Authentication
* [x] Frontend Auth UI (Signup, Login, Logout modals)
* [x] Session token persistence (Firebase Auth SDK on client)
* [x] Send ID Token in Authorization HTTP Header (`Bearer <token>`)
* [x] Flask `@require_auth` decorator & token verification
* [x] Document authentication architecture (`docs/Authentication.md`)

### Phase 3 – Firestore Database Architecture
* [x] Design & structure `users/`, `conversations/`, `messages/` collections
* [x] Backend document CRUD service helpers in Python (`db_service.py`)
* [x] Auto-sync user profiles upon authentication
* [x] Audit timestamps (`createdAt`, `updatedAt`) on all documents
* [x] Document Firestore structure (`docs/Firestore-Structure.md` & `docs/Database.md`)

### Phase 4 – Multiple Conversations Management
* [ ] ChatGPT-style sidebar / conversation list drawer
* [ ] New Chat creation & conversation switching
* [ ] Rename & delete conversation actions
* [ ] Sort conversation list by `updatedAt`

### Phase 5 – AI Integration & Chat Persistence
* [ ] Persist user messages to Firestore before API request
* [ ] Pass current conversation history to Groq API
* [ ] Persist AI responses to Firestore
* [ ] Return formatted JSON response to client

### Phase 6 – Security & Error Handling
* [ ] Firestore Security Rules (enforce strict `request.auth.uid == userId`)
* [ ] Token expiration and re-authentication handling
* [ ] API error handling and input sanitization

### Phase 7 – UI/UX & Responsive Polish
* [ ] Modern sidebar layout & responsive dark mode
* [ ] Auto scrolling & typing indicators

### Phase 8 – Production Documentation & Deployment
* [ ] Update all documentation (`Authentication.md`, `Firestore-Structure.md`, `Deployment.md`)
* [ ] Final release readiness
