import React, { useState } from 'react';
import { fetchItinerary } from './api';
import DestinationPlans from './components/DestinationPlans';
import Stays from './components/Stays';

export default function App() {
  const [query, setQuery] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const result = await fetchItinerary(query);
    setData(result);
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 600, margin: '20px auto', fontFamily: 'Arial, sans-serif' }}>
      <h1>TripMate Chatbot</h1>
      <form onSubmit={handleSubmit} style={{ marginBottom: 20 }}>
        <input
          type="text"
          value={query}
          placeholder="Enter your travel query"
          onChange={(e) => setQuery(e.target.value)}
          required
          style={{ width: '80%', padding: 10, fontSize: 16 }}
        />
        <button type="submit" style={{ padding: '10px 15px', marginLeft: 10 }}>Plan Trip</button>
      </form>
      {loading && <p>Loading...</p>}
      {data && (
        <>
          <DestinationPlans plan={data.destinations?.plan} />
          <Stays stays={data.stays?.stays} />
        </>
      )}
    </div>
  );
}
