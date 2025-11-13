from pydantic import BaseModel, Field
from typing import List, Optional

class SalesWithoutInventoryItem(BaseModel):
    Date: str
    Voucher_No: str = Field(alias="Voucher No")
    Voucher_Type: str = Field(alias="Voucher Type")
    IS_Invoice: str = Field(alias="IS Invoice")
    Bill_Wise_Details: Optional[str] = Field(None, alias="Bill Wise Details")
    Debit_Party_Ledger: str = Field(alias="Debit / Party Ledger")
    Address_1: str = Field(alias="Address 1")
    Address_2: Optional[str] = Field(None, alias="Address 2")
    Address_3: Optional[str] = Field(None, alias="Address 3")
    Address_4: Optional[str] = Field(None, alias="Address 4")
    Pincode: int
    State: str
    Place_of_Supply: str = Field(alias="Place of Supply")
    Country: str
    VAT_Tin_No: Optional[str] = Field(None, alias="VAT Tin No")
    CST_No: Optional[str] = Field(None, alias="CST No")
    Service_Tax_No: Optional[str] = Field(None, alias="Service Tax No")
    GSTIN: str
    GST_Registration_Type: str = Field(alias="GST Registration Type")
    Consignee_Name: Optional[str] = Field(None, alias="Consignee Name")
    Consignee_Add_1: Optional[str] = Field(None, alias="Consignee Add 1")
    Consignee_Add_2: Optional[str] = Field(None, alias="Consignee Add 2")
    Consignee_Add_3: Optional[str] = Field(None, alias="Consignee Add 3")
    Consignee_Add_4: Optional[str] = Field(None, alias="Consignee Add 4")
    Consignee_State: Optional[str] = Field(None, alias="Consignee State")
    Consignee_Country: Optional[str] = Field(None, alias="Consignee Country")
    Consignee_Pincode: Optional[int] = Field(None, alias="Consignee Pincode")
    Consignee_GSTIN: Optional[str] = Field(None, alias="Consignee GSTIN")
    
    # Credit Ledgers - making most optional except the first one
    Credit_Ledger_1: str = Field(alias="Credit Ledger 1")
    Credit_Ledger_1_Amount: float = Field(alias="Credit Ledger 1 Amount")
    Ledger_1_Description: str = Field(alias="Ledger 1 Description")
    
    # Optional credit ledgers 2-30
    Credit_Ledger_2: Optional[str] = Field(None, alias="Credit Ledger 2")
    Credit_Ledger_2_Amount: Optional[float] = Field(None, alias="Credit Ledger 2 Amount")
    Ledger_2_Description: Optional[str] = Field(None, alias="Ledger 2 Description")
    
    Credit_Ledger_3: Optional[str] = Field(None, alias="Credit Ledger 3")
    Credit_Ledger_3_Amount: Optional[float] = Field(None, alias="Credit Ledger 3 Amount")
    Ledger_3_Description: Optional[str] = Field(None, alias="Ledger 3 Description")
    
    # Add more as needed...
    
    Credit_Period: Optional[str] = Field(None, alias="Credit Period")
    Cost_Center: Optional[str] = Field(None, alias="Cost Center")
    Narration: Optional[str] = None
    IRN_Ack_No: Optional[str] = Field(None, alias="IRN Ack No")
    IRN_Ack_Date: Optional[str] = Field(None, alias="IRN Ack Date")
    IRN_No: Optional[str] = Field(None, alias="IRN No")
    IRN_Bill_to_Place: Optional[str] = Field(None, alias="IRN Bill to Place")
    IRN_Ship_to_State: Optional[str] = Field(None, alias="IRN Ship to State")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

class SalesWithoutInventoryRequest(BaseModel):
    body: List[SalesWithoutInventoryItem]

class TallyResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None
    status_code: Optional[int] = None

class DeleteUploadedDataRequest(BaseModel):
    IsFileReceived: str = "true"
    CompanyName: str