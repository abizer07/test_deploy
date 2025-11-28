# app/services.py
from datetime import datetime
from typing import List
from invoices_api.models import Invoice, InvoiceItem
from invoices_api.schemas import InvoiceCreate, InvoiceUpdate


def calculate_totals(items, tax_percentage, discount):
    sub_total = sum(item["quantity"] * item["unit_price"] for item in items)

    tax_amount = (sub_total * tax_percentage) / 100
    grand_total = sub_total + tax_amount - discount

    return sub_total, tax_amount, grand_total


async def create_invoice_service(data: InvoiceCreate):
    sub_total, tax_amount, grand_total = calculate_totals(
        [item.dict() for item in data.items],
        data.tax_percentage,
        data.discount,
    )

    invoice_items = [
        InvoiceItem(
            **item.dict(),
            total_price=item.quantity * item.unit_price
        )
        for item in data.items
    ]

    invoice = Invoice(
        **data.dict(exclude={"items"}),
        items=invoice_items,
        sub_total=sub_total,
        tax_amount=tax_amount,
        grand_total=grand_total,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    return await invoice.insert()


async def get_all_invoices_service() -> List[Invoice]:
    return await Invoice.find_all().to_list()


async def get_invoice_service(invoice_id: str) -> Invoice:
    return await Invoice.get(invoice_id)


async def update_invoice_service(invoice_id: str, data: InvoiceUpdate):
    invoice = await Invoice.get(invoice_id)
    update_data = data.dict(exclude_unset=True)

    if "items" in update_data:
        sub_total, tax_amount, grand_total = calculate_totals(
            [item.dict() for item in update_data["items"]],
            update_data.get("tax_percentage", invoice.tax_percentage),
            update_data.get("discount", invoice.discount),
        )

        update_data["items"] = [
            InvoiceItem(
                **item.dict(),
                total_price=item.quantity * item.unit_price
            )
            for item in update_data["items"]
        ]

        update_data["sub_total"] = sub_total
        update_data["tax_amount"] = tax_amount
        update_data["grand_total"] = grand_total

    update_data["updated_at"] = datetime.utcnow()
    await invoice.set(update_data)

    return invoice


async def delete_invoice_service(invoice_id: str):
    invoice = await Invoice.get(invoice_id)
    if invoice:
        await invoice.delete()
    return invoice
