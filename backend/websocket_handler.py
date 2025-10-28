"""
WebSocket Handler for Real-Time Chat
Provides real-time bidirectional communication for the chatbot
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import json
import asyncio
from datetime import datetime
from loguru import logger


class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        # Active connections: user_id -> Set of WebSocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # Connection metadata
        self.connection_metadata: Dict[WebSocket, Dict] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int, session_id: str = None):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        
        # Add to active connections
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        
        # Store metadata
        self.connection_metadata[websocket] = {
            'user_id': user_id,
            'session_id': session_id,
            'connected_at': datetime.utcnow(),
            'message_count': 0
        }
        
        logger.info(f"WebSocket connected: user_id={user_id}, session_id={session_id}")
        
        # Send welcome message
        await self.send_personal_message({
            'type': 'connection',
            'status': 'connected',
            'message': 'Connected to MedAI-Pro chat',
            'timestamp': datetime.utcnow().isoformat()
        }, websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.connection_metadata:
            metadata = self.connection_metadata[websocket]
            user_id = metadata['user_id']
            
            # Remove from active connections
            if user_id in self.active_connections:
                self.active_connections[user_id].discard(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            
            # Remove metadata
            del self.connection_metadata[websocket]
            
            logger.info(f"WebSocket disconnected: user_id={user_id}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket connection"""
        try:
            await websocket.send_json(message)
            
            # Update message count
            if websocket in self.connection_metadata:
                self.connection_metadata[websocket]['message_count'] += 1
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    async def send_to_user(self, message: dict, user_id: int):
        """Send a message to all connections of a specific user"""
        if user_id in self.active_connections:
            disconnected = set()
            
            for connection in self.active_connections[user_id]:
                try:
                    await self.send_personal_message(message, connection)
                except Exception as e:
                    logger.error(f"Error sending to user {user_id}: {e}")
                    disconnected.add(connection)
            
            # Clean up disconnected connections
            for connection in disconnected:
                self.disconnect(connection)
    
    async def broadcast(self, message: dict):
        """Broadcast a message to all connected users"""
        for user_id in list(self.active_connections.keys()):
            await self.send_to_user(message, user_id)
    
    def get_active_users(self) -> List[int]:
        """Get list of currently active user IDs"""
        return list(self.active_connections.keys())
    
    def get_connection_count(self, user_id: int = None) -> int:
        """Get number of active connections"""
        if user_id:
            return len(self.active_connections.get(user_id, set()))
        return sum(len(connections) for connections in self.active_connections.values())
    
    def get_user_metadata(self, user_id: int) -> List[Dict]:
        """Get metadata for all connections of a user"""
        if user_id not in self.active_connections:
            return []
        
        metadata_list = []
        for connection in self.active_connections[user_id]:
            if connection in self.connection_metadata:
                metadata = self.connection_metadata[connection].copy()
                metadata['connected_at'] = metadata['connected_at'].isoformat()
                metadata_list.append(metadata)
        
        return metadata_list


# Global connection manager instance
manager = ConnectionManager()


async def handle_chat_message(websocket: WebSocket, data: dict, chatbot, translator):
    """
    Handle incoming chat message
    
    Args:
        websocket: WebSocket connection
        data: Message data
        chatbot: Chatbot instance
        translator: Translator instance
    """
    try:
        message_text = data.get('message', '')
        language = data.get('language', 'en')
        user_id = manager.connection_metadata[websocket]['user_id']
        
        # Send typing indicator
        await manager.send_personal_message({
            'type': 'typing',
            'status': 'bot_typing',
            'timestamp': datetime.utcnow().isoformat()
        }, websocket)
        
        # Translate message to English if needed
        if language != 'en':
            message_text = translator.translate_text(message_text, 'en', language)
        
        # Process message with chatbot
        response = chatbot.process_message(message_text, language)
        
        # Send response
        await manager.send_personal_message({
            'type': 'message',
            'role': 'assistant',
            'message': response['response'],
            'intent': response.get('intent'),
            'sentiment': response.get('sentiment'),
            'urgency': response.get('urgency'),
            'timestamp': datetime.utcnow().isoformat()
        }, websocket)
        
        # If emergency detected, send alert
        if response.get('is_emergency'):
            await manager.send_personal_message({
                'type': 'alert',
                'level': 'critical',
                'message': 'Emergency situation detected. Please seek immediate medical attention.',
                'timestamp': datetime.utcnow().isoformat()
            }, websocket)
        
    except Exception as e:
        logger.error(f"Error handling chat message: {e}")
        await manager.send_personal_message({
            'type': 'error',
            'message': 'An error occurred processing your message',
            'timestamp': datetime.utcnow().isoformat()
        }, websocket)


async def handle_voice_message(websocket: WebSocket, data: dict, voice_handler, chatbot, translator):
    """
    Handle incoming voice message
    
    Args:
        websocket: WebSocket connection
        data: Voice data
        voice_handler: Voice handler instance
        chatbot: Chatbot instance
        translator: Translator instance
    """
    try:
        audio_data = data.get('audio')
        language = data.get('language', 'en')
        
        # Send processing indicator
        await manager.send_personal_message({
            'type': 'processing',
            'status': 'transcribing',
            'timestamp': datetime.utcnow().isoformat()
        }, websocket)
        
        # Transcribe audio
        transcription = voice_handler.transcribe_audio(audio_data, language)
        
        # Send transcription
        await manager.send_personal_message({
            'type': 'transcription',
            'text': transcription,
            'timestamp': datetime.utcnow().isoformat()
        }, websocket)
        
        # Process as text message
        await handle_chat_message(
            websocket,
            {'message': transcription, 'language': language},
            chatbot,
            translator
        )
        
    except Exception as e:
        logger.error(f"Error handling voice message: {e}")
        await manager.send_personal_message({
            'type': 'error',
            'message': 'An error occurred processing your voice message',
            'timestamp': datetime.utcnow().isoformat()
        }, websocket)


async def handle_typing_indicator(websocket: WebSocket, data: dict):
    """Handle typing indicator from user"""
    try:
        is_typing = data.get('is_typing', False)
        user_id = manager.connection_metadata[websocket]['user_id']
        
        # Broadcast typing status to other connections of the same user
        await manager.send_to_user({
            'type': 'typing',
            'status': 'user_typing' if is_typing else 'user_stopped_typing',
            'timestamp': datetime.utcnow().isoformat()
        }, user_id)
        
    except Exception as e:
        logger.error(f"Error handling typing indicator: {e}")


async def handle_ping(websocket: WebSocket):
    """Handle ping message to keep connection alive"""
    try:
        await manager.send_personal_message({
            'type': 'pong',
            'timestamp': datetime.utcnow().isoformat()
        }, websocket)
    except Exception as e:
        logger.error(f"Error handling ping: {e}")


async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int,
    session_id: str,
    chatbot,
    voice_handler,
    translator
):
    """
    Main WebSocket endpoint handler
    
    Args:
        websocket: WebSocket connection
        user_id: User ID
        session_id: Chat session ID
        chatbot: Chatbot instance
        voice_handler: Voice handler instance
        translator: Translator instance
    """
    await manager.connect(websocket, user_id, session_id)
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            message_type = data.get('type')
            
            # Route to appropriate handler
            if message_type == 'message':
                await handle_chat_message(websocket, data, chatbot, translator)
            
            elif message_type == 'voice':
                await handle_voice_message(websocket, data, voice_handler, chatbot, translator)
            
            elif message_type == 'typing':
                await handle_typing_indicator(websocket, data)
            
            elif message_type == 'ping':
                await handle_ping(websocket)
            
            else:
                logger.warning(f"Unknown message type: {message_type}")
                await manager.send_personal_message({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}',
                    'timestamp': datetime.utcnow().isoformat()
                }, websocket)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"WebSocket disconnected normally: user_id={user_id}")
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# Export manager and endpoint
__all__ = ['manager', 'websocket_endpoint', 'ConnectionManager']

