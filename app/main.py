import os

import motor
import uvicorn
from fastapi import Depends, FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from app.dependencies import get_query_token, get_token_header
from app.routers import users, datasets, collections
import jwt
from typing import Dict
import time

SECRET_KEY = "secretkey"
ALGORITHM = "HS256"

JWT_SECRET = SECRET_KEY
JWT_ALGORITHM = ALGORITHM
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


app = FastAPI(dependencies=[Depends(get_query_token)])

app = FastAPI()

app.include_router(users.router)
app.include_router(datasets.router)
app.include_router(collections.router)

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    print('here')
    as_hashed = get_password_hash(password=plain_password)
    result = pwd_context.verify(plain_password, hashed_password)
    return pwd_context.verify(plain_password, hashed_password)

def token_response(token: str):
    return {"access_token": token}

def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}

def signJWT(user_id: str) -> Dict[str, str]:
    payload = {
        "user_id": user_id,
        "expires": time.time() + 600
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(token)



@app.on_event("startup")
async def startup_db_client():
    # app.mongodb_client = AsyncIOMotorClient(settings.DB_URL)
    # app.mongodb = app.mongodb_client[settings.DB_NAME]
    app.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])
    app.db = app.mongo_client.clowder


@app.on_event("shutdown")
async def shutdown_db_client():
    # app.mongodb_client.close()
    pass

@app.get("/token/{username}/{password}")
async def getToken(username: str, password: str):
    print('username used is:' + username)
    print('password used is: ' + password)
    return {'status':'none'}




@app.get("/")
async def root():
    return {"message": "Hello World!"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
