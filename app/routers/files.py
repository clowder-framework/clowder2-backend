import os
from typing import List
import shutil
import gridfs
import motor
from pymongo import MongoClient
from gridfs import GridFS
from starlette.responses import FileResponse
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


@router.post("/uploadfile/")
async def create_upload_file(request: Request, file: UploadFile = File(...)):
    print('here')
    content = await file.read()
    file_upload = {
        'data': content
    }
    result = await request.app.db["fileuploads"].insert_one(file_upload)
    return {"filename": file.filename}

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

@router.get("/downloadAFile")
async def download_test(request: Request):
    most_recent_three = fs.find().sort("uploadDate", -1).limit(3)

    for grid_out in most_recent_three:
        filename = grid_out.filename
        content_type = grid_out.content_type
        data = grid_out.read()
        with open(filename, 'wb') as f:
            f.write(data)
        file_path = os.path.join(os.getcwd(), filename)
        if os.path.isfile(file_path):
            # this serves the file
            # return FileResponse(file_path)
            # this downloads the file
            return FileResponse(path=file_path, media_type='application/octet-stream', filename=filename)

        print('here')
        print('here')


    # return FileResponse(file_location, media_type='application/octet-stream', filename=file_name)
    return {"status":"ok"}

