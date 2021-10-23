import os
from typing import List
import shutil

from bson import ObjectId
from fastapi import APIRouter, Request, HTTPException, Depends, File, UploadFile
from app.models.datasets import Dataset
from app.models.collections import Collection
from auth import AuthHandler

router = APIRouter()

auth_handler = AuthHandler()

@router.post("/test/")
async def test():
    return {'ok':'test'}

@router.post("/files/")
async def create_file(file: bytes = File(...)):
    print('here')
    return {"file_size": len(file)}


@router.post("/uploadfile/")
async def create_upload_file(request: Request, file: UploadFile = File(...)):
    print('here')
    content = await file.read()
    file_upload = {
        'data': content
    }
    result = await request.app.db["fileuploads"].insert_one(file_upload)
    return {"filename": file.filename}


async def image(image: UploadFile = File(...)):
    print('here')
    with open("destination.png", "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    return {"filename": image.filename}