import json
import asyncio
from typing import List, Dict, Any
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
import logging

logger = logging.getLogger(__name__)

class AgentWebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.session_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if session_id:
            if session_id not in self.session_connections:
                self.session_connections[session_id] = []
            self.session_connections[session_id].append(websocket)
        
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket, session_id: str = None):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if session_id and session_id in self.session_connections:
            if websocket in self.session_connections[session_id]:
                self.session_connections[session_id].remove(websocket)
            
            if not self.session_connections[session_id]:
                del self.session_connections[session_id]
        
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast_agent_update(self, session_id: str, agent: str, status: str, data: dict):
        message = {
            "type": "agent_update",
            "session_id": session_id,
            "agent": agent,
            "status": status,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        message_str = json.dumps(message)
        logger.info(f"Broadcasting agent update: {agent} - {status}")
        
        # Send to session-specific connections
        if session_id in self.session_connections:
            disconnected = []
            for connection in self.session_connections[session_id]:
                try:
                    await connection.send_text(message_str)
                except Exception as e:
                    logger.error(f"Error broadcasting to session connection: {e}")
                    disconnected.append(connection)
            
            # Clean up disconnected connections
            for conn in disconnected:
                self.disconnect(conn, session_id)
        
        # Also broadcast to all general connections
        disconnected_general = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.error(f"Error broadcasting to general connection: {e}")
                disconnected_general.append(connection)
        
        # Clean up disconnected general connections
        for conn in disconnected_general:
            self.disconnect(conn)
    
    async def broadcast_session_update(self, session_id: str, event_type: str, data: dict):
        message = {
            "type": "session_update",
            "session_id": session_id,
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        message_str = json.dumps(message)
        logger.info(f"Broadcasting session update: {event_type}")
        
        # Send to all connections (both session-specific and general)
        all_connections = set(self.active_connections)
        if session_id in self.session_connections:
            all_connections.update(self.session_connections[session_id])
        
        disconnected = []
        for connection in all_connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.error(f"Error broadcasting session update: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for conn in disconnected:
            self.disconnect(conn, session_id)

# Global WebSocket manager instance
websocket_manager = AgentWebSocketManager()

# WebSocket endpoint handler
async def websocket_endpoint(websocket: WebSocket, session_id: str = None):
    """Main WebSocket endpoint handler"""
    await websocket_manager.connect(websocket, session_id)
    
    try:
        while True:
            message = await websocket.receive_text()
            await websocket_manager.handle_client_message(websocket, message)
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        websocket_manager.logger.error(f"WebSocket error: {e}")
        websocket_manager.disconnect(websocket) 