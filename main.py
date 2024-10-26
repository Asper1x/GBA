#uvicorn main:app --reload

from fastapi import FastAPI, Body, HTTPException, status

from routers import users

app = FastAPI()

app.include_router(users.router)



@app.get("/")
def read_root():
    return {"todo": "main page"}

