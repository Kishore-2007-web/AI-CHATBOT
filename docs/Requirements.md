# Software Requirements Specification (SRS)

## Functional Requirements

### FR-01

The application shall display a chatbot webpage.

### FR-02

The user shall be able to enter a text message.

### FR-03

The user shall be able to submit the message.

### FR-04

The frontend shall send the message to the backend using HTTP POST.

### FR-05

The backend shall receive the request.

### FR-06

The backend shall send the user's prompt to the Groq API.

### FR-07

The backend shall receive the AI response.

### FR-08

The backend shall return the AI response as JSON.

### FR-09

The frontend shall display the AI response.

---

## Non-Functional Requirements

### Performance

* Average response time should be under 5 seconds.

### Security

* API keys must never be exposed to the frontend.
* Environment variables shall store sensitive information.

### Usability

* The interface should be simple and intuitive.
* No login should be required for Version 1.

### Compatibility

* Latest Chrome
* Microsoft Edge
* Firefox

### Maintainability

* Code should be modular.
* Documentation should remain updated.

### Scalability

The architecture should support future additions such as:

* User authentication
* Database
* Conversation history
* Multiple AI models
* Streaming responses

---

## Constraints

* HTML
* CSS
* JavaScript
* Python
* Flask
* Groq API

No database will be used in Version 1.
