from fastapi import FastAPI
from app.routes import router
import uvicorn

app = FastAPI(title="Plivo In-Memory Pub/Sub")

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)