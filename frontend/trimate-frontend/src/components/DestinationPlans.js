import React from 'react';

export default function DestinationPlans({ plan }) {
  return (
    <div>
      <h2>Destinations</h2>
      {plan && Array.isArray(plan) && plan.length > 0 ? (
        <ul>
          {plan.map((item, idx) => (
            <li key={idx}>{item}</li>
          ))}
        </ul>
      ) : (
        <p>No destinations found.</p>
      )}
    </div>
  );
}
