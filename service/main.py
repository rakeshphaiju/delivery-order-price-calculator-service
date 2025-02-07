import os
import uvicorn

from fastapi import FastAPI, Depends
from dotenv import load_dotenv

from service.api.wolt_dopc_service_api import router as wolt_dopc_service_api
from service.auth import router as auth_router
from service.auth import login_manager

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Wolt Delivery Order Price", version=os.environ.get("VERSION", "local")
)

app.include_router(wolt_dopc_service_api)
app.include_router(auth_router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

@app.get("/")
async def home_page(user=Depends(login_manager)):
    return {"Welcome": user.username}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
