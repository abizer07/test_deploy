import os
import io
import re
import pdfplumber
import pandas as pd
from typing import List
from fastapi import UploadFile, HTTPException
from datetime import datetime

# Adjust this import to match your project structure
from app.models import Transaction, UploadResponse


async def process_statement(file: UploadFile) -> UploadResponse:
    """
    Process uploaded bank statement file (PDF, CSV, or XLSX).
    
    - Saves file to /tmp/uploads for debugging
    - Detects file type and parses accordingly
    - Extracts transactions with debits, credits, and balances
    - Returns structured transaction data
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Read file content
    content = await file.read()
    
    # Save file to disk for debugging
    upload_dir = "/tmp/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Detect file type and process accordingly
    file_extension = file.filename.lower().split('.')[-1]
    
    try:
        if file_extension == 'pdf':
            transactions = await parse_pdf_statement(content, file.filename)
        elif file_extension == 'csv':
            transactions = await parse_csv_statement(content, file.filename)
        elif file_extension in ['xlsx', 'xls']:
            transactions = await parse_excel_statement(content, file.filename)
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file format: {file_extension}. Supported formats: PDF, CSV, XLSX"
            )
        
        return UploadResponse(
            filename=file.filename,
            transactions=transactions,
            message=f"Successfully parsed {len(transactions)} transactions"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )


async def parse_pdf_statement(content: bytes, filename: str) -> List[Transaction]:
    """
    Parse PDF bank statement and extract transactions.
    
    Expected format:
    Date Description Debit Credit Balance
    01/10/2025 POS AMAZON 500.00 - 10,000.00
    """
    transactions = []
    
    try:
        # Use BytesIO to read PDF from memory
        pdf_file = io.BytesIO(content)
        
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    lines = text.split("\n")
                    page_transactions = parse_transaction_lines(lines)
                    transactions.extend(page_transactions)
        
        if not transactions:
            raise ValueError("No transactions found in PDF")
            
        return transactions
        
    except Exception as e:
        raise ValueError(f"Error parsing PDF: {str(e)}")


def parse_transaction_lines(lines: List[str]) -> List[Transaction]:
    """
    Parse transaction lines from bank statement text.
    Handles format: Date Description Debit Credit Balance
    """
    transactions = []
    
    # Regex pattern to match transaction lines
    # Handles both numeric values and "-" for empty fields
    txn_pattern = re.compile(
        r"^(\d{2}/\d{2}/\d{4})\s+(.+?)\s+([\d,]+\.\d{2}|-)\s+([\d,]+\.\d{2}|-)\s+([\d,]+\.\d{2})$"
    )
    
    for line in lines:
        line = line.strip()
        
        # Skip header lines and empty lines
        if not line or any(x in line.lower() for x in [
            "bank statement", "date description", "debit credit balance",
            "opening balance", "closing balance", "page"
        ]):
            continue
        
        match = txn_pattern.match(line)
        
        if match:
            date_str, description, debit, credit, balance = match.groups()
            
            # Parse date (format: dd/mm/yyyy)
            try:
                txn_date = datetime.strptime(date_str, "%d/%m/%Y").date()
            except ValueError:
                # If date parsing fails, skip this transaction
                continue
            
            # Convert values, treating "-" as None
            debit_value = None if debit == "-" else float(debit.replace(",", ""))
            credit_value = None if credit == "-" else float(credit.replace(",", ""))
            balance_value = float(balance.replace(",", ""))
            
            transactions.append(Transaction(
                date=txn_date,
                description=description.strip(),
                debit=debit_value,
                credit=credit_value,
                balance=balance_value
            ))
    
    return transactions


async def parse_csv_statement(content: bytes, filename: str) -> List[Transaction]:
    """
    Parse CSV bank statement.
    Expected columns: Date, Description, Debit, Credit, Balance
    """
    try:
        # Read CSV from bytes
        df = pd.read_csv(io.BytesIO(content))
        
        # Normalize column names (case-insensitive)
        df.columns = df.columns.str.strip().str.lower()
        
        # Validate required columns
        required_cols = ['date', 'description', 'debit', 'credit', 'balance']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"CSV must contain columns: {required_cols}")
        
        transactions = []
        
        for _, row in df.iterrows():
            # Parse date
            try:
                if pd.notna(row['date']):
                    # Try multiple date formats
                    date_str = str(row['date'])
                    for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y"]:
                        try:
                            txn_date = datetime.strptime(date_str, fmt).date()
                            break
                        except ValueError:
                            continue
                    else:
                        txn_date = None
                else:
                    txn_date = None
            except:
                txn_date = None
            
            # Parse debit/credit values
            debit_value = None
            credit_value = None
            
            if pd.notna(row['debit']) and str(row['debit']) != '-':
                try:
                    debit_value = float(row['debit'])
                except:
                    pass
            
            if pd.notna(row['credit']) and str(row['credit']) != '-':
                try:
                    credit_value = float(row['credit'])
                except:
                    pass
            
            # Parse balance
            balance_value = None
            if pd.notna(row['balance']):
                try:
                    balance_value = float(row['balance'])
                except:
                    pass
            
            transactions.append(Transaction(
                date=txn_date,
                description=str(row['description']).strip() if pd.notna(row['description']) else None,
                debit=debit_value,
                credit=credit_value,
                balance=balance_value
            ))
        
        return transactions
        
    except Exception as e:
        raise ValueError(f"Error parsing CSV: {str(e)}")


async def parse_excel_statement(content: bytes, filename: str) -> List[Transaction]:
    """
    Parse Excel bank statement.
    Expected columns: Date, Description, Debit, Credit, Balance
    """
    try:
        # Read Excel from bytes
        df = pd.read_excel(io.BytesIO(content))
        
        # Normalize column names
        df.columns = df.columns.str.strip().str.lower()
        
        # Validate required columns
        required_cols = ['date', 'description', 'debit', 'credit', 'balance']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"Excel must contain columns: {required_cols}")
        
        transactions = []
        
        for _, row in df.iterrows():
            # Parse date
            try:
                if pd.notna(row['date']):
                    if isinstance(row['date'], datetime):
                        txn_date = row['date'].date()
                    else:
                        date_str = str(row['date'])
                        for fmt in ["%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y"]:
                            try:
                                txn_date = datetime.strptime(date_str, fmt).date()
                                break
                            except ValueError:
                                continue
                        else:
                            txn_date = None
                else:
                    txn_date = None
            except:
                txn_date = None
            
            # Parse debit/credit values
            debit_value = None
            credit_value = None
            
            if pd.notna(row['debit']) and str(row['debit']) != '-':
                try:
                    debit_value = float(row['debit'])
                except:
                    pass
            
            if pd.notna(row['credit']) and str(row['credit']) != '-':
                try:
                    credit_value = float(row['credit'])
                except:
                    pass
            
            # Parse balance
            balance_value = None
            if pd.notna(row['balance']):
                try:
                    balance_value = float(row['balance'])
                except:
                    pass
            
            transactions.append(Transaction(
                date=txn_date,
                description=str(row['description']).strip() if pd.notna(row['description']) else None,
                debit=debit_value,
                credit=credit_value,
                balance=balance_value
            ))
        
        return transactions
        
    except Exception as e:
        raise ValueError(f"Error parsing Excel: {str(e)}")