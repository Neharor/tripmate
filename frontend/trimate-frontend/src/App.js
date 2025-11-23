import React, { useState } from 'react';
import LandingPage from './LandingPage';
import ChatInterface from './ChatInterface';

export default function App() {
  const [showChat, setShowChat] = useState(false);

  return (
    <>
      {showChat ? (
        <ChatInterface onBackToHome={() => setShowChat(false)} />
      ) : (
        <LandingPage onStartPlanning={() => setShowChat(true)} />
      )}
    </>
  );
}
