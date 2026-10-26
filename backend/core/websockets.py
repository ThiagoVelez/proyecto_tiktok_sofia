"""
Gestor de Conexiones WebSocket en Tiempo Real y Pub/Sub.
Permite streaming de notificaciones en vivo, alertas parentales instantáneas,
y sincronización de contadores de likes/comentarios en tiempo real.
"""

import json
from typing import Dict, List, Set, Optional, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from .security import decode_access_token, is_token_revoked
from .logging import logger
from .redis_client import get_redis


class WebSocketConnectionManager:
    """Administrador de conexiones persistentes WebSocket y salas de eventos."""

    def __init__(self):
        # Conexiones por ID de usuario: user_id -> List[WebSocket]
        self.active_user_connections: Dict[int, List[WebSocket]] = {}
        # Conexiones por sala/recurso (ej: video_123): room -> Set[WebSocket]
        self.active_rooms: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_user_connections:
            self.active_user_connections[user_id] = []
        self.active_user_connections[user_id].append(websocket)
        logger.info(f"WebSocket conectado: Usuario {user_id}")

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_user_connections:
            if websocket in self.active_user_connections[user_id]:
                self.active_user_connections[user_id].remove(websocket)
            if not self.active_user_connections[user_id]:
                del self.active_user_connections[user_id]

        # Limpiar de cualquier sala
        for room, clients in list(self.active_rooms.items()):
            if websocket in clients:
                clients.remove(websocket)
            if not clients:
                del self.active_rooms[room]

        logger.info(f"WebSocket desconectado: Usuario {user_id}")

    def join_room(self, room: str, websocket: WebSocket):
        if room not in self.active_rooms:
            self.active_rooms[room] = set()
        self.active_rooms[room].add(websocket)

    def leave_room(self, room: str, websocket: WebSocket):
        if room in self.active_rooms and websocket in self.active_rooms[room]:
            self.active_rooms[room].remove(websocket)
            if not self.active_rooms[room]:
                del self.active_rooms[room]

    async def send_personal_message(self, message: Dict[str, Any], user_id: int):
        """Envía un mensaje a todas las sesiones activas de un usuario específico."""
        if user_id in self.active_user_connections:
            payload_str = json.dumps(message)
            for connection in list(self.active_user_connections[user_id]):
                try:
                    await connection.send_text(payload_str)
                except Exception as e:
                    logger.warning(f"Error enviando mensaje a usuario {user_id}: {e}")

    async def broadcast_to_room(self, message: Dict[str, Any], room: str):
        """Envía un mensaje a todos los clientes suscritos a una sala o recurso."""
        if room in self.active_rooms:
            payload_str = json.dumps(message)
            for connection in list(self.active_rooms[room]):
                try:
                    await connection.send_text(payload_str)
                except Exception as e:
                    logger.warning(f"Error enviando mensaje a sala {room}: {e}")

    async def broadcast_all(self, message: Dict[str, Any]):
        """Transmite un mensaje global a todos los clientes conectados."""
        payload_str = json.dumps(message)
        for user_id, conns in list(self.active_user_connections.items()):
            for connection in conns:
                try:
                    await connection.send_text(payload_str)
                except Exception:
                    pass


ws_manager = WebSocketConnectionManager()
ws_router = APIRouter(tags=["Tiempo Real (WebSockets)"])


@ws_router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None)
):
    """
    Canal WebSocket bidireccional autenticado con JWT.
    Permite unirse a salas (videos/chats) y recibir notificaciones instantáneas.
    """
    if not token or is_token_revoked(token):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        user_id = int(payload["sub"])
    except (ValueError, TypeError):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await ws_manager.connect(websocket, user_id)

    # Mensaje inicial de bienvenida
    await websocket.send_text(json.dumps({
        "event": "connected",
        "user_id": user_id,
        "message": "Conexión en tiempo real activa."
    }))

    try:
        while True:
            data_text = await websocket.receive_text()
            try:
                data = json.loads(data_text)
                action = data.get("action")
                room = data.get("room")

                if action == "join" and room:
                    ws_manager.join_room(room, websocket)
                    await websocket.send_text(json.dumps({"event": "joined_room", "room": room}))
                elif action == "leave" and room:
                    ws_manager.leave_room(room, websocket)
                    await websocket.send_text(json.dumps({"event": "left_room", "room": room}))
                elif action == "ping":
                    await websocket.send_text(json.dumps({"event": "pong"}))
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"error": "Formato JSON no válido."}))
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"Error en sesión WebSocket de usuario {user_id}: {e}")
        ws_manager.disconnect(websocket, user_id)
