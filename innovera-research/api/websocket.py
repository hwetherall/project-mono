"""
WebSocket endpoint for real-time progress streaming.
"""
import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

# Connected WebSocket clients per run_id / chain_id
_clients: dict[str, set[WebSocket]] = {}


def get_clients(key: str) -> set[WebSocket]:
    if key not in _clients:
        _clients[key] = set()
    return _clients[key]


async def broadcast(key: str, message: str):
    """Send a message to all WebSocket clients connected to a run or chain."""
    clients = get_clients(key)
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


def _make_relay(key: str, queue: asyncio.Queue, websocket: WebSocket, terminal_types: set[str]):
    """Create a relay coroutine that reads from queue and broadcasts.
    Exits when any event type in terminal_types is received."""
    async def relay():
        try:
            while True:
                try:
                    message = await asyncio.wait_for(queue.get(), timeout=60.0)
                    await broadcast(key, message)
                    data = json.loads(message)
                    if data.get("type") in terminal_types:
                        break
                except asyncio.TimeoutError:
                    try:
                        await websocket.send_text(json.dumps({"type": "ping"}))
                    except Exception:
                        break
        except Exception:
            pass
    return relay


@router.websocket("/ws/{run_id}")
async def websocket_endpoint(websocket: WebSocket, run_id: str):
    await websocket.accept()
    clients = get_clients(run_id)
    clients.add(websocket)

    try:
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

        relay = _make_relay(run_id, queue, websocket, {"run_complete", "run_error"})
        relay_task = asyncio.create_task(relay())

        try:
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


@router.websocket("/ws/chain/{chain_id}")
async def chain_websocket_endpoint(websocket: WebSocket, chain_id: str):
    await websocket.accept()
    clients = get_clients(f"chain:{chain_id}")
    clients.add(websocket)

    try:
        from api.routes import active_chains

        chain = active_chains.get(chain_id)
        if not chain:
            await websocket.send_text(json.dumps({
                "type": "error",
                "error": f"Chain {chain_id} not found"
            }))
            await websocket.close()
            return

        progress = chain["progress"]
        queue = progress.queue

        relay = _make_relay(
            f"chain:{chain_id}", queue, websocket,
            {"chain_complete", "run_error"},
        )
        relay_task = asyncio.create_task(relay())

        try:
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
