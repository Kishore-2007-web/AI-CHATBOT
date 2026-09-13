import { 
    auth, 
    googleProvider,
    createUserWithEmailAndPassword, 
    signInWithEmailAndPassword, 
    signInWithPopup,
    signOut, 
    onAuthStateChanged 
} from "./firebase-config.js";
import { fetchUserConversations, createNewConversation } from "./conversations.js";
import { fetchMemorySettings } from "./memory.js";

let currentUser = null;

// Auth Modal & UI elements
const authModal = document.getElementById("auth-modal");
const authForm = document.getElementById("auth-form");
const authTitle = document.getElementById("auth-title");
const authSubmitBtn = document.getElementById("auth-submit-btn");
const authToggleBtn = document.getElementById("auth-toggle-btn");
const googleSignInBtn = document.getElementById("google-signin-btn");
const authError = document.getElementById("auth-error");
const emailInput = document.getElementById("auth-email");
const passwordInput = document.getElementById("auth-password");

const userProfileBar = document.getElementById("user-profile-bar");
const userEmailDisplay = document.getElementById("user-email-display");
const logoutBtn = document.getElementById("logout-btn");

const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");

let isSignUpMode = false;

// Handle Email/Password Form Submission
if (authForm) {
    authForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const email = emailInput.value.trim();
        const password = passwordInput.value.trim();

        if (!email || !password) {
            showError("Please enter both email and password.");
            return;
        }

        if (isSignUpMode) {
            showError("Sign up is currently disabled. Please sign in with an existing account.");
            return;
        }

        authError.classList.add("hidden");
        authSubmitBtn.disabled = true;
        authSubmitBtn.textContent = "Signing In...";

        try {
            await signInWithEmailAndPassword(auth, email, password);
            emailInput.value = "";
            passwordInput.value = "";
        } catch (error) {
            console.error("Auth Error:", error);
            showError(getFriendlyErrorMessage(error.code, error.message));
        } finally {
            authSubmitBtn.disabled = false;
            authSubmitBtn.textContent = "Sign In";
        }
    });
}

// Handle Google OAuth Sign In
if (googleSignInBtn) {
    googleSignInBtn.addEventListener("click", async () => {
        authError.classList.add("hidden");
        googleSignInBtn.disabled = true;

        try {
            console.log("[Auth] Initiating Google Sign In Popup...");
            await signInWithPopup(auth, googleProvider);
        } catch (error) {
            console.error("Google Auth Error:", error);
            if (error.code !== "auth/popup-closed-by-user") {
                showError(getFriendlyErrorMessage(error.code, error.message));
            }
        } finally {
            googleSignInBtn.disabled = false;
        }
    });
}

// Handle Logout
if (logoutBtn) {
    logoutBtn.addEventListener("click", async () => {
        try {
            await signOut(auth);
        } catch (error) {
            console.error("Logout Error:", error);
        }
    });
}

// Auth State Observer
onAuthStateChanged(auth, (user) => {
    currentUser = user;

    if (user) {
        // User is logged in
        if (authModal) authModal.classList.add("hidden");
        if (userProfileBar) userProfileBar.classList.remove("hidden");
        if (userEmailDisplay) userEmailDisplay.textContent = user.email || user.displayName || "Google User";

        // Enable chat inputs
        if (userInput) {
            userInput.disabled = false;
            userInput.placeholder = "Message Kisa...";
        }
        if (sendBtn) sendBtn.disabled = false;

        // Fetch conversations & memory settings for authenticated user
        fetchUserConversations();
        fetchMemorySettings();

        console.log("[Auth] User logged in:", user.email);
    } else {
        // User is logged out
        if (authModal) authModal.classList.remove("hidden");
        if (userProfileBar) userProfileBar.classList.add("hidden");
        if (userEmailDisplay) userEmailDisplay.textContent = "";

        // Disable chat inputs
        if (userInput) {
            userInput.disabled = true;
            userInput.placeholder = "Please sign in to chat...";
        }
        if (sendBtn) sendBtn.disabled = true;

        createNewConversation();
        console.log("[Auth] User logged out.");
    }
});

// Helper: Get JWT ID Token for API requests
export async function getAuthToken() {
    if (!currentUser) return null;
    try {
        return await currentUser.getIdToken();
    } catch (error) {
        console.error("Failed to get ID token:", error);
        return null;
    }
}

export function getCurrentUser() {
    return currentUser;
}

function showError(msg) {
    if (authError) {
        authError.textContent = msg;
        authError.classList.remove("hidden");
    }
}

function getFriendlyErrorMessage(code, rawMessage) {
    switch (code) {
        case "auth/email-already-in-use":
            return "This email is already registered. Please sign in.";
        case "auth/invalid-email":
            return "Invalid email address format.";
        case "auth/weak-password":
            return "Password should be at least 6 characters long.";
        case "auth/user-not-found":
        case "auth/wrong-password":
        case "auth/invalid-credential":
            return "Invalid email or password.";
        case "auth/popup-closed-by-user":
            return "Google sign-in popup was closed.";
        case "auth/account-exists-with-different-credential":
            return "An account already exists with the same email using a different sign-in method.";
        case "auth/too-many-requests":
            return "Too many failed attempts. Please try again later.";
        case "auth/operation-not-allowed":
            return "Sign-in method is not enabled in Firebase Console (Authentication -> Sign-in method).";
        case "auth/unauthorized-domain":
            return "Domain not authorized in Firebase Console. Try opening http://localhost:5000 instead of 127.0.0.1.";
        case "auth/network-request-failed":
            return "Network error. Please check your internet connection.";
        default:
            return code ? `Authentication failed (${code}). Please check Firebase setup.` : (rawMessage || "Authentication failed. Please try again.");
    }
}
