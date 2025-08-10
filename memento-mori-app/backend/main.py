import os
import time
import asyncio
from typing import Any, Dict

import httpx
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import websockets

API_BASE = os.getenv("UPSTREAM_BASE", "https://api.mentemori.icu")
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL", "60"))
ALLOWED_ORIGINS = [
    os.getenv("ALLOWED_ORIGIN", "*"),  # set to your GitHub Pages origin in prod
]

app = FastAPI(title="Memento Mori API Proxy")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

client = httpx.AsyncClient(base_url=API_BASE, timeout=30.0)
_cache: Dict[str, Dict[str, Any]] = {}


def _cache_get(key: str):
    e = _cache.get(key)
    if not e:
        return None
    if time.time() - e["ts"] > CACHE_TTL_SECONDS:
        _cache.pop(key, None)
        return None
    return e["data"]


def _cache_set(key: str, data: Any):
    _cache[key] = {"ts": time.time(), "data": data}


async def _forward(path: str):
    cache_key = path
    if (cached := _cache_get(cache_key)) is not None:
        return cached
    r = await client.get(path)
    if r.status_code != 200:
        raise HTTPException(r.status_code, r.text)
    data = r.json()
    _cache_set(cache_key, data)
    return data


@app.get("/healthz")
async def healthz():
    return {"ok": True}


@app.get("/worlds")
async def worlds():
    return await _forward("/worlds")


@app.get("/wgroups")
async def wgroups():
    return await _forward("/wgroups")


@app.get("/{world_id}/player_ranking/latest")
async def player_ranking(world_id: int):
    return await _forward(f"/{world_id}/player_ranking/latest")


@app.get("/{world_id}/guild_ranking/latest")
async def guild_ranking(world_id: int):
    return await _forward(f"/{world_id}/guild_ranking/latest")


@app.get("/{world_id}/temple/latest")
async def temple(world_id: int):
    return await _forward(f"/{world_id}/temple/latest")


@app.get("/{world_id}/arena/latest")
async def arena(world_id: int):
    return await _forward(f"/{world_id}/arena/latest")


@app.get("/{world_id}/localgvg/latest")
async def localgvg(world_id: int):
    return await _forward(f"/{world_id}/localgvg/latest")


@app.get("/wg/{wgroup_id}/legend/latest")
async def legend(wgroup_id: int):
    return await _forward(f"/wg/{wgroup_id}/legend/latest")


@app.get("/wg/{wgroup_id}/globalgvg/{gclass}/{block}/latest")
async def globalgvg(wgroup_id: int, gclass: int, block: int):
    return await _forward(f"/wg/{wgroup_id}/globalgvg/{gclass}/{block}/latest")


# --- WebSocket relay for /gvg ---
@app.websocket("/ws/gvg")
async def gvg_ws_proxy(ws: WebSocket):
    await ws.accept()
    upstream_url = API_BASE.replace("http", "ws") + "/gvg"

    try:
        async with websockets.connect(upstream_url, ping_interval=20, ping_timeout=20, max_size=None) as upstream:
            async def from_client():
                # forward binary messages from client to upstream
                while True:
                    msg = await ws.receive_bytes()
                    await upstream.send(msg)

            async def from_upstream():
                # forward binary messages from upstream to client
                while True:
                    data = await upstream.recv()
                    if isinstance(data, bytes):
                        await ws.send_bytes(data)
                    # ignore text frames (protocol uses binary)

            await asyncio.gather(from_client(), from_upstream())
    except WebSocketDisconnect:
        return
    except Exception as e:
        # surface error to client as close with reason
        try:
            await ws.close(code=1011, reason=str(e))
        except Exception:
            pass