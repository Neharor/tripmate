import React, { useState } from 'react';
import LandingPage from './LandingPage';
import ChatInterface from './ChatInterface';
import MyTrips from './MyTrips';

export default function App() {
  const [currentView, setCurrentView] = useState('home'); // 'home', 'chat', 'trips'

  return (
    <>
      {currentView === 'chat' ? (
        <ChatInterface 
          onBackToHome={() => setCurrentView('home')}
          onViewTrips={() => setCurrentView('trips')}
        />
      ) : currentView === 'trips' ? (
        <MyTrips onBackToHome={() => setCurrentView('home')} />
      ) : (
        <LandingPage 
          onStartPlanning={() => setCurrentView('chat')}
          onViewTrips={() => setCurrentView('trips')}
        />
      )}
    </>
  );
}
