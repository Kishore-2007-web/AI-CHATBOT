import { getAuthToken } from "./auth.js";
import { loadConversationMessages, resetChatToWelcome } from "./script.js";

let activeConversationId = null;
let conversationsCache = [];

export function getActiveConversationId() {
    return activeConversationId;
}

export function setActiveConversationId(id) {
    activeConversationId = id;
}

export async function fetchUserConversations() {
    const token = await getAuthToken();
    if (!token) return [];

    try {
        const response = await fetch("/api/conversations", {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
        if (response.ok) {
            const data = await response.json();
            conversationsCache = data.conversations || [];
            renderConversationsList(conversationsCache);
            return conversationsCache;
        }
    } catch (error) {
        console.error("Failed to fetch conversations:", error);
    }
    return [];
}

export function groupConversationsByDate(conversations) {
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    const groups = {
        Today: [],
        Yesterday: [],
        Older: []
    };

    conversations.forEach(conv => {
        const date = new Date(conv.updatedAt || conv.createdAt);
        if (date.toDateString() === today.toDateString()) {
            groups.Today.push(conv);
        } else if (date.toDateString() === yesterday.toDateString()) {
            groups.Yesterday.push(conv);
        } else {
            groups.Older.push(conv);
        }
    });

    return groups;
}

export function renderConversationsList(conversations) {
    const container = document.getElementById("conversation-list");
    if (!container) return;

    container.innerHTML = "";
    if (!conversations || conversations.length === 0) {
        container.innerHTML = `<div class="empty-memory-text">No conversations yet. Click 'New Chat' to start!</div>`;
        return;
    }

    const grouped = groupConversationsByDate(conversations);

    for (const [groupName, convs] of Object.entries(grouped)) {
        if (convs.length === 0) continue;

        const header = document.createElement("div");
        header.className = "date-group-header";
        header.textContent = groupName;
        container.appendChild(header);

        convs.forEach(conv => {
            const item = document.createElement("div");
            item.className = `conv-item ${conv.id === activeConversationId ? "active" : ""}`;
            item.dataset.id = conv.id;

            item.innerHTML = `
                <span class="conv-title">${escapeHtml(conv.title || "New Conversation")}</span>
                <div class="conv-actions">
                    <button class="conv-action-btn rename-btn" title="Rename">✏️</button>
                    <button class="conv-action-btn delete-btn" title="Delete">🗑️</button>
                </div>
            `;

            // Click to select conversation
            item.addEventListener("click", (e) => {
                if (e.target.closest(".conv-actions")) return;
                selectConversation(conv.id, conv.title);
            });

            // Action: Rename
            const renameBtn = item.querySelector(".rename-btn");
            renameBtn.addEventListener("click", (e) => {
                e.stopPropagation();
                handleRenameConversation(conv.id, conv.title);
            });

            // Action: Delete
            const deleteBtn = item.querySelector(".delete-btn");
            deleteBtn.addEventListener("click", (e) => {
                e.stopPropagation();
                handleDeleteConversation(conv.id);
            });

            container.appendChild(item);
        });
    }
}

export async function selectConversation(convId, title = "Kisa AI Assistant") {
    activeConversationId = convId;
    
    // Update active class in sidebar
    document.querySelectorAll(".conv-item").forEach(el => {
        el.classList.toggle("active", el.dataset.id === convId);
    });

    // Update Header title
    const titleDisplay = document.getElementById("chat-title-display");
    if (titleDisplay) {
        titleDisplay.textContent = title || "Kisa AI Assistant";
    }

    // Close mobile sidebar if open
    closeMobileSidebar();

    // Load messages from backend
    await loadConversationMessages(convId);
}

export async function createNewConversation() {
    activeConversationId = null;
    resetChatToWelcome();
    
    const titleDisplay = document.getElementById("chat-title-display");
    if (titleDisplay) {
        titleDisplay.textContent = "Kisa AI Assistant";
    }

    document.querySelectorAll(".conv-item").forEach(el => el.classList.remove("active"));
    closeMobileSidebar();
}

async function handleRenameConversation(convId, currentTitle) {
    const newTitle = prompt("Enter new conversation title:", currentTitle);
    if (!newTitle || newTitle.trim() === "" || newTitle.trim() === currentTitle) return;

    const token = await getAuthToken();
    if (!token) return;

    try {
        const response = await fetch(`/api/conversations/${convId}`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ title: newTitle.trim() })
        });

        if (response.ok) {
            fetchUserConversations();
            if (activeConversationId === convId) {
                const titleDisplay = document.getElementById("chat-title-display");
                if (titleDisplay) titleDisplay.textContent = newTitle.trim();
            }
        }
    } catch (error) {
        console.error("Error renaming conversation:", error);
    }
}

async function handleDeleteConversation(convId) {
    if (!confirm("Are you sure you want to delete this conversation?")) return;

    const token = await getAuthToken();
    if (!token) return;

    try {
        const response = await fetch(`/api/conversations/${convId}`, {
            method: "DELETE",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (response.ok) {
            if (activeConversationId === convId) {
                createNewConversation();
            }
            fetchUserConversations();
        }
    } catch (error) {
        console.error("Error deleting conversation:", error);
    }
}

function filterConversations(query) {
    const q = query.toLowerCase().trim();
    if (!q) {
        renderConversationsList(conversationsCache);
        return;
    }
    const filtered = conversationsCache.filter(c => (c.title || "").toLowerCase().includes(q));
    renderConversationsList(filtered);
}

function closeMobileSidebar() {
    const sidebar = document.getElementById("sidebar");
    const backdrop = document.getElementById("sidebar-backdrop");
    if (sidebar) sidebar.classList.remove("open");
    if (backdrop) backdrop.classList.add("hidden");
}

function toggleMobileSidebar() {
    const sidebar = document.getElementById("sidebar");
    const backdrop = document.getElementById("sidebar-backdrop");
    if (sidebar) sidebar.classList.toggle("open");
    if (backdrop) backdrop.classList.toggle("hidden");
}

function escapeHtml(str) {
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

// Attach Sidebar Event Listeners
document.addEventListener("DOMContentLoaded", () => {
    const newChatBtn = document.getElementById("new-chat-btn");
    if (newChatBtn) {
        newChatBtn.addEventListener("click", createNewConversation);
    }

    const searchInput = document.getElementById("conv-search-input");
    if (searchInput) {
        searchInput.addEventListener("input", (e) => filterConversations(e.target.value));
    }

    const sidebarToggleBtn = document.getElementById("sidebar-toggle-btn");
    if (sidebarToggleBtn) {
        sidebarToggleBtn.addEventListener("click", toggleMobileSidebar);
    }

    const backdrop = document.getElementById("sidebar-backdrop");
    if (backdrop) {
        backdrop.addEventListener("click", closeMobileSidebar);
    }
});
