# Inicialização do servidor FastAPI
from fastapi import FastAPI
from src.finance.api import router

app = FastAPI()

# Incluir as rotas do processamento
app.include_router(router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "API de Processamento de Planilhas Online"}