#!/bin/bash
# Script to add timings to itinerary

cd /Users/nehaarora/Documents/Q7/Mod01/Project/Project/tripmate/backend

# Backup the file
cp agents/langchain_orchestrator.py agents/langchain_orchestrator.py.backup

# Replace all occurrences
sed -i '' 's/**Morning:** {morning_acts\[0\]\.capitalize()}/**9:00 AM - 12:00 PM:** {morning_acts[0].capitalize()}/g' agents/langchain_orchestrator.py
sed -i '' 's/**Afternoon:** {afternoon_acts\[0\]\.capitalize()}/**1:00 PM - 5:00 PM:** {afternoon_acts[0].capitalize()}/g' agents/langchain_orchestrator.py  
sed -i '' 's/**Evening:** {evening_acts\[0\]\.capitalize()}/**7:00 PM - 9:00 PM:** {evening_acts[0].capitalize()}/g' agents/langchain_orchestrator.py

echo "✅ Updated all occurrences with timings"
