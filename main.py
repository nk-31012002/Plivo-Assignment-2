from fastapi import FastAPI
from app.routes import router
import uvicorn

app = FastAPI(title="Plivo In-Memory Pub/Sub")

# Include the corrected router
app.include_router(router)

if __name__ == "__main__":
    # 0.0.0.0 is necessary for Docker to expose the port [cite: 273]
    uvicorn.run(app, host="0.0.0.0", port=8000)