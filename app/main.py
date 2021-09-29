import os
import json
import motor
import uvicorn
from fastapi import Depends, FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import APIRouter, Request, HTTPException
from passlib.context import CryptContext
from app.dependencies import get_query_token, get_token_header
from app.routers import users, datasets, collections
from app.models.users import User
from auth import AuthHandler
from mongoengine import connect


DATABASE_URI = "mongodb://127.0.0.1:27017"
db=DATABASE_URI+"/clowder"
connect(host=db)

auth_handler = AuthHandler()


app = FastAPI(dependencies=[Depends(get_query_token)])

app = FastAPI()

app.include_router(users.router)
app.include_router(datasets.router)
app.include_router(collections.router)


async def authenticate_user(username: str, password: str):
    user = await app.db["users"].find_one({"name": username})
    current_user = User.from_mongo(user)
    if not user:
        return False
    if not current_user.verify_password(password):
        return False
    return current_user




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







@app.get("/")
async def root():
    return {"message": "Hello World!"}

@app.post("/signin")
async def sign_in(request: Request):
    request_json = await request.json()
    username = request_json["username"]
    password = request_json["password"]
    current_user = await authenticate_user(username, password)
    return current_user


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
