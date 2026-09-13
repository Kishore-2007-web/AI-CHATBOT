import { getAuthToken } from "./auth.js";

export async function fetchUserMemories() {
    const token = await getAuthToken();
    if (!token) return;

    try {
        const response = await fetch("/api/memories", {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
        if (response.ok) {
            const data = await response.json();
            renderMemoriesList(data.memories || []);
        }
    } catch (error) {
        console.error("Error fetching memories:", error);
    }
}

export function renderMemoriesList(memories) {
    const container = document.getElementById("memories-list");
    if (!container) return;

    container.innerHTML = "";
    if (!memories || memories.length === 0) {
        container.innerHTML = `<div class="empty-memory-text">No long-term memories saved yet. Talk with Kisa to save preferences!</div>`;
        return;
    }

    memories.forEach(mem => {
        const item = document.createElement("div");
        item.className = "memory-item";
        item.innerHTML = `
            <div>
                <span>${escapeHtml(mem.content)}</span>
                <span class="memory-category-tag">${escapeHtml(mem.category || "general")}</span>
            </div>
            <button class="conv-action-btn delete-mem-btn" data-id="${mem.id}" title="Delete Memory">🗑️</button>
        `;

        item.querySelector(".delete-mem-btn").addEventListener("click", () => {
            deleteSingleMemory(mem.id);
        });

        container.appendChild(item);
    });
}

async function deleteSingleMemory(memoryId) {
    const token = await getAuthToken();
    if (!token) return;

    try {
        const response = await fetch(`/api/memories/${memoryId}`, {
            method: "DELETE",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
        if (response.ok) {
            fetchUserMemories();
        }
    } catch (error) {
        console.error("Error deleting memory:", error);
    }
}

async function clearAllMemories() {
    if (!confirm("Are you sure you want to clear ALL saved memories?")) return;

    const token = await getAuthToken();
    if (!token) return;

    try {
        const response = await fetch("/api/memories", {
            method: "DELETE",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
        if (response.ok) {
            fetchUserMemories();
        }
    } catch (error) {
        console.error("Error clearing memories:", error);
    }
}

export async function fetchMemorySettings() {
    const token = await getAuthToken();
    if (!token) return;

    try {
        const response = await fetch("/api/settings/memory", {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
        if (response.ok) {
            const data = await response.json();
            const toggle = document.getElementById("memory-toggle");
            if (toggle) {
                toggle.checked = data.memoryEnabled !== false;
            }
        }
    } catch (error) {
        console.error("Error fetching memory settings:", error);
    }
}

async function updateMemoryToggleSetting(enabled) {
    const token = await getAuthToken();
    if (!token) return;

    try {
        await fetch("/api/settings/memory", {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ enabled: enabled })
        });
    } catch (error) {
        console.error("Error updating memory setting:", error);
    }
}

function openSettingsModal() {
    const modal = document.getElementById("settings-modal");
    if (modal) modal.classList.remove("hidden");
    fetchMemorySettings();
    fetchUserMemories();
}

function closeSettingsModal() {
    const modal = document.getElementById("settings-modal");
    if (modal) modal.classList.add("hidden");
}

function escapeHtml(str) {
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

document.addEventListener("DOMContentLoaded", () => {
    const settingsBtn = document.getElementById("settings-btn");
    if (settingsBtn) {
        settingsBtn.addEventListener("click", openSettingsModal);
    }

    const closeBtn = document.getElementById("close-settings-btn");
    if (closeBtn) {
        closeBtn.addEventListener("click", closeSettingsModal);
    }

    const clearBtn = document.getElementById("clear-memories-btn");
    if (clearBtn) {
        clearBtn.addEventListener("click", clearAllMemories);
    }

    const toggle = document.getElementById("memory-toggle");
    if (toggle) {
        toggle.addEventListener("change", (e) => {
            updateMemoryToggleSetting(e.target.checked);
        });
    }
});
