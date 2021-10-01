import os
from typing import List

from bson import ObjectId
from fastapi import APIRouter, Request, HTTPException, Depends
from mongoengine import connect
from pydantic import BaseModel
from app.models.datasets import Dataset, MongoDataset
from auth import AuthHandler

router = APIRouter()

auth_handler = AuthHandler()

DATABASE_URI = "mongodb://127.0.0.1:27017"
db=DATABASE_URI+"/clowder"
connect(host=db)

@router.post('/datasets')
async def save_dataset(request: Request, username=Depends(auth_handler.auth_wrapper)):
    res = await request.app.db["users"].find_one({'name': username})
    request_json = await request.json()
    request_json["creator"] = res["_id"]
    res = await request.app.db["datasets"].insert_one(request_json)
    found = await request.app.db["datasets"].find_one({'_id': res.inserted_id})
    return Dataset.from_mongo(found)


@router.get("/datasets", response_model=List[Dataset])
async def get_datasets(request: Request, skip: int = 0, limit: int = 2):
    datasets = []
    for doc in await request.app.db["datasets"].find().skip(skip).limit(limit).to_list(length=limit):
        datasets.append(doc)
    return datasets


@router.get("/datasets/{dataset_id}")
async def get_dataset(dataset_id: str, request: Request):
    if (dataset := await request.app.db["datasets"].find_one({"_id": ObjectId(dataset_id)})) is not None:
        return Dataset.from_mongo(dataset)
    raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")