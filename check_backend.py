#!/usr/bin/env python3
import subprocess
import time
import requests
import os

print("🔍 Checking backend status...")

# Check if port 5002 is in use
try:
    result = subprocess.run(['lsof', '-ti:5002'], capture_output=True, text=True)
    if result.stdout.strip():
        print(f"✅ Process running on port 5002: {result.stdout.strip()}")
    else:
        print("❌ No process on port 5002")
except:
    print("❌ Could not check port 5002")

# Try to connect to backend
try:
    response = requests.get('http://localhost:5002/api/trending-destinations', timeout=5)
    print(f"✅ Backend responding! Status: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("❌ Backend not responding - starting it now...")
    
    # Change to backend directory and start
    os.chdir('backend')
    print("📂 Changed to backend directory")
    print("🚀 Starting backend server...")
    subprocess.Popen(['python3', 'main.py'])
    
    # Wait and test again
    time.sleep(3)
    try:
        response = requests.get('http://localhost:5002/api/trending-destinations', timeout=5)
        print(f"✅ Backend now responding! Status: {response.status_code}")
    except:
        print("❌ Backend still not responding")
        
except Exception as e:
    print(f"❌ Error checking backend: {e}")