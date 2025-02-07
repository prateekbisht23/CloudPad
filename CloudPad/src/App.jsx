import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import NotePage from './components/NotePage'; // Adjust path if needed

const App = () => {
  return (
    <Router>
      <div className="App">
        <h1>CloudPad</h1>
        <Routes>
          {/* Route for the NotePage where each note will be displayed */}
          <Route path="/note/:noteId" element={<NotePage />} />
          {/* Add additional routes if needed */}
          <Route path="/" element={<h2>Welcome to CloudPad</h2>} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
