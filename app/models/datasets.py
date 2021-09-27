from typing import Optional

from bson import ObjectId
from mongoengine import Document, StringField, IntField, DynamicDocument
from pydantic import BaseModel, Field
from app.models.mongomodel import OID, MongoModel


class Dataset(MongoModel):
    name: str
    description: str = None
    views: int
    downloads: int = None


# class MongoDataset(Document):
#     name = StringField()
#     description = StringField()
#     price = IntField()
#     tax = IntField()


class MongoDataset(DynamicDocument):
    pass
