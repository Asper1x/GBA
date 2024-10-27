#uvicorn main:app --reload

from fastapi import FastAPI

from routers import users, dialogs

app = FastAPI()

app.include_router(users.router)
app.include_router(dialogs.router)


@app.get("/")
def read_root():
    return {"todo": "main page"}

