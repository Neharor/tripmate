// API Base URL
export const API_BASE_URL = 'http://localhost:5002';

// Generate a unique session ID for this browser session
const SESSION_ID = 'session_' + Date.now() + '_' + Math.random().toString(36).substring(2, 9);

export async function fetchItinerary(query, uiSelections = {}) {
  const url = `${API_BASE_URL}/api/generate`;

  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      query,
      session_id: SESSION_ID,
      ui_selections: uiSelections
    }),
  });

  // If response is not OK try to read body (might contain JSON error message)
  if (!response.ok) {
    const text = await response.text();
    try {
      const json = JSON.parse(text || '{}');
      throw new Error(json.error || `Request failed: ${response.status}`);
    } catch (e) {
      throw new Error(text || `Request failed: ${response.status} ${response.statusText}`);
    }
  }

  // Ensure we parse JSON safely
  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    return await response.json();
  }

  // Fallback: try to parse text as JSON, otherwise throw
  const text = await response.text();
  try {
    return JSON.parse(text);
  } catch (e) {
    throw new Error('Response was not valid JSON');
  }
}
  