import os
from typing import List

from bson import ObjectId
from fastapi import APIRouter, Request, HTTPException, Depends
from app.models.datasets import Dataset
from app.models.collections import Collection
from auth import AuthHandler

router = APIRouter()

auth_handler = AuthHandler()

@router.post('/datasets')
async def save_dataset(request: Request, user_id=Depends(auth_handler.auth_wrapper)):
    user = await request.app.db["users"].find_one({"_id": ObjectId(user_id)})
    request_json = await request.json()
    request_json["author"] = user["_id"]
    res = await request.app.db["datasets"].insert_one(request_json)
    found = await request.app.db["datasets"].find_one({'_id': res.inserted_id})
    return Dataset.from_mongo(found)


@router.get("/datasets", response_model=List[Dataset])
async def get_datasets(request: Request, user_id=Depends(auth_handler.auth_wrapper), skip: int = 0, limit: int = 2, mine=False):
    datasets = []
    user = await request.app.db["users"].find_one({"_id": ObjectId(user_id)})
    if mine:
        for doc in await request.app.db["datasets"].find({"author": ObjectId(user_id)}).skip(skip).limit(limit).to_list(length=limit):
            datasets.append(doc)
    else:
        for doc in await request.app.db["datasets"].find().skip(skip).limit(limit).to_list(length=limit):
            datasets.append(doc)
    return datasets


@router.get("/datasets/{dataset_id}")
async def get_dataset(dataset_id: str, request: Request):
    if (dataset := await request.app.db["datasets"].find_one({"_id": ObjectId(dataset_id)})) is not None:
        return Dataset.from_mongo(dataset)
    raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found")

@router.post("/datasets/{dataset_id}/addToCollection/{collection_id}")
async def add_dataset_to_collection(dataset_id: str, collection_id: str, request: Request):
    dataset = await request.app.db["datasets"].find_one({"_id": ObjectId(dataset_id)})
    collection = await request.app.db["collections"].find_one({"_id": ObjectId(collection_id)})
    if dataset is not None and collection is not None:
        current_dataset = Dataset.from_mongo(dataset)
        current_dataset_collections = current_dataset.collections
        if ObjectId(collection_id) in current_dataset_collections:
            return {'status': 'unnecessary'}
        else:
            updated_dataset = await request.app.db["datasets"].update_one({'_id': ObjectId(dataset_id)},{'$push': {'collections': ObjectId(collection_id)}})
            updated_collection = await request.app.db["collections"].update_one({'_id': ObjectId(collection_id)},{'$inc': {'dataset_count': 1}})
            return {'status': 'ok'}
    raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found or Collection {collection_id} not found")

@router.post("/datasets/{dataset_id}/removeFromCollection/{collection_id}")
async def remove_dataset_from_collection(dataset_id: str, collection_id: str, request: Request):
    dataset = await request.app.db["datasets"].find_one({"_id": ObjectId(dataset_id)})
    collection = await request.app.db["collections"].find_one({"_id": ObjectId(collection_id)})
    if dataset is not None and collection is not None:
        current_dataset = Dataset.from_mongo(dataset)
        if ObjectId(collection_id) not in current_dataset.collections:
            return {'status': 'unnecessary'}
        else:
            updated_dataset = await request.app.db["datasets"].update_one({'_id': ObjectId(dataset_id)},{'$pull': {'collections': ObjectId(collection_id)}})
            updated_collection = await request.app.db["collections"].update_one({'_id': ObjectId(collection_id)},{'$inc': {'dataset_count': -1}})
            return {'status':'ok'}
    raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} not found or Collection {collection_id} not found")
