import os
import io
import re
import pdfplumber
import pandas as pd
from fastapi import UploadFile, HTTPException
from datetime import datetime
from typing import List

from motor.motor_asyncio import AsyncIOMotorClient
from app.models import Transaction, UploadResponse


# ------------------------------------------------------------------------------
#                               MONGODB SETUP
# ------------------------------------------------------------------------------
MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017/mydb")

mongo_client = AsyncIOMotorClient(MONGO_URL)
db = mongo_client["mydb"]
transactions_collection = db["transactions"]


async def save_transactions_to_db(transactions, filename: str):
    upload_id = datetime.now().timestamp()

    docs = []
    for txn in transactions:

        # Convert datetime.date → datetime.datetime
        date_val = (
            datetime.combine(txn.date, datetime.min.time())
            if txn.date else None
        )

        docs.append({
            "upload_id": upload_id,
            "filename": filename,
            "date": date_val,          # <-- now valid for MongoDB
            "description": txn.description,
            "debit": txn.debit,
            "credit": txn.credit,
            "balance": txn.balance,
            "created_at": datetime.now()
        })

    if docs:
        await transactions_collection.insert_many(docs)

    return upload_id



# ------------------------------------------------------------------------------
#                               MAIN PROCESS FUNCTION
# ------------------------------------------------------------------------------
async def process_statement(file: UploadFile) -> UploadResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    content = await file.read()

    # Debug save
    os.makedirs("/tmp/uploads", exist_ok=True)
    with open(f"/tmp/uploads/{file.filename}", "wb") as f:
        f.write(content)

    ext = file.filename.lower().split('.')[-1]

    try:
        if ext == "pdf":
            transactions = await parse_pdf(content)
        elif ext == "csv":
            transactions = await parse_csv(content)
        elif ext in ["xlsx", "xls"]:
            transactions = await parse_excel(content)
        else:
            raise HTTPException(400, f"Unsupported file type: {ext}")

        # SAVE TO DATABASE
        await save_transactions_to_db(transactions, file.filename)

        return UploadResponse(
            filename=file.filename,
            transactions=transactions,
            message=f"Parsed and saved {len(transactions)} transactions"
        )

    except Exception as e:
        raise HTTPException(500, f"Error processing file: {str(e)}")


# ------------------------------------------------------------------------------
#                               PDF PARSER
# ------------------------------------------------------------------------------
async def parse_pdf(content: bytes) -> List[Transaction]:
    transactions = []
    pdf_file = io.BytesIO(content)

    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    lines = text.split("\n")
                    transactions.extend(parse_transaction_lines(lines))

        return transactions

    except Exception as e:
        raise ValueError(f"PDF parse error: {str(e)}")


# ------------------------------------------------------------------------------
#                               PDF LINE PARSER
# ------------------------------------------------------------------------------
def parse_transaction_lines(lines: List[str]) -> List[Transaction]:
    txns = []

    pattern = re.compile(
        r"^(\d{2}/\d{2}/\d{4})\s+(.+?)\s+([\d,]+\.\d{2}|-)\s+([\d,]+\.\d{2}|-)\s+([\d,]+\.\d{2})$"
    )

    for line in lines:
        line = line.strip()
        if not line or any(x in line.lower() for x in [
            "opening", "closing", "balance", "date", "page"
        ]):
            continue

        m = pattern.match(line)
        if m:
            date_str, desc, debit, credit, balance = m.groups()

            try:
                date_val = datetime.strptime(date_str, "%d/%m/%Y").date()
            except:
                continue

            debit = None if debit == "-" else float(debit.replace(",", ""))
            credit = None if credit == "-" else float(credit.replace(",", ""))
            balance = float(balance.replace(",", ""))

            txns.append(Transaction(
                date=date_val,
                description=desc.strip(),
                debit=debit,
                credit=credit,
                balance=balance
            ))

    return txns


# ------------------------------------------------------------------------------
#                               CSV PARSER
# ------------------------------------------------------------------------------
async def parse_csv(content: bytes) -> List[Transaction]:
    try:
        df = pd.read_csv(io.BytesIO(content))
        df.columns = df.columns.str.lower().str.strip()
        return build_transactions_from_df(df)

    except Exception as e:
        raise ValueError(f"CSV parse error: {str(e)}")


# ------------------------------------------------------------------------------
#                               EXCEL PARSER
# ------------------------------------------------------------------------------
async def parse_excel(content: bytes) -> List[Transaction]:
    try:
        df = pd.read_excel(io.BytesIO(content))
        df.columns = df.columns.str.lower().str.strip()
        return build_transactions_from_df(df)

    except Exception as e:
        raise ValueError(f"Excel parse error: {str(e)}")


# ------------------------------------------------------------------------------
#                               HELPER FOR CSV + EXCEL
# ------------------------------------------------------------------------------
def build_transactions_from_df(df) -> List[Transaction]:
    required = ['date', 'description', 'debit', 'credit', 'balance']
    if not all(c in df.columns for c in required):
        raise ValueError("Missing required columns")

    txns = []

    for _, row in df.iterrows():
        txns.append(Transaction(
            date=parse_date(row['date']),
            description=str(row['description']),
            debit=parse_number(row['debit']),
            credit=parse_number(row['credit']),
            balance=parse_number(row['balance'])
        ))

    return txns


def parse_date(val):
    if pd.isna(val): return None
    if isinstance(val, datetime): return val.date()

    for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y"]:
        try:
            return datetime.strptime(str(val), fmt).date()
        except:
            pass
    return None


def parse_number(val):
    if pd.isna(val) or val == "-": return None
    try: return float(str(val).replace(",", ""))
    except: return None
