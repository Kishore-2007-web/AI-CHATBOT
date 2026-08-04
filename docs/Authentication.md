# Authentication Architecture & Session Guide

This document describes the **Firebase Authentication** architecture, user session lifecycle, token transmission, and backend security middleware implemented in **Phase 2**.

---

## 1. Authentication Lifecycle & Token Flow

```text
Browser Client
   │
   ├── 1. User enters Email & Password in Auth Modal
   ├── 2. Client calls signInWithEmailAndPassword() or createUserWithEmailAndPassword()
   ├── 3. Firebase Auth returns UserCredential object containing User ID & JWT ID Token
   │
   ├── 4. onAuthStateChanged listener unlocks Chat UI and displays user email
   │
   ├── 5. On every API request:
   │      - Client calls user.getIdToken()
   │      - Passes header: "Authorization: Bearer <idToken>"
   ▼
Flask Backend (@require_auth)
   │
   ├── 6. Extracts Bearer token from request.headers
   ├── 7. Verifies token signature via firebase_admin.auth.verify_id_token(id_token)
   ├── 8. Attaches decoded user claim to g.user
   └── 9. Proceeds to execute endpoint (/chat)
```

---

## 2. Frontend Configuration (`static/js/firebase-config.js` & `static/js/auth.js`)

- **Config File**: `firebase-config.js` exports the initialized Firebase Web App and Auth module.
- **Auth Controller**: `auth.js` manages:
  - Sign Up & Sign In toggle forms
  - Error translation for invalid passwords/duplicate emails
  - Persistent login state via `onAuthStateChanged`
  - Token acquisition helper `getAuthToken()`

---

## 3. Backend Verification (`app.py`)

The `@require_auth` decorator wraps protected API routes:

```python
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        
        id_token = auth_header.split("Bearer ")[1].strip()
        decoded_token = auth.verify_id_token(id_token)
        g.user = decoded_token
        return f(*args, **kwargs)
    return decorated_function
```

---

## 4. Security Highlights

1. **Token Expiration**: Firebase ID Tokens expire after 1 hour. The client SDK automatically refreshes tokens in the background when `user.getIdToken()` is invoked.
2. **Revocation Check**: The backend verifies token integrity cryptographically using Firebase's public keys.
3. **Protected Endpoints**: Unauthenticated HTTP requests to `/chat` immediately fail with HTTP 401 Unauthorized.
