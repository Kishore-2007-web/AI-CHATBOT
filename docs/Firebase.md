# Firebase Integration Guide

This document explains the Firebase configuration for **AI Chatbot v2.0**, including Authentication, Firestore Database, and Admin SDK credentials management.

---

## 1. Firebase Architecture Overview

```text
Browser Client (Frontend)
   ↓  (Sends Auth Token in Authorization Header)
Flask Backend (Python)
   ↓  (1. Admin SDK Verifies Token)
   ↓  (2. Interacts with Cloud Firestore)
Cloud Firestore & Groq API
```

---

## 2. Prerequisites & Services Enabled

1. **Firebase Project**: Created via [Firebase Console](https://console.firebase.google.com/).
2. **Firebase Authentication**: Enabled with **Email/Password** sign-in provider.
3. **Cloud Firestore**: Provisioned in Production mode.
4. **Firebase Admin SDK**: Service Account key generated and downloaded.

---

## 3. Environment Variables Configuration

The Firebase Admin SDK credentials must be stored securely and never committed to version control.

### Option A: Local Credentials File (Recommended for Development)
Place the downloaded JSON file in the root folder as `firebase-key.json` (which is gitignored).

Add the following to your `.env` file:
```env
FIREBASE_CREDENTIALS_PATH=firebase-key.json
```

### Option B: Inline Environment Variables (Recommended for Production Deployment)
If deploying to platforms like Render, Heroku, or Vercel:
```env
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxx@your-project-id.iam.gserviceaccount.com
```

---

## 4. Backend Initialization Logic

In `app.py`, Firebase Admin SDK is initialized as follows:

```python
import os
import firebase_admin
from firebase_admin import credentials, auth, firestore

# Initialize Firebase Admin SDK
cred_path = os.environ.get("FIREBASE_CREDENTIALS_PATH", "firebase-key.json")

if os.path.exists(cred_path):
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firebase Admin SDK initialized successfully.")
else:
    db = None
    print(f"Warning: Firebase credentials file not found at {cred_path}.")
```

---

## 5. Security Checklist

- [x] Service account private key is added to `.gitignore`.
- [x] Frontend browser does NOT communicate with Groq directly.
- [x] Admin SDK credentials loaded via environment variables or gitignored file.
- [x] Flask backend handles token verification and database operations.
