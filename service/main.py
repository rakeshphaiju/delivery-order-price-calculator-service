import os
import uvicorn
from http import HTTPStatus as hs

from fastapi import FastAPI, Request, Depends
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.exception_handlers import http_exception_handler
from dotenv import load_dotenv
from starlette.exceptions import HTTPException as StarletteHTTPException

from service.common import logger, NotAuthenticatedException
from service.api.wolt_dopc_service_api import router as wolt_dopc_service_api
from service.auth import router as auth_router, login_manager
from service.db import create_tables

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Wolt Delivery Order Price", version=os.environ.get("VERSION", "local")
)

app.include_router(wolt_dopc_service_api)
app.include_router(auth_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_log_info = {"errors": exc.errors(), "body": exc.body}
    logger.error('RequestValidationError on "{} {}": {}', request.method, request.url.path, error_log_info)
    return JSONResponse(status_code=hs.BAD_REQUEST, content={"detail": str(exc)})


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == hs.INTERNAL_SERVER_ERROR:
        logger.opt(exception=exc.__cause__).critical(
            'Internal server error on "{} {}": {}', request.method, request.url.path, exc.detail
        )
    else:
        logger.error('Error on "{} {}": {} ({})', request.method, request.url.path, exc.status_code, exc.detail)

    return await http_exception_handler(request, exc)


@app.exception_handler(NotAuthenticatedException)
async def auth_exception_handler(request: Request, exc: NotAuthenticatedException):
    """
    Redirect the user to the login page if not logged in
    """
    resp = RedirectResponse("/api/v1/login")
    resp.delete_cookie("access-token")
    return resp

@app.on_event("startup")
async def startup():
    await create_tables()


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

@app.get("/")
async def home_page(user=Depends(login_manager)):
    return {"Welcome": user}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
