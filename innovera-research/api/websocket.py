"""
WebSocket endpoint for real-time progress streaming.
"""
import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

# Connected WebSocket clients per run_id
_clients: dict[str, set[WebSocket]] = {}


def get_clients(run_id: str) -> set[WebSocket]:
    if run_id not in _clients:
        _clients[run_id] = set()
    return _clients[run_id]


async def broadcast(run_id: str, message: str):
    """Send a message to all WebSocket clients connected to a run."""
    clients = get_clients(run_id)
    disconnected = set()
    for ws in clients:
        try:
            await ws.send_text(message)
        except Exception:
            disconnected.add(ws)
    clients -= disconnected


async def stream_progress(run_id: str, queue: asyncio.Queue, ws: WebSocket):
    """Read from progress queue and send to WebSocket client."""
    try:
        while True:
            message = await asyncio.wait_for(queue.get(), timeout=1.0)
            await broadcast(run_id, message)
            data = json.loads(message)
            if data.get("type") in ("run_complete", "run_error"):
                break
    except asyncio.TimeoutError:
        pass
    except WebSocketDisconnect:
        pass


@router.websocket("/ws/{run_id}")
async def websocket_endpoint(websocket: WebSocket, run_id: str):
    await websocket.accept()
    clients = get_clients(run_id)
    clients.add(websocket)

    try:
        # Import here to avoid circular imports
        from api.routes import active_runs

        run = active_runs.get(run_id)
        if not run:
            await websocket.send_text(json.dumps({
                "type": "error",
                "error": f"Run {run_id} not found"
            }))
            await websocket.close()
            return

        progress = run["progress"]
        queue = progress.queue

        # Create a consumer that reads from the queue and broadcasts
        # We need a separate queue for each WebSocket client
        client_queue: asyncio.Queue = asyncio.Queue()

        # Start a task that copies from the main queue to all clients
        async def relay():
            try:
                while True:
                    try:
                        message = await asyncio.wait_for(queue.get(), timeout=60.0)
                        await broadcast(run_id, message)
                        data = json.loads(message)
                        if data.get("type") in ("run_complete", "run_error"):
                            break
                    except asyncio.TimeoutError:
                        # Send a ping to keep connection alive
                        try:
                            await websocket.send_text(json.dumps({"type": "ping"}))
                        except Exception:
                            break
            except Exception:
                pass

        relay_task = asyncio.create_task(relay())

        try:
            # Keep the connection open, waiting for client messages (or disconnect)
            while True:
                try:
                    await asyncio.wait_for(websocket.receive_text(), timeout=120.0)
                except asyncio.TimeoutError:
                    continue
        except WebSocketDisconnect:
            pass
        finally:
            relay_task.cancel()
            try:
                await relay_task
            except asyncio.CancelledError:
                pass

    except Exception:
        pass
    finally:
        clients.discard(websocket)
