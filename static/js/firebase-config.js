// Firebase Web JS SDK Configuration
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.8.0/firebase-app.js";
import { 
    getAuth, 
    createUserWithEmailAndPassword, 
    signInWithEmailAndPassword, 
    signOut, 
    onAuthStateChanged,
    updateProfile
} from "https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js";

// Web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyBpI93SwmegqRm-p4TFMjdLy7DXE0gWfWU",
  authDomain: "kisa-ai-c0b1e.firebaseapp.com",
  projectId: "kisa-ai-c0b1e",
  storageBucket: "kisa-ai-c0b1e.firebasestorage.app",
  messagingSenderId: "52450586947",
  appId: "1:52450586947:web:a639aa35d25e9247a9fff6",
  measurementId: "G-WMTBJ3HL3N"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

export { 
    app, 
    auth, 
    createUserWithEmailAndPassword, 
    signInWithEmailAndPassword, 
    signOut, 
    onAuthStateChanged,
    updateProfile
};
