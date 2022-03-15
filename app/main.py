import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    users,
    files,
    datasets,
    collections,
    authentication,
    folders,
)
from app.config import settings

app = FastAPI(
    title=settings.APP_NAME, openapi_url=f"{settings.API_V2_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(datasets.router, prefix="/datasets", tags=["datasets"])
api_router.include_router(
    collections.router, prefix="/collections", tags=["collections"]
)
api_router.include_router(authentication.router, tags=["login"])
api_router.include_router(folders.router, prefix="/folders", tags=["folders"])

app.include_router(api_router, prefix=settings.API_V2_STR)

# rabbitmq_client = {}
#
#
# @app.on_event("startup")
# async def startup_rabbitmq_client():
#     global rabbitmq_client
#     rabbitmq_client = ExamplePublisher(
#         "amqp://guest:guest@localhost:5672/%2F?connection_attempts=3&heartbeat=3600"
#     )
#     rabbitmq_client.run()
#     return rabbitmq_client
#
#
# @app.on_event("shutdown")
# async def shutdown_rabbitmq_client():
#     global rabbitmq_client
#     rabbitmq_client.stop()


@app.get("/")
async def root():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
