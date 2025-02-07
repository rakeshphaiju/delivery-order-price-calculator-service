from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from starlette.responses import RedirectResponse
from http import HTTPStatus as hs
from datetime import timedelta
from pydantic import BaseModel

from service.common.exceptions.AuthenticationException import (
    AuthenticationException,
    AccessRightsException,
    NotAuthenticatedException,
)


router = APIRouter(tags=["Authenticator"])

login_manager = LoginManager(
    secret="secret-key", token_url="/api/v1/login", use_cookie=True, not_authenticated_exception=NotAuthenticatedException
)

class User(BaseModel):
  username: str
  password: str

# Example user database
fake_db = {
    "user1": User(username="user1", password="password1"),
    "user2": User(username="user2", password="password2"),
}


@login_manager.user_loader()
def load_user(username: str):
    return fake_db.get(username)


@router.post("/api/v1/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Log user in"""

    username = form_data.username
    password = form_data.password

    if username is None or password is None:
        raise HTTPException(status_code=hs.BAD_REQUEST, detail="Bad Request")
    try:
        user = fake_db.get(username)
        if not user or user.password != password:
          raise NotAuthenticatedException("Invalid credentials")
    except AuthenticationException as err:
        raise HTTPException(status_code=hs.UNAUTHORIZED, detail=str(err)) from err
    except AccessRightsException as err:
        raise HTTPException(hs.FORBIDDEN, detail=str(err)) from err

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
    return {"user": user.username}
  
