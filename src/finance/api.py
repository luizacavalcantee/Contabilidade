 # Endpoint para upload e processamento da planilha
from fastapi import APIRouter, UploadFile, File
from src.finance.process_excel import GestaoFinanceira

router = APIRouter()

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    # Salva o arquivo temporariamente
    with open("temp_upload.xlsx", "wb") as buffer:
        buffer.write(await file.read())
    
    # Usa a classe correta
    gestao = GestaoFinanceira("temp_upload.xlsx")
    return {
        "receita": gestao.calcular_receita_bruta().to_dict(),
        "despesas": gestao.calcular_despesas().to_dict()
    }