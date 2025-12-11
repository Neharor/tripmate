#!/bin/bash

echo "🚀 Starting TripMate Backend & Frontend"
echo "======================================"

# Kill any existing processes
echo "🔄 Stopping existing processes..."
pkill -f "python3 main.py" 2>/dev/null || true
pkill -f "npm start" 2>/dev/null || true
sleep 2

# Start backend
echo "📡 Starting backend server..."
cd backend
python3 main.py &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 3

# Test backend
echo "🧪 Testing backend connection..."
curl -s http://localhost:5002/api/trending-destinations > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Backend is running on http://localhost:5002"
else
    echo "❌ Backend failed to start"
fi

# Start frontend
echo "🎨 Starting frontend server..."
cd ../frontend/trimate-frontend
npm start &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

echo ""
echo "🌟 TripMate is starting up!"
echo "   Backend:  http://localhost:5002"
echo "   Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Keep script running
wait