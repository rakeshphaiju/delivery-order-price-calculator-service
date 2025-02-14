from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login import LoginManager

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.context import CryptContext
from starlette.responses import RedirectResponse
from http import HTTPStatus as hs
from datetime import timedelta

from service.db import get_db
from service.models.user import UserDb
from service.common.logger import logger
from service.common.exceptions.AuthenticationException import (
    NotAuthenticatedException,
)


router = APIRouter(tags=["Authenticator"])

login_manager = LoginManager(
    secret="secret-key", token_url="/api/v1/login", use_cookie=True, not_authenticated_exception=NotAuthenticatedException
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@login_manager.user_loader()
async def load_user(username: str):
    return username
    

@router.post("/api/v1/register")
async def register(username: str, password: str, db: AsyncSession = Depends(get_db)):
    # Check if the username already exists
    result = await db.execute(select(UserDb).filter(UserDb.username == username))
    db_user = result.scalar_one_or_none()
    if db_user:
        raise HTTPException(status_code=hs.BAD_REQUEST, detail="Username already registered")

    # Hash the password
    hashed_password = pwd_context.hash(password)

    # Create a new user
    new_user = UserDb(username=username, hashed_password=hashed_password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {"username": new_user.username, "message": "User created successfully"}


@router.post("/api/v1/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """Log user in"""
    
    username = form_data.username
    password = form_data.password
    # Fetch the user from the database
    result = await db.execute(select(UserDb).filter(UserDb.username == username))
    user = result.scalar_one_or_none()
    
    if not username or not password:
        raise HTTPException(status_code=hs.BAD_REQUEST, detail="Bad Request")

    # Verify the username and password
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=hs.UNAUTHORIZED,
            detail="Invalid username or password",
        )

    access_token_expires = timedelta(hours=12)
    access_token = login_manager.create_access_token(data=dict(sub=user.username), expires=access_token_expires)
    response = RedirectResponse(url="/", status_code=hs.FOUND)

    response.set_cookie(key="access-token", value=access_token)
    return response


@router.post("/api/v1/logout")
async def logout(response: Response):
    """Log user out"""

    response = RedirectResponse(url="/", status_code=hs.FOUND)
    response.delete_cookie("access-token")
    return response


@router.get("/api/v1/user")
async def get_user(user=Depends(login_manager)):
    return {"user": user}
  
