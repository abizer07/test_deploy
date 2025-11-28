# app/routes.py
from fastapi import APIRouter, HTTPException
from invoices_api.schemas import InvoiceCreate, InvoiceUpdate
from invoices_api.services import (
    create_invoice_service,
    get_all_invoices_service,
    get_invoice_service,
    update_invoice_service,
    delete_invoice_service,
)

invoices_api_router = APIRouter(prefix="/invoices", tags=["Invoices"])


@invoices_api_router.post("/")
async def create_invoice(data: InvoiceCreate):
    return await create_invoice_service(data)


@invoices_api_router.get("/")
async def get_all_invoices():
    return await get_all_invoices_service()


@invoices_api_router.get("/{invoice_id}")
async def get_invoice(invoice_id: str):
    invoice = await get_invoice_service(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@invoices_api_router.put("/{invoice_id}")
async def update_invoice(invoice_id: str, data: InvoiceUpdate):
    invoice = await update_invoice_service(invoice_id, data)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@invoices_api_router.delete("/{invoice_id}")
async def delete_invoice(invoice_id: str):
    invoice = await delete_invoice_service(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return {"message": "Invoice deleted successfully"}
