import { getAuthToken } from "./auth.js";

const button = document.getElementById("send-btn");
const input = document.getElementById("user-input");
const chatBox = document.getElementById("chat-box");

function addMessage(message, type) {
    const div = document.createElement("div");
    div.className = "message " + type;
    div.innerHTML = marked.parse(message);
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
    const message = input.value.trim();
    if (message === "") return;

    // Get Auth token
    const token = await getAuthToken();
    if (!token) {
        addMessage("Please sign in to send messages.", "bot");
        return;
    }

    addMessage(message, "user");
    input.value = "";

    const loading = document.createElement("div");
    loading.className = "message bot";
    loading.textContent = "Kisa is thinking...";
    chatBox.appendChild(loading);
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                message: message
            })
        });

        const data = await response.json();
        loading.remove();

        if (response.ok) {
            addMessage(data.reply, "bot");
        } else {
            addMessage(`Error (${response.status}): ${data.error || "Failed to process message."}`, "bot");
        }
    } catch (error) {
        console.error("Chat Error:", error);
        loading.remove();
        addMessage("Something went wrong. Please check your connection and try again.", "bot");
    }
}

if (button) {
    button.addEventListener("click", sendMessage);
}

if (input) {
    input.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    });
}