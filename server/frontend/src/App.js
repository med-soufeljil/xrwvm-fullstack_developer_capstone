import React from 'react';
import { Routes, Route } from 'react-router-dom';
import LoginPanel from './components/Login/Login'; // Existing import
import Register from "./components/Register/Register";
 // Import the Register component

function App() {
  return (
    <Routes>
      {/* Define routes for your components */}
      <Route path="/login" element={<LoginPanel />} /> {/* Existing route */}
      <Route path="/register" element={<Register />} /> {/* Route for Register component */}
      {/* Add more routes as needed */}
    </Routes>
  );
}

export default App;
