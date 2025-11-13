from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.services import process_statement
from app.models import UploadResponse


router = APIRouter(prefix="/api")


@router.post("/upload-statement", response_model=UploadResponse)
async def upload_statement(file: UploadFile = File(...)):
    """Endpoint to upload bank statement file. For now the service returns a placeholder result.
    The actual parsing and tallying logic will live in `app.services.process_statement`.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    result = await process_statement(file)
    return result