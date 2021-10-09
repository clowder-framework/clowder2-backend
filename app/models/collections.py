from typing import Optional, List
import os
from bson import ObjectId
from mongoengine import Document, StringField, IntField, DynamicDocument, connect
from pydantic import BaseModel, Field
from app.models.pyobjectid import PyObjectId
from app.models.mongomodel import OID, MongoModel


class Collection(MongoModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    description: str = ""
    author: PyObjectId
    dataset_count: int = 0


# class MongoDataset(Document):
#     name = StringField()
#     description = StringField()
#     price = IntField()
#     tax = IntField()


class MongoCollection(DynamicDocument):
    pass
