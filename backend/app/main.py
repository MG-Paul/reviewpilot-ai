from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Set
import json
import logging

from app.api.v1.projects import router as projects_router
from app.api.v1.references import router as references_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ReviewPilot")

app = FastAPI(
    title="ReviewPilot AI API",
    description="Backend API services for ReviewPilot AI Systematic Review Copilot",
    version="1.0.0",
)

# CORS configurations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers under api/v1
app.include_router(projects_router, prefix="/api/v1")
app.include_router(references_router, prefix="/api/v1")

# Real-time WebSocket connection manager for cell-locking and live PRISMA updates
class ConnectionManager:
    def __init__(self):
        # Maps project_id -> list of active websockets
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Maps project_id -> dict of field_name/resource -> user_id who holds the lock
        self.locks: Dict[str, Dict[str, str]] = {}

    async def connect(self, websocket: WebSocket, project_id: str):
        await websocket.accept()
        if project_id not in self.active_connections:
            self.active_connections[project_id] = []
        self.active_connections[project_id].append(websocket)
        logger.info(f"WebSocket connected to project {project_id}")

    def disconnect(self, websocket: WebSocket, project_id: str):
        if project_id in self.active_connections:
            self.active_connections[project_id].remove(websocket)
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]
        logger.info(f"WebSocket disconnected from project {project_id}")

    async def broadcast_to_project(self, project_id: str, message: dict):
        if project_id in self.active_connections:
            for connection in self.active_connections[project_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting message: {e}")

manager = ConnectionManager()

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "ReviewPilot AI Backend"}

@app.websocket("/ws/project/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    await manager.connect(websocket, project_id)
    try:
        while True:
            # Expecting messages for: LOCK_FIELD, UNLOCK_FIELD
            data = await websocket.receive_text()
            message = json.loads(data)
            action = message.get("action")
            user_id = message.get("user_id")
            resource = message.get("resource") # e.g. "reference_123:sample_size"

            if action == "LOCK_FIELD":
                if project_id not in manager.locks:
                    manager.locks[project_id] = {}
                # Lock if not already locked or held by the same user
                current_holder = manager.locks[project_id].get(resource)
                if not current_holder or current_holder == user_id:
                    manager.locks[project_id][resource] = user_id
                    await manager.broadcast_to_project(project_id, {
                        "event": "FIELD_LOCKED",
                        "resource": resource,
                        "user_id": user_id
                    })
                else:
                    await websocket.send_json({
                        "event": "LOCK_FAILED",
                        "resource": resource,
                        "reason": f"Field locked by user {current_holder}"
                    })

            elif action == "UNLOCK_FIELD":
                if project_id in manager.locks and resource in manager.locks[project_id]:
                    if manager.locks[project_id][resource] == user_id:
                        del manager.locks[project_id][resource]
                        await manager.broadcast_to_project(project_id, {
                            "event": "FIELD_UNLOCKED",
                            "resource": resource,
                            "user_id": user_id
                        })

    except WebSocketDisconnect:
        manager.disconnect(websocket, project_id)
        # Release locks held by disconnected user
        # Note: In a production system, we would clean up locks for the user_id.
        logger.info(f"Client disconnected from WebSocket project room {project_id}")
