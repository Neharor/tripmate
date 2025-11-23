"""
Real-Time WebSocket Server for Agent Status Updates
Provides live progress updates as agents work on user queries
"""
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
from functools import wraps
import time
import json

socketio = None

def init_socketio(app):
    """Initialize SocketIO with Flask app"""
    global socketio
    socketio = SocketIO(
        app,
        cors_allowed_origins="*",
        async_mode='threading',
        logger=True,
        engineio_logger=True
    )
    
    register_handlers()
    return socketio

def register_handlers():
    """Register all WebSocket event handlers"""
    
    @socketio.on('connect')
    def handle_connect():
        """Client connected"""
        print(f'Client connected: {request.sid}')
        emit('connection_status', {
            'status': 'connected',
            'message': 'Connected to TripMate AI',
            'timestamp': time.time()
        })
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Client disconnected"""
        print(f'Client disconnected: {request.sid}')
    
    @socketio.on('join_session')
    def handle_join_session(data):
        """Join a session room for targeted updates"""
        session_id = data.get('session_id')
        join_room(session_id)
        emit('joined_session', {
            'session_id': session_id,
            'message': f'Joined session {session_id}'
        })
    
    @socketio.on('leave_session')
    def handle_leave_session(data):
        """Leave a session room"""
        session_id = data.get('session_id')
        leave_room(session_id)
        emit('left_session', {
            'session_id': session_id
        })
    
    @socketio.on('start_trip_planning')
    def handle_trip_planning(data):
        """User started trip planning - initiate agent workflow"""
        session_id = data.get('session_id')
        query = data.get('query')
        
        # Emit initial status
        emit_agent_status(session_id, {
            'status': 'started',
            'message': '🤔 Understanding your request...',
            'progress': 0
        })
        
        # This will be handled by orchestrator
        # which will emit updates as agents work
        return {'status': 'acknowledged', 'session_id': session_id}


# Helper functions for agents to emit updates

def emit_agent_status(session_id, status_data):
    """
    Emit agent status update to specific session
    
    Args:
        session_id: User session identifier
        status_data: Dict with status, message, progress, agent_name
    """
    if socketio:
        socketio.emit('agent_status', {
            **status_data,
            'timestamp': time.time(),
            'session_id': session_id
        }, room=session_id)


def emit_agent_started(session_id, agent_name, message):
    """Agent started working"""
    emit_agent_status(session_id, {
        'agent': agent_name,
        'status': 'working',
        'message': message,
        'progress': 10
    })


def emit_agent_progress(session_id, agent_name, message, progress):
    """Agent progress update"""
    emit_agent_status(session_id, {
        'agent': agent_name,
        'status': 'working',
        'message': message,
        'progress': progress
    })


def emit_agent_completed(session_id, agent_name, message, result=None):
    """Agent completed task"""
    data = {
        'agent': agent_name,
        'status': 'completed',
        'message': message,
        'progress': 100
    }
    if result:
        data['result'] = result
    
    emit_agent_status(session_id, data)


def emit_agent_error(session_id, agent_name, error_message):
    """Agent encountered error"""
    emit_agent_status(session_id, {
        'agent': agent_name,
        'status': 'error',
        'message': f'❌ {error_message}',
        'progress': 0
    })


def emit_final_result(session_id, result_data):
    """Emit final trip planning result"""
    if socketio:
        socketio.emit('trip_result', {
            **result_data,
            'timestamp': time.time(),
            'session_id': session_id
        }, room=session_id)


# Decorator to wrap agent methods with status updates
def agent_status_tracker(agent_name, start_message, success_message):
    """
    Decorator to automatically emit status updates for agent methods
    
    Usage:
        @agent_status_tracker('FlightAgent', '✈️ Searching flights...', '✅ Flights found!')
        def search_flights(self, session_id, **kwargs):
            # Agent work here
            return results
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract session_id from args or kwargs
            session_id = kwargs.get('session_id') or (args[1] if len(args) > 1 else None)
            
            if not session_id:
                # No session tracking, just run function
                return func(*args, **kwargs)
            
            try:
                # Emit start status
                emit_agent_started(session_id, agent_name, start_message)
                
                # Execute agent work
                result = func(*args, **kwargs)
                
                # Emit completion
                emit_agent_completed(session_id, agent_name, success_message, result)
                
                return result
            
            except Exception as e:
                # Emit error
                emit_agent_error(session_id, agent_name, str(e))
                raise
        
        return wrapper
    return decorator


# Example usage in agents:
"""
from realtime.socketio_server import agent_status_tracker, emit_agent_progress

class FlightAgent:
    @agent_status_tracker('FlightAgent', '✈️ Searching flights...', '✅ Found best flights!')
    def search_flights(self, session_id, origin, destination, dates):
        # Emit intermediate progress
        emit_agent_progress(session_id, 'FlightAgent', 'Contacting Amadeus API...', 30)
        
        flights = amadeus_api.search(origin, destination, dates)
        
        emit_agent_progress(session_id, 'FlightAgent', 'Ranking flights by value...', 70)
        
        ranked = flight_ranker.rank(flights)
        
        return ranked[:5]  # Top 5 flights
"""
