from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
import asyncio
import threading
from .schemas import SalesWithoutInventoryRequest, TallyResponse, SalesWithoutInventoryItem
from .services import tally_service

router = APIRouter(prefix="/tally", tags=["Tally Integration"])

@router.post(
    "/sales-without-inventory",
    response_model=TallyResponse,
    summary="Update sales without inventory in Tally",
    description="Send sales data to Tally without inventory information"
)
def update_sales_without_inventory(
    sales_data: SalesWithoutInventoryRequest
):
    """
    Update sales data in Tally without inventory information.
    
    This endpoint sends sales voucher data to Tally ERP system using the API2Books integration.
    """
    try:
        result = tally_service.update_sales_without_inventory(sales_data)
        
        if not result.success:
            raise HTTPException(
                status_code=result.status_code or 400,
                detail=result.message
            )
            
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update sales data in Tally: {str(e)}"
        )

@router.post(
    "/single-sale",
    response_model=TallyResponse,
    summary="Update single sale without inventory",
    description="Send single sales voucher data to Tally"
)
def update_single_sale(sale_item: SalesWithoutInventoryItem):
    """
    Update single sales voucher in Tally without inventory information.
    """
    try:
        sales_data = SalesWithoutInventoryRequest(body=[sale_item])
        result = tally_service.update_sales_without_inventory(sales_data)
        
        if not result.success:
            raise HTTPException(
                status_code=result.status_code or 400,
                detail=result.message
            )
            
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update single sale in Tally: {str(e)}"
        )

@router.post(
    "/delete-uploaded-data",
    response_model=TallyResponse,
    summary="Delete uploaded data from Tally server",
    description="Remove previously uploaded data from the Tally server"
)
def delete_uploaded_data():
    """
    Delete uploaded data from Tally server.
    
    This endpoint calls the ApproveDownload API to remove previously uploaded data
    from the Tally integration server.
    """
    try:
        result = tally_service.delete_uploaded_data()
        
        if not result.success:
            raise HTTPException(
                status_code=result.status_code or 400,
                detail=result.message
            )
            
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete uploaded data: {str(e)}"
        )

def _process_sales_in_background(sales_data: SalesWithoutInventoryRequest):
    """Helper function to process sales in background thread"""
    tally_service.update_sales_without_inventory(sales_data)

@router.post(
    "/sales-without-inventory-background",
    response_model=dict,
    summary="Update sales in background",
    description="Process sales update in background to avoid timeout issues"
)
def update_sales_background(
    sales_data: SalesWithoutInventoryRequest,
    background_tasks: BackgroundTasks
):
    """
    Process sales update in background to avoid timeout issues
    """
    try:
        # Add the task to background
        background_tasks.add_task(
            _process_sales_in_background,
            sales_data
        )
        
        return {
            "success": True,
            "message": "Sales update queued for background processing",
            "data": None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to queue sales update: {str(e)}"
        )

@router.get(
    "/health",
    summary="Health check for Tally integration",
    description="Check if Tally service is configured properly"
)
def health_check():
    """
    Health check endpoint to verify Tally service configuration
    """
    try:
        # Test configuration
        config = {
            "tally_api_url": tally_service.tally_api_url,
            "tally_delete_url": tally_service.tally_delete_url,
            "company_name": tally_service.company_name,
            "template_key": tally_service.template_key,
            "version": tally_service.version
        }
        
        return {
            "success": True,
            "message": "Tally service is configured",
            "config": config
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Tally service configuration error: {str(e)}"
        )