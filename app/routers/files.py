import os
from typing import List
import shutil
import gridfs
import motor
from pymongo import MongoClient
from gridfs import GridFS
from starlette.responses import FileResponse
from starlette.background import BackgroundTasks
from bson import ObjectId
from fastapi import APIRouter, Request, HTTPException, Depends, File, UploadFile
from app.models.datasets import Dataset
from app.models.collections import Collection
from auth import AuthHandler

router = APIRouter()

auth_handler = AuthHandler()

client = MongoClient(os.environ["MONGODB_URL"])
current_db = client['clowder']
fs = GridFS(current_db)

def cleanup(temp_file):
    os.remove(temp_file)

def remove_file(path: str) -> None:
    os.unlink(path)

@router.post("/test/")
async def test():
    return {'ok':'test'}

@router.get("/allfiles")
async def get_all_files(request: Request):
    files = []
    skip = 0
    limit = 300
    for doc in await request.app.db["fileuploads"].find().skip(skip).limit(limit).to_list(length=limit):
        files.append(doc)
    return {'ok':'files'}

@router.post("/files/")
async def create_file(file: bytes = File(...)):
    print('here')
    return {"file_size": len(file)}


@router.post("/upload/dataset/{dataset_id}")
async def upload_file(dataset_id: str, request: Request, file: UploadFile = File(...)):
    if (dataset := await request.app.db["datasets"].find_one({"_id": ObjectId(dataset_id)})) is not None:
        current_dataset = Dataset.from_mongo(dataset)
    content = await file.read()
    filename = file.filename
    content_type = file.content_type
    try:
        oid = fs.put(content, content_type=content_type, filename=filename)
        updated_dataset = await request.app.db["datasets"].update_one({'_id': ObjectId(dataset_id)}, {
            '$push': {'files': ObjectId(oid)}})
    except Exception as e:
        print(e)
    return {"id": str(oid)}

@router.post("/uploadfileGridFs/")
async def create_upload_file_gridfs(request: Request, file: UploadFile = File(...)):
    print('here')
    content = await file.read()
    filename = file.filename
    content_type = file.content_type
    try:
        oid = fs.put(content, content_type=content_type, filename=filename)
    except Exception as e:
        print(e)
    return {"filename": file.filename}

@router.get("/downloadFile/{file_id}")
async def download_test(file_id: str, request: Request, background_tasks: BackgroundTasks):
    file = fs.find_one({"_id": ObjectId(file_id)})

    if file is not None:
        filename = file.filename
        data = file.read()
        with open(filename, 'wb') as f:
            f.write(data)
        file_path = os.path.join(os.getcwd(), filename)
        if os.path.isfile(file_path):
            background_tasks.add_task(remove_file, file_path)
            return FileResponse(path=file_path, media_type='application/octet-stream', filename=filename)


    # return FileResponse(file_location, media_type='application/octet-stream', filename=file_name)
    return {"status":"ok"}

