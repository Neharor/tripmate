import React from 'react';

export default function Stays({ stays }) {
  return (
    <div>
      <h2>Stays</h2>
      {stays && stays.length > 0 ? (
        <ul>
          {stays.map((stay, idx) => (
            <li key={idx}>{stay}</li>
          ))}
        </ul>
      ) : (
        <p>No stays found.</p>
      )}
    </div>
  );
}
