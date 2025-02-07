// Import the necessary Firebase SDKs
import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";
import { getStorage } from "firebase/storage";

// Your Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyD3kdDehSbSGOrWcBQFsSFoDRb6D35zRFw",
  authDomain: "cloudpad-3cc4b.firebaseapp.com",
  projectId: "cloudpad-3cc4b",
  storageBucket: "cloudpad-3cc4b.firebasestorage.app",
  messagingSenderId: "895823164435",
  appId: "1:895823164435:web:85e515912a9e21efeabbe6",
  measurementId: "G-0B9GRJJW7V"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Get Firestore and Storage services
const db = getFirestore(app);
const storage = getStorage(app);

export { db, storage };
