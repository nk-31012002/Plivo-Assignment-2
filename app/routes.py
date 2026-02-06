# from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Response, status
# from .hub import hub
# from .schemas import WSRequest
# from datetime import datetime
# import asyncio

# # Use 'router' consistently here
# router = APIRouter()

# @router.post("/topics")
# async def create_topic(data: dict, response: Response):
#     name = data.get("name")
#     if not hub.create_topic(name):
#         response.status_code = 409
#         return {"error": "Topic already exists"}
#     return {"status": "created", "topic": name}

# @router.get("/topics"){
#     async def list_topis():
#         return{
#             "topics" : [
#                 {"name": name, "subscription": len(hub.topics[name])}
#                 for name in hub.topics
#             ]
#         }
# } [cite: 225, 231]

# @router.get("/stats")
# async def get_stats():
#     return {"topics": hub.get_stats()}

# @router.get("/health")
# async def health():
#     return {
#         "uptime_sec": int(time.time() - hub.start_time),
#         "topics": len(hub.topics)
#     }

# @router.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     queue = asyncio.Queue(maxsize=100) # Bounded for Backpressure [cite: 256]
#     subscribed_topics = set()

#     async def send_to_client():
#         try:
#             while True:
#                 msg = await queue.get()
#                 await websocket.send_json(msg)
#         except: pass

#     sender_task = asyncio.create_task(send_to_client())

#     try:
#         while True:
#             raw_data = await websocket.receive_json()
#             req = WSRequest(**raw_data)
#             ts = datetime.utcnow().isoformat() + "Z"

#             if req.type == "subscribe":
#                 if req.topic in hub.topics:
#                     hub.topics[req.topic].add(queue)
#                     subscribed_topics.add(req.topic)
#                     await websocket.send_json({"type": "ack", "topic": req.topic, "status": "ok", "request_id": req.request_id, "ts": ts})
#                 else:
#                     await websocket.send_json({"type": "error", "error": {"code": "TOPIC_NOT_FOUND"}, "ts": ts})

#             elif req.type == "publish":
#                 if req.topic in hub.topics:
#                     hub.stats[req.topic]["messages"] += 1
#                     event = {"type": "event", "topic": req.topic, "message": req.message.dict(), "ts": ts}
#                     for q in hub.topics[req.topic]:
#                         try:
#                             q.put_nowait(event)
#                         except asyncio.QueueFull:
#                             q.get_nowait() # Drop oldest policy [cite: 260]
#                             q.put_nowait(event)
#                     await websocket.send_json({"type": "ack", "status": "ok", "request_id": req.request_id, "ts": ts})

#             elif req.type == "ping":
#                 await websocket.send_json({"type": "pong", "request_id": req.request_id, "ts": ts})

#     except WebSocketDisconnect:
#         for t in subscribed_topics:
#             if t in hub.topics:
#                 hub.topics[t].remove(queue)
#         sender_task.cancel()

import asyncio
import time
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Response, status
from .hub import hub
from .schemas import WSRequest

router = APIRouter()

@router.post("/topics", status_code=201)
async def create_topic(topic_data: dict, response: Response):
    name = topic_data.get("name")
    if not name or not hub.create_topic(name):
        response.status_code = 409
        return {"error": "Topic already exists"}
    return {"status": "created", "topic": name}

@router.get("/topics")
async def list_topics():
    return {
        "topics": [
            {"name": name, "subscribers": len(hub.topics[name])} 
            for name in hub.topics
        ]
    }

@router.delete("/topics/{name}")
async def delete_topic(name: str, response: Response):
    if hub.delete_topic(name):
        return {"status": "deleted", "topic": name}
    response.status_code = 404
    return {"error": "Topic not found"}

@router.get("/health")
async def get_health():
    return {
        "uptime_sec": int(time.time() - hub.start_time),
        "topics": len(hub.topics),
        "subscribers": sum(len(s) for s in hub.topics.values())
    }

@router.get("/stats")
async def get_stats():
    return {"topics": hub.get_stats()}

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    queue = asyncio.Queue(maxsize=100)
    subscribed_topics = set()

    async def send_worker():
        try:
            while True:
                msg = await queue.get()
                await websocket.send_json(msg)
        except: pass

    worker_task = asyncio.create_task(send_worker())

    try:
        while True:
            data = await websocket.receive_json()
            req = WSRequest(**data)
            ts = datetime.utcnow().isoformat() + "Z"

            if req.type == "subscribe":
                if req.topic in hub.topics:
                    hub.topics[req.topic].add(queue)
                    subscribed_topics.add(req.topic)
                    if req.last_n and req.last_n > 0 and req.topic in hub.history:
                        history = hub.history[req.topic][-req.last_n:]
                        for old_msg in history:
                            await queue.put(old_msg)

                    await websocket.send_json({
                        "type": "ack", "topic": req.topic, "status": "ok", 
                        "request_id": req.request_id, "ts": ts
                    })
                else:
                    await websocket.send_json({"type": "error", "error": {"code": "TOPIC_NOT_FOUND"}, "ts": ts})
           
            elif req.type == "unsubscribe":
                if req.topic in hub.topics and queue in hub.topics[req.topic]:
                    hub.topics[req.topic].remove(queue)
                    subscribed_topics.discard(req.topic)
                    await websocket.send_json({
                        "type": "ack", "topic": req.topic, "status": "ok", 
                        "request_id": req.request_id, "ts": ts
                    })

            elif req.type == "publish":
                if req.topic in hub.topics:
                    event = {"type": "event", "topic": req.topic, "message": req.message.dict(), "ts": ts}
                    await hub.publish(req.topic, event)
                    await websocket.send_json({"type": "ack", "status": "ok", "request_id": req.request_id, "ts": ts})

            elif req.type == "ping":
                await websocket.send_json({"type": "pong", "request_id": req.request_id, "ts": ts})

    except WebSocketDisconnect:
        for t in subscribed_topics:
            if t in hub.topics:
                hub.topics[t].remove(queue)
        worker_task.cancel()