# CloudPad

## Project Overview
CloudPad is a real-time, cloud-based notepad that allows users to create, edit, and save notes using unique URLs. Users can also upload and store files (PDFs, Word documents, images, audio, etc.), which are linked to specific notes. The project leverages **React** for the frontend and **Firebase (Firestore & Storage)** for backend and real-time syncing.

## Features
- **Unique URL-Based Notes**: Users can access and create notes via dynamic URLs (e.g., `yourwebsite.com/mynote`).
- **Real-Time Synchronization**: Notes update live across multiple devices using Firebase Firestore.
- **File Upload & Storage**: Supports file uploads (PDFs, images, Word documents, etc.) stored in Firebase Storage.
- **Auto-Saving**: Text changes are automatically saved in Firestore.
- **Drag & Drop File Upload**: Users can easily drag and drop files to upload.
- **Free Hosting & Backend**: Uses Firebase Hosting and Firestore, eliminating the need for a structured backend.

## Tech Stack
- **Frontend**: React, React Router, Tailwind CSS (optional for styling)
- **Backend**: Firebase Firestore (NoSQL database)
- **File Storage**: Firebase Storage
- **Authentication** (Future Enhancement): Firebase Authentication (optional for private notes)

## Project Setup Guide
### 1. Firebase Setup
1. Go to [Firebase Console](https://console.firebase.google.com/) and create a new project.
2. Enable Firestore Database in "Test Mode."
3. Enable Firebase Storage to allow file uploads.
4. Register your app (Web App) and obtain Firebase config settings.
5. Install Firebase SDK in your React project:
   ```bash
   npm install firebase
   ```
6. Create a `firebase.js` file in your `src` directory and configure Firebase:
   ```javascript
   import { initializeApp } from "firebase/app";
   import { getFirestore } from "firebase/firestore";
   import { getStorage } from "firebase/storage";

   const firebaseConfig = {
     apiKey: "YOUR_API_KEY",
     authDomain: "YOUR_AUTH_DOMAIN",
     projectId: "YOUR_PROJECT_ID",
     storageBucket: "YOUR_STORAGE_BUCKET",
     messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
     appId: "YOUR_APP_ID"
   };

   const app = initializeApp(firebaseConfig);
   export const db = getFirestore(app);
   export const storage = getStorage(app);
   ```

### 2. React Project Setup
1. Create a React project:
   ```bash
   npx create-react-app cloudpad
   cd cloudpad
   ```
2. Install dependencies:
   ```bash
   npm install react-router-dom firebase react-dropzone
   ```
3. Implement `NotePage.js` (handles text editing & file uploads).
4. Configure **React Router** to handle dynamic URLs.

### 3. Running the Project
Start the development server:
```bash
npm start
```
Ensure Firebase setup is correctly linked.

## Future Enhancements
- **User Authentication**: Allow users to create and manage personal notes.
- **Note Sharing**: Enable public/private sharing settings.
- **Advanced File Handling**: Support folders and file previews.
- **Dark Mode**: UI theme switcher.

## Mentor Feedback
We appreciate any feedback on:
- Best practices for structuring Firestore data.
- Efficient file handling in Firebase Storage.
- Security considerations for public and private notes.

---
🚀 **Goal:** A simple, accessible, and cloud-synced notepad with file storage!

