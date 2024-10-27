import os
from fastapi import APIRouter
from classes.dialog import DialogQuery
from model.model import Client
from typing import Optional, List
from fastapi import FastAPI, Body, HTTPException, status, Form

from fastapi.responses import Response
from pydantic import ConfigDict, BaseModel, Field
from pydantic.functional_validators import BeforeValidator

from bson import ObjectId
import motor.motor_asyncio
from pymongo import ReturnDocument

from routers.users import UserModel, UsersCollection, user_collection

from typing_extensions import Annotated

from MONGODB_URL import MONGODB_URL


ai_client = Client()
router = APIRouter(tags=["dialogs"])


client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)

PyObjectId = Annotated[str, BeforeValidator(str)]

db = client.get_database("main")
dialog_collection = db.get_collection("dialogs")

class DialogModel(BaseModel):
    """
    Container for a single dialog record.
    """
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    user_id: str = Field(...)
    content: List[str] = Field(...)
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "user_id": "",
                "content" : [],
            }
        },
    )

class UpdateDialogModel(BaseModel):
    """
    A set of optional updates to be made to a document in the database.
    """

    content: Optional[List[str]] = None
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "content" : [],
            }
        },
    )

class DialogsCollection(BaseModel):
    """
    Container for a collection of dialog records.
    """
    dialogs: List[DialogModel]

user_dialogs = {}

@router.get("/user/{id}")
async def get_user_by_id(id: str):
    """
    Get a user by their unique ID.
    """
    try:
        objectID = ObjectId(id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid ID format")


    searched_user = await user_collection.find_one({"_id" : objectID})

    if searched_user is None:
        raise HTTPException(status_code=404, detail='User not found.')
    user: UserModel = UserModel(**searched_user)
    return user

@router.post("/create_dialog/{id}")
async def create_dialog(dialog: DialogQuery, id: str):

    existing_dialog = await dialog_collection.find_one({"user_id": id})
    if existing_dialog:
        return {"error": "user already has dialog. Must continue dialog."}

    try:
        objectID = ObjectId(id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    searched_user = await user_collection.find_one({"_id": objectID})
    if searched_user is None:
        raise HTTPException(status_code=404, detail='User not found.')

    response = ai_client.response(dialog.prompt, searched_user)
    
    
    await dialog_collection.insert_one(
        DialogModel(user_id=id, content=[dialog.prompt, response]).model_dump(by_alias=True)
    )

    return {"user_request" : [dialog.prompt, UserModel(**searched_user)], "response": response}

@router.put("/continue_dialog/{id}")
async def continue_dialog(dialog: DialogQuery, id: str):

    existing_dialog = await dialog_collection.find_one({"user_id": id})
    if not existing_dialog:
        return {"error": "User doesn't have a dialog. Must create one."}
    #todo change user data 
    
    try:
        objectID = ObjectId(id)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    searched_user = await user_collection.find_one({"_id": objectID})
    if searched_user is None:
        raise HTTPException(status_code=404, detail='User not found.')

    response = ai_client.response(dialog.prompt, searched_user)
    
    
    
    await dialog_collection.find_one_and_update(
        {"user_id": id}, {"$push": {"content": [dialog.prompt, response]}}
    )

    return {"user_request": [dialog.prompt, UserModel(**searched_user)], "response": response}




@router.get("/get_dialog/")
async def get_dialog():
    dialogs = await dialog_collection.find().to_list(1000)

    processed_dialogs = []
    for dialog in dialogs:
        content = dialog.get("content", [])
        if not isinstance(content, list) or not all(isinstance(item, str) for item in content):
            content = [str(item) for item in content]
        
        dialog_model = DialogModel(
            id=str(dialog.get("_id")),
            user_id=dialog.get("user_id"),
            content=content
        )
        
        processed_dialogs.append(dialog_model)

    return DialogsCollection(dialogs=processed_dialogs)
