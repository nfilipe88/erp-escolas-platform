# backend/main.py
from fastapi import FastAPI

app = FastAPI(title="ERP Escolas API", version="0.1.0")

@app.get("/")
def read_root():
    return {"mensagem": "O Backend do ERP está a funcionar!", "status": "online"}