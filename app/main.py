import uvicorn
from fastapi import Depends, FastAPI

from app.dependencies import get_query_token
from app.routers import users, datasets, collections, authentication

# app = FastAPI(dependencies=[Depends(get_query_token)])

app = FastAPI()

app.include_router(users.router)
app.include_router(datasets.router)
app.include_router(collections.router)
app.include_router(authentication.router)


@app.on_event("startup")
async def startup_db_client():
    pass


@app.on_event("shutdown")
async def shutdown_db_client():
    pass


@app.get("/")
async def root():
    return {"message": "Hello World!"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
