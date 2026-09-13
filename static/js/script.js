import { getAuthToken } from "./auth.js";
import { getActiveConversationId, setActiveConversationId, fetchUserConversations } from "./conversations.js";

const input = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const chatBox = document.getElementById("chat-box");
const welcomeScreen = document.getElementById("welcome-screen");

// Configure Marked.js renderer for code blocks with Copy buttons & Syntax Highlighting
const renderer = new marked.Renderer();
renderer.code = function(code, language) {
    const validLang = language && typeof hljs !== 'undefined' && hljs.getLanguage(language) ? language : 'text';
    let highlighted = escapeHtml(code);

    if (validLang !== 'text' && typeof hljs !== 'undefined') {
        try {
            highlighted = hljs.highlight(code, { language: validLang }).value;
        } catch (e) {
            console.warn("Highlight error:", e);
        }
    }

    const encodedCode = encodeURIComponent(code);
    return `
        <div class="code-block-wrapper">
            <div class="code-block-header">
                <span>${validLang}</span>
                <button class="copy-code-btn" data-code="${encodedCode}">Copy Code</button>
            </div>
            <pre><code class="hljs language-${validLang}">${highlighted}</code></pre>
        </div>
    `;
};

marked.setOptions({ renderer: renderer, breaks: true });

// Attach event listener for dynamic Code Copy buttons
document.addEventListener("click", (e) => {
    if (e.target.classList.contains("copy-code-btn")) {
        const rawCode = decodeURIComponent(e.target.dataset.code || "");
        navigator.clipboard.writeText(rawCode).then(() => {
            const origText = e.target.textContent;
            e.target.textContent = "Copied!";
            setTimeout(() => e.target.textContent = origText, 2000);
        });
    }
});

export function resetChatToWelcome() {
    if (chatBox) {
        chatBox.innerHTML = "";
        chatBox.classList.add("hidden");
    }
    if (welcomeScreen) {
        welcomeScreen.classList.remove("hidden");
    }
}

export async function loadConversationMessages(convId) {
    const token = await getAuthToken();
    if (!token || !convId) return;

    try {
        const response = await fetch(`/api/conversations/${convId}/messages`, {
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (response.ok) {
            const data = await response.json();
            const messages = data.messages || [];

            chatBox.innerHTML = "";
            if (messages.length > 0) {
                if (welcomeScreen) welcomeScreen.classList.add("hidden");
                chatBox.classList.remove("hidden");

                messages.forEach(msg => {
                    renderMessageElement(msg.content, msg.role, msg.id);
                });
                chatBox.scrollTop = chatBox.scrollHeight;
            } else {
                resetChatToWelcome();
            }
        }
    } catch (error) {
        console.error("Error loading conversation messages:", error);
    }
}

export function renderMessageElement(content, role, messageId = null) {
    if (welcomeScreen) welcomeScreen.classList.add("hidden");
    if (chatBox) chatBox.classList.remove("hidden");

    const wrapper = document.createElement("div");
    wrapper.className = `message-wrapper ${role === "user" ? "user" : "bot"}`;
    if (messageId) wrapper.dataset.id = messageId;

    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${role === "user" ? "user" : "bot"}`;
    
    // Parse Markdown safely
    msgDiv.innerHTML = marked.parse(content);

    // Actions bar (Copy, Edit, Regenerate)
    const actionsDiv = document.createElement("div");
    actionsDiv.className = "message-actions";

    const copyBtn = document.createElement("button");
    copyBtn.className = "msg-action-btn";
    copyBtn.textContent = "Copy";
    copyBtn.addEventListener("click", () => {
        navigator.clipboard.writeText(content).then(() => {
            copyBtn.textContent = "Copied!";
            setTimeout(() => copyBtn.textContent = "Copy", 2000);
        });
    });
    actionsDiv.appendChild(copyBtn);

    if (role === "user") {
        const editBtn = document.createElement("button");
        editBtn.className = "msg-action-btn";
        editBtn.textContent = "Edit";
        editBtn.addEventListener("click", () => handleEditUserMessage(messageId, content));
        actionsDiv.appendChild(editBtn);
    } else if (role === "assistant" || role === "bot") {
        const regenBtn = document.createElement("button");
        regenBtn.className = "msg-action-btn";
        regenBtn.textContent = "Regenerate";
        regenBtn.addEventListener("click", () => handleRegenerateAssistantMessage(messageId));
        actionsDiv.appendChild(regenBtn);
    }

    wrapper.appendChild(msgDiv);
    wrapper.appendChild(actionsDiv);
    chatBox.appendChild(wrapper);

    chatBox.scrollTop = chatBox.scrollHeight;
    return wrapper;
}

async function sendMessage(overrideText = null) {
    const message = overrideText || input.value.trim();
    if (message === "") return;

    const token = await getAuthToken();
    if (!token) return;

    if (!overrideText && input) {
        input.value = "";
        autoExpandTextarea(input);
    }

    // Render User message immediately in UI
    renderMessageElement(message, "user");

    // Add Loading Indicator
    const loadingWrapper = document.createElement("div");
    loadingWrapper.className = "message-wrapper bot";
    loadingWrapper.innerHTML = `
        <div class="message bot">
            <em>Kisa is thinking...</em>
        </div>
    `;
    chatBox.appendChild(loadingWrapper);
    chatBox.scrollTop = chatBox.scrollHeight;

    // Lock send button
    if (sendBtn) sendBtn.disabled = true;

    try {
        const activeConvId = getActiveConversationId();

        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                message: message,
                conversation_id: activeConvId
            })
        });

        const data = await response.json();
        loadingWrapper.remove();

        if (response.ok) {
            // Update active conversation ID if newly created
            if (!activeConvId && data.conversation_id) {
                setActiveConversationId(data.conversation_id);
            }

            renderMessageElement(data.reply, "assistant", data.bot_message_id);
            fetchUserConversations();
        } else {
            renderMessageElement(`Error (${response.status}): ${data.error || "Failed to process request."}`, "bot");
        }
    } catch (error) {
        console.error("Chat Request Error:", error);
        loadingWrapper.remove();
        renderMessageElement("Something went wrong. Please check your connection and try again.", "bot");
    } finally {
        if (sendBtn) sendBtn.disabled = false;
    }
}

async function handleEditUserMessage(messageId, currentText) {
    const newText = prompt("Edit your message:", currentText);
    if (!newText || newText.trim() === "" || newText.trim() === currentText) return;

    const activeConvId = getActiveConversationId();
    const token = await getAuthToken();
    if (!token || !activeConvId || !messageId) return;

    try {
        // Find wrapper element in DOM and remove subsequent message wrappers
        const wrappers = Array.from(chatBox.querySelectorAll(".message-wrapper"));
        const index = wrappers.findIndex(w => w.dataset.id === messageId);
        if (index !== -1) {
            for (let i = index; i < wrappers.length; i++) {
                wrappers[i].remove();
            }
        }

        // Send edit request to backend
        const response = await fetch("/api/chat/edit", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                conversation_id: activeConvId,
                message_id: messageId,
                new_message: newText.trim()
            })
        });

        const data = await response.json();
        if (response.ok) {
            renderMessageElement(newText.trim(), "user", data.user_message_id);
            renderMessageElement(data.reply, "assistant", data.bot_message_id);
            fetchUserConversations();
        }
    } catch (error) {
        console.error("Edit message error:", error);
    }
}

async function handleRegenerateAssistantMessage(assistantMessageId) {
    const activeConvId = getActiveConversationId();
    const token = await getAuthToken();
    if (!token || !activeConvId || !assistantMessageId) return;

    try {
        // Remove target assistant message from DOM
        const wrapper = chatBox.querySelector(`.message-wrapper[data-id="${assistantMessageId}"]`);
        if (wrapper) wrapper.remove();

        // Loading indicator
        const loadingWrapper = document.createElement("div");
        loadingWrapper.className = "message-wrapper bot";
        loadingWrapper.innerHTML = `<div class="message bot"><em>Kisa is regenerating response...</em></div>`;
        chatBox.appendChild(loadingWrapper);

        const response = await fetch("/api/chat/regenerate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                conversation_id: activeConvId,
                message_id: assistantMessageId
            })
        });

        const data = await response.json();
        loadingWrapper.remove();

        if (response.ok) {
            renderMessageElement(data.reply, "assistant", data.bot_message_id);
        }
    } catch (error) {
        console.error("Regenerate response error:", error);
    }
}

function autoExpandTextarea(el) {
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 140) + "px";
}

function escapeHtml(str) {
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

document.addEventListener("DOMContentLoaded", () => {
    if (sendBtn) {
        sendBtn.addEventListener("click", () => sendMessage());
    }

    if (input) {
        input.addEventListener("input", () => autoExpandTextarea(input));
        input.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    // Attach click listeners to Welcome Prompt Suggestion Chips
    document.querySelectorAll(".suggestion-chip").forEach(chip => {
        chip.addEventListener("click", () => {
            const promptText = chip.dataset.prompt;
            if (promptText) {
                sendMessage(promptText);
            }
        });
    });
});