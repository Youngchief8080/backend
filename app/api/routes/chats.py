from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import List, Dict, Optional
import json
from uuid import uuid4
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.model.chats import ChatMessage

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active: Dict[str, WebSocket] = {}
        self.meta: Dict[str, Dict] = {}

    async def connect(self, ws: WebSocket, username: str) -> str:
        await ws.accept()
        cid = str(uuid4())
        self.active[cid] = ws
        self.meta[cid] = {"username": username, "role": "user"}
        return cid

    def disconnect(self, cid: str):
        self.active.pop(cid, None)
        self.meta.pop(cid, None)

    def get_admins(self) -> List[str]:
        return [cid for cid, info in self.meta.items() if info["role"] == "admin"]

    def get_active_users(self) -> List[Dict]:
        return [
            {"client_id": cid, "username": info["username"]}
            for cid, info in self.meta.items()
            if info["role"] == "user"
        ]

    def find_by_username(self, username: str) -> Optional[str]:
        username_lower = username.strip().lower()
        for cid, info in self.meta.items():
            if info["username"].strip().lower() == username_lower:
                return cid
        return None

    async def send(self, cid: str, data: dict):
        ws = self.active.get(cid)
        if ws:
            await ws.send_json(data)

manager = ConnectionManager()

@router.websocket("/ws/{username}")
async def ws_chat(ws: WebSocket, username: str, db: Session = Depends(get_db)):
    cid = await manager.connect(ws, username)
    print("CONNECT:", cid, username)

    try:
        while True:
            text = await ws.receive_text()
            msg = json.loads(text)
            mtype = msg.get("type")
            info = manager.meta.get(cid)
            if not info:
                break

            role = info["role"]
            print(f"MSG RECV from {info['username']} ({role}):", msg)

            if mtype == "identification":
                role = msg.get("role", "user")
                manager.meta[cid]["role"] = role
                print("Set role:", role)
                if role == "admin":
                    await ws.send_json({
                        "type": "active_users",
                        "users": manager.get_active_users()
                    })

            elif mtype == "message" and role == "admin":
                content = msg.get("content", "")
                recipient = msg.get("recipient")

                if not recipient:
                    await ws.send_json({"type": "error", "content": "Missing recipient."})
                    continue

                rid = manager.find_by_username(recipient)
                if not rid:
                    print(f"Admin tried to message unknown user '{recipient}'. Available users:", manager.get_active_users())
                    await ws.send_json({
                        "type": "error",
                        "content": f"User '{recipient}' not connected."
                    })
                    continue

                cm = ChatMessage(
                    id=str(uuid4()),
                    sender=info["username"],
                    sender_id=cid,
                    content=content,
                    recipient=recipient,
                    is_admin=True
                )
                db.add(cm)
                db.commit()
                db.refresh(cm)

                # Send to recipient
                await manager.send(rid, {
                    "type": "message",
                    "id": cm.id,
                    "content": content,
                    "sender": cm.sender,
                    "recipient": cm.recipient,
                    "timestamp": cm.timestamp.isoformat(),
                    "is_admin": True,
                    "is_own": False
                })

                # Send confirmation to admin
                await ws.send_json({
                    "type": "message",
                    "id": cm.id,
                    "content": content,
                    "sender": cm.sender,
                    "recipient": cm.recipient,
                    "timestamp": cm.timestamp.isoformat(),
                    "is_admin": True,
                    "is_own": True
                })

            elif mtype == "message" and role == "user":
                content = msg.get("content", "")
                cm = ChatMessage(
                    id=str(uuid4()),
                    sender=info["username"],
                    sender_id=cid,
                    content=content,
                    recipient=None,
                    is_admin=False
                )
                db.add(cm)
                db.commit()
                db.refresh(cm)

                # Send confirmation to user
                await ws.send_json({
                    "type": "message",
                    "id": cm.id,
                    "content": cm.content,
                    "sender": cm.sender,
                    "timestamp": cm.timestamp.isoformat(),
                    "is_admin": False,
                    "is_own": True
                })

                # Send to all admins
                for admin_cid in manager.get_admins():
                    await manager.send(admin_cid, {
                        "type": "message",
                        "id": cm.id,
                        "content": cm.content,
                        "sender": cm.sender,
                        "timestamp": cm.timestamp.isoformat(),
                        "is_admin": False,
                        "is_own": False
                    })

            elif mtype == "request_active_users" and role == "admin":
                await ws.send_json({
                    "type": "active_users",
                    "users": manager.get_active_users()
                })

    except WebSocketDisconnect:
        print("DISCONNECT:", info["username"])
        manager.disconnect(cid)

    except Exception as e:
        print("ERROR:", e)
        manager.disconnect(cid)

@router.get("/messages/", response_model=List[dict])
def list_msgs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    msgs = db.query(ChatMessage).order_by(ChatMessage.timestamp.desc()).offset(skip).limit(limit).all()
    return [
        {
            "id": m.id,
            "sender": m.sender,
            "content": m.content,
            "recipient": m.recipient,
            "timestamp": m.timestamp.isoformat(),
            "is_admin": m.is_admin
        }
        for m in msgs
    ]