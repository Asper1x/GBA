from fastapi import APIRouter
from classes.dialog import DialogQuery
from model.model import Client

client = Client()
router = APIRouter(tags=["dialogs"])


@router.post("/dialogs/")
async def continue_dialog(dialog: DialogQuery):
    response, tags = client.response(dialog.prompt)

    return {"response": response}
