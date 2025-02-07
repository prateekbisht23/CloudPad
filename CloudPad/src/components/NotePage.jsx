import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { db, storage } from "../firebase/firebase"; // Import the Firebase services
import { doc, setDoc, getDoc, onSnapshot } from "firebase/firestore";
import { ref, uploadBytes, getDownloadURL } from "firebase/storage";
import { useDropzone } from "react-dropzone";

const NotePage = () => {
  const { noteId } = useParams(); // Get the note ID from the URL
  const [content, setContent] = useState("");
  const [files, setFiles] = useState([]);

  useEffect(() => {
    if (!noteId) return;
    const noteRef = doc(db, "notes", noteId);
    
    const fetchNote = async () => {
      try {
        const docSnap = await getDoc(noteRef);
        if (!docSnap.exists()) {
          await setDoc(noteRef, { content: "", files: [] });
        }
      } catch (error) {
        console.error("Error fetching note:", error);
      }
    };

    fetchNote();
    
    const unsubscribe = onSnapshot(noteRef, (doc) => {
      if (doc.exists()) {
        setContent(doc.data().content);
        setFiles(doc.data().files || []);
      }
    }, (error) => {
      console.error("Error in real-time sync:", error);
    });

    return () => unsubscribe();
  }, [noteId]);

  const handleContentChange = async (e) => {
    const newContent = e.target.value;
    setContent(newContent);
    try {
      await setDoc(doc(db, "notes", noteId), { content: newContent, files }, { merge: true });
    } catch (error) {
      console.error("Error saving content:", error);
    }
  };

  const onDrop = async (acceptedFiles) => {
    if (!acceptedFiles.length) return;
    const file = acceptedFiles[0];
    const storageRef = ref(storage, `notes/${noteId}/${file.name}`);
    try {
      await uploadBytes(storageRef, file);
      const fileURL = await getDownloadURL(storageRef);
      
      const newFile = { name: file.name, url: fileURL, size: file.size, type: file.type };
      const updatedFiles = [...files, newFile];
      setFiles(updatedFiles);
      await setDoc(doc(db, "notes", noteId), { content, files: updatedFiles }, { merge: true });
    } catch (error) {
      console.error("Error uploading file:", error);
    }
  };

  const { getRootProps, getInputProps } = useDropzone({ onDrop });

  return (
    <div className="container">
      <h2>Note: {noteId}</h2>
      <textarea value={content} onChange={handleContentChange} placeholder="Start typing..." />
      <div {...getRootProps({ className: "dropzone" })}>
        <input {...getInputProps()} />
        <p>Drag & drop files here, or click to select</p>
      </div>
      <ul>
        {files.map((file, index) => (
          <li key={index}><a href={file.url} target="_blank" rel="noopener noreferrer">{file.name}</a></li>
        ))}
      </ul>
    </div>
  );
};

export default NotePage;
