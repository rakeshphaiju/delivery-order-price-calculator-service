import os
import uvicorn

from fastapi import FastAPI
from dotenv import load_dotenv

import service.api.wolt_dopc_service_api as wolt_dopc_service_api

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Wolt Delivery Order Price", version=os.environ.get("VERSION", "local")
)

app.include_router(wolt_dopc_service_api.router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
