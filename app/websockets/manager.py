from fastapi import WebSocket
from typing import Dict, List, Optional
import uuid

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_metadata: Dict[str, dict] = {}

    async def connect(self, websocket: WebSocket, client_id: str, user_data: dict):
        self.active_connections[client_id] = websocket
        self.user_metadata[client_id] = user_data

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.user_metadata:
            del self.user_metadata[client_id]

    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(message)
            except Exception:
                self.disconnect(client_id)

    async def broadcast(self, message: str, exclude: List[str] = None):
        exclude = exclude or []
        disconnected = []
        
        for client_id, connection in list(self.active_connections.items()):
            if client_id not in exclude:
                try:
                    await connection.send_text(message)
                except Exception:
                    disconnected.append(client_id)
        
        for client_id in disconnected:
            self.disconnect(client_id)

    async def broadcast_json(self, data: dict, exclude: List[str] = None):
        await self.broadcast(json.dumps(data), exclude)

    def get_active_users(self) -> List[dict]:
        return [
            {
                "client_id": client_id,
                "username": meta.get("username", "anonymous"),
                "role": meta.get("role", "user")
            }
            for client_id, meta in self.user_metadata.items()
        ]