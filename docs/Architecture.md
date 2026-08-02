# System Architecture

## Overview

The application follows a simple Client–Server architecture.

```text
+-------------------------+
|        User             |
+-----------+-------------+
            |
            v
+-------------------------+
|  Browser (Frontend)     |
| HTML • CSS • JavaScript |
+-----------+-------------+
            |
            | HTTP POST
            v
+-------------------------+
| Flask Backend (Python)  |
+-----------+-------------+
            |
            | HTTPS Request
            v
+-------------------------+
|      Groq API           |
|   Llama 3.3 Model       |
+-----------+-------------+
            |
            | AI Response
            v
+-------------------------+
| Flask Backend           |
+-----------+-------------+
            |
            | JSON Response
            v
+-------------------------+
| Browser                 |
+-------------------------+
```

---

## Request Flow

```text
User

↓

HTML Form

↓

JavaScript

↓

fetch("/chat")

↓

Flask

↓

Groq API

↓

Flask

↓

JSON Response

↓

JavaScript

↓

Display Response
```

---

## Component Responsibilities

### Frontend

* Display user interface
* Accept user input
* Send requests
* Display responses

---

### Backend

* Receive requests
* Validate input
* Secure API key
* Communicate with Groq
* Return JSON

---

### AI Service

* Process prompts
* Generate responses
* Return generated text
