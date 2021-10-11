import os
from typing import List
from app.models.pyobjectid import PyObjectId
from bson import ObjectId
from fastapi import APIRouter, Request, HTTPException, Depends
from mongoengine import connect

from app.models.collections import Collection
from auth import AuthHandler

auth_handler = AuthHandler()

router = APIRouter()


def check_can_add_parent_collection(child: Collection, parent: Collection):
    if child.id in parent.child_collections or child.id == parent.id:
        return False
    for each_id in parent.parent_collections:
        current_parent = await router.app.db["collections"].find_one({"_id": ObjectId(each_id)})
        check_can_add_parent_collection(child=child, parent=current_parent)
    return True

@router.post('/collections', response_model=Collection)
async def save_collection(request: Request, user_id=Depends(auth_handler.auth_wrapper)):
    user = await request.app.db["users"].find_one({"_id": ObjectId(user_id)})
    request_json = await request.json()
    request_json["author"] = user["_id"]
    res = await request.app.db["collections"].insert_one(request_json)
    found = await request.app.db["collections"].find_one({'_id': res.inserted_id})
    return Collection.from_mongo(found)


@router.get("/collections", response_model=List[Collection])
async def get_collections(request: Request, skip: int = 0, limit: int = 2):
    collections = []
    for doc in await request.app.db["collections"].find().skip(skip).limit(limit).to_list(length=limit):
        collections.append(doc)
    return collections


@router.get("/collections/{collection_id}")
async def get_collection(collection_id: str, request: Request):
    if (collection := await request.app.db["collections"].find_one({"_id": ObjectId(collection_id)})) is not None:
        return Collection.from_mongo(collection)
    raise HTTPException(status_code=404, detail=f"Collection {collection_id} not found")

@router.post("/collections/{collection_id}/addToParent/{parent_collection_id}")
async def add_collection_to_parent_collection(collection_id: str, parent_collection_id: str, request: Request):
    collection = await request.app.db["collections"].find_one({"_id": ObjectId(collection_id)})
    parent_collection = await request.app.db["collections"].find_one({"_id": ObjectId(parent_collection_id)})
    if collection is not None and parent_collection is not None:
        current_collection = Collection.from_mongo(collection)
        current_parent_collection = Collection.from_mongo(parent_collection)
        can_add = check_can_add_parent_collection(current_collection, current_parent_collection)
        if not can_add:
            return {'status': 'unnecessary'}
        else:
            updated_collection = await request.app.db["collections"].update_one({'_id': ObjectId(collection_id)},{'$push': {'parent_collections': ObjectId(parent_collection_id)}})
            updated_parent_collection = await request.app.db["collections"].update_one({'_id': ObjectId(parent_collection_id)},{'$push': {'child_collections': ObjectId(collection_id)}})
            return {'status': 'ok'}
    raise HTTPException(status_code=404, detail=f"Collection {collection_id} not found or Collection {parent_collection_id} not found")

@router.post("/collections/{collection_id}/removeFromParent/{parent_collection_id}")
async def remove_dataset_from_collection(collection_id: str, parent_collection_id: str, request: Request):
    collection = await request.app.db["collections"].find_one({"_id": ObjectId(collection_id)})
    parent_collection = await request.app.db["collections"].find_one({"_id": ObjectId(parent_collection_id)})
    if collection is not None and parent_collection is not None:
        current_collection = Collection.from_mongo(collection)
        current_parent_collection = Collection.from_mongo(parent_collection)
        if current_collection.id in current_parent_collection.child_collections:
            updated_parent_collection = await request.app.db["collections"].update_one({'_id': ObjectId(parent_collection_id)},{'$pull': {'child_collections': ObjectId(collection_id)}})
        if current_parent_collection.id in current_collection.parent_collections:
            updated_collection = await request.app.db["collections"].update_one({'_id': ObjectId(collection_id)}, {
                '$pull': {'parent_collections': ObjectId(parent_collection_id)}})
        else:
            return {'status': 'ok'}
    raise HTTPException(status_code=404, detail=f"Collection {collection_id} not found or Collection {parent_collection_id} not found")