#!/bin/bash

# Kill any existing processes on port 5002
lsof -ti:5002 | xargs kill -9 2>/dev/null

# Navigate to backend directory
cd /Users/nehaarora/Documents/Q7/Mod01/Project/Project/tripmate/backend

# Start the main server
python3 main.py