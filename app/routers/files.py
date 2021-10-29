import os
from pymongo import MongoClient
from gridfs import GridFS
from starlette.responses import FileResponse
from starlette.background import BackgroundTasks
from bson import ObjectId
from app import dependencies
from fastapi import APIRouter, Request, HTTPException, Depends, File, UploadFile
from app.models.datasets import Dataset
from ..auth import AuthHandler

router = APIRouter()

auth_handler = AuthHandler()

client = MongoClient(os.environ["MONGODB_URL"])
current_db = client['clowder']
fs = GridFS(current_db)

def remove_file(path: str) -> None:
    os.unlink(path)

@router.post("/upload/dataset/{dataset_id}")
async def upload_file(dataset_id: str,
                      request: Request,
                      file: UploadFile = File(...),
                      db: MongoClient = Depends(dependencies.get_db)
):
    if (dataset := await db["datasets"].find_one({"_id": ObjectId(dataset_id)})) is not None:
        current_dataset = Dataset.from_mongo(dataset)
        content = await file.read()
        filename = file.filename
        content_type = file.content_type
        try:
            oid = fs.put(content, content_type=content_type, filename=filename)
            updated_dataset = await db["datasets"].update_one({'_id': ObjectId(dataset_id)}, {
                '$push': {'files': ObjectId(oid)}})
        except Exception as e:
            print(e)
        return {"id": str(oid)}
    else:
        return {"status":"dataset not found"}


@router.get("/downloadFile/{file_id}")
async def download(file_id: str,
                   request: Request,
                   background_tasks: BackgroundTasks
):
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
    return {"status": "file not found"}

