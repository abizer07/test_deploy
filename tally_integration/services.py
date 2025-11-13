import requests
import os
import json
from typing import Dict, Any
from .schemas import SalesWithoutInventoryRequest, TallyResponse

class TallyService:
    def __init__(self):
        self.tally_api_url = os.getenv("TALLY_API_URL", "https://api.api2books.com/api/User/SalesWithoutInventory")
        self.tally_delete_url = os.getenv("TALLY_DELETE_URL", "https://api.api2books.com/api/User/ApproveDownload")
        self.x_auth_key = os.getenv("TALLY_X_AUTH_KEY", "test_992471d0e4cd4d12a0000000000000")
        self.template_key = os.getenv("TALLY_TEMPLATE_KEY", "2")
        self.company_name = os.getenv("TALLY_COMPANY_NAME", "Tally Company Name")
        self.add_auto_master = os.getenv("TALLY_ADD_AUTO_MASTER", "0")
        self.automaster_ids = os.getenv("TALLY_AUTOMASTER_IDS", "1,2,3")
        self.version = os.getenv("TALLY_VERSION", "5")

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for Tally API requests"""
        return {
            "X-Auth-Key": self.x_auth_key,
            "Template-Key": self.template_key,
            "CompanyName": self.company_name,
            "AddAutoMaster": self.add_auto_master,
            "Automasterids": self.automaster_ids,
            "version": self.version,
            "Content-Type": "application/json"
        }

    def update_sales_without_inventory(
        self, 
        sales_data: SalesWithoutInventoryRequest
    ) -> TallyResponse:
        """
        Update sales without inventory in Tally
        """
        try:
            # Convert Pydantic model to dict
            payload = sales_data.dict(by_alias=True)
            
            print(f"Making request to: {self.tally_api_url}")
            print(f"Headers: {self._get_headers()}")
            print(f"Payload sample: {json.dumps(payload, indent=2)[:500]}...")
            
            response = requests.post(
                self.tally_api_url,
                json=payload,
                headers=self._get_headers(),
                timeout=30
            )
            
            # Try to get response text
            try:
                response_data = response.json()
            except:
                response_data = response.text
                
            if response.status_code == 200:
                return TallyResponse(
                    success=True,
                    message="Sales data updated successfully in Tally",
                    data=response_data,
                    status_code=response.status_code
                )
            else:
                return TallyResponse(
                    success=False,
                    message=f"API returned status {response.status_code}: {response.text}",
                    data=response_data,
                    status_code=response.status_code
                )
                
        except requests.exceptions.Timeout:
            return TallyResponse(
                success=False,
                message="Request timeout - Tally API took too long to respond",
                data=None,
                status_code=408
            )
        except requests.exceptions.ConnectionError:
            return TallyResponse(
                success=False,
                message="Connection error - Could not connect to Tally API",
                data=None,
                status_code=503
            )
        except requests.exceptions.HTTPError as e:
            return TallyResponse(
                success=False,
                message=f"HTTP error: {str(e)}",
                data=None,
                status_code=500
            )
        except Exception as e:
            return TallyResponse(
                success=False,
                message=f"Unexpected error: {str(e)}",
                data=None,
                status_code=500
            )

    def delete_uploaded_data(self) -> TallyResponse:
        """
        Delete uploaded data from Tally server
        """
        try:
            # Prepare form data
            form_data = {
                "IsFileReceived": "true",
                "CompanyName": self.company_name
            }
            
            headers = {
                "X-Auth-Key": self.x_auth_key,
                "Template-Key": self.template_key,
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            print(f"Making delete request to: {self.tally_delete_url}")
            print(f"Headers: {headers}")
            print(f"Form data: {form_data}")
            
            response = requests.post(
                self.tally_delete_url,
                data=form_data,
                headers=headers,
                timeout=30
            )
            
            # Try to get response text
            try:
                response_data = response.json()
            except:
                response_data = response.text
                
            if response.status_code == 200:
                return TallyResponse(
                    success=True,
                    message="Uploaded data deleted successfully",
                    data=response_data,
                    status_code=response.status_code
                )
            else:
                return TallyResponse(
                    success=False,
                    message=f"Delete API returned status {response.status_code}: {response.text}",
                    data=response_data,
                    status_code=response.status_code
                )
                
        except requests.exceptions.Timeout:
            return TallyResponse(
                success=False,
                message="Delete request timeout",
                data=None,
                status_code=408
            )
        except requests.exceptions.ConnectionError:
            return TallyResponse(
                success=False,
                message="Delete connection error",
                data=None,
                status_code=503
            )
        except Exception as e:
            return TallyResponse(
                success=False,
                message=f"Delete unexpected error: {str(e)}",
                data=None,
                status_code=500
            )

# Create service instance
tally_service = TallyService()