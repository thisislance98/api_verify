#!/usr/bin/env python3
"""
Concur Expense SDK
A comprehensive SDK for interacting with Concur's expense management APIs.
Supports reports, expenses, expense entries, and related operations.
"""

import os
import requests
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date
from dataclasses import dataclass, asdict
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConcurAPIError(Exception):
    """Base exception for Concur API errors."""
    pass


class AuthenticationError(ConcurAPIError):
    """Raised when authentication fails."""
    pass


class NotFoundError(ConcurAPIError):
    """Raised when a resource is not found."""
    pass


class ValidationError(ConcurAPIError):
    """Raised when request validation fails."""
    pass


class ReportStatus(Enum):
    """Expense report status enumeration."""
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    APPROVED = "Approved"
    PAID = "Paid"
    REJECTED = "Rejected"


class ExpenseType(Enum):
    """Common expense types."""
    AIRFARE = "AIRFR"
    HOTEL = "LODNG"
    MEALS = "MEALS"
    CAR_RENTAL = "CARRT"
    TAXI = "TAXIC"
    PARKING = "PARKN"
    PHONE = "PHONE"
    INTERNET = "INTRN"
    OTHER = "OTHER"


@dataclass
class ConcurConfig:
    """Configuration for Concur API connection."""
    client_id: str
    client_secret: str
    username: str
    password: str
    base_url: str = "https://integration.api.concursolutions.com"
    token_url: str = "https://integration.api.concursolutions.com/oauth2/v0/token"
    api_version: str = "v4"  # Updated to use v4 endpoints
    login_url: Optional[str] = None  # For US2 or other data centers


@dataclass
class ExpenseReport:
    """Represents an expense report."""
    id: Optional[str] = None
    name: Optional[str] = None
    purpose: Optional[str] = None
    business_purpose: Optional[str] = None
    total: Optional[float] = None
    currency_code: Optional[str] = None
    submission_date: Optional[str] = None
    approval_status: Optional[str] = None
    workflow_step: Optional[str] = None
    owner_name: Optional[str] = None
    created_date: Optional[str] = None
    last_modified_date: Optional[str] = None
    country: Optional[str] = None
    policy_id: Optional[str] = None
    report_version: Optional[int] = None


@dataclass
class ExpenseEntry:
    """Represents an expense entry within a report."""
    id: Optional[str] = None
    report_id: Optional[str] = None
    expense_type: Optional[str] = None
    transaction_amount: Optional[float] = None
    transaction_currency_code: Optional[str] = None
    transaction_date: Optional[str] = None
    business_purpose: Optional[str] = None
    vendor_description: Optional[str] = None
    city_name: Optional[str] = None
    country_code: Optional[str] = None
    payment_type: Optional[str] = None
    receipt_required: Optional[bool] = None
    has_receipt: Optional[bool] = None


class ConcurExpenseSDK:
    """
    Main SDK class for interacting with Concur Expense APIs.
    Provides methods for managing reports, expenses, and related operations.
    """

    def __init__(self, config: Optional[ConcurConfig] = None):
        """
        Initialize the Concur Expense SDK.
        
        Args:
            config: ConcurConfig object or None to load from environment variables
        """
        if config:
            self.config = config
        else:
            self.config = self._load_config_from_env()
        
        self._access_token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None
        self.session = requests.Session()

    def _load_config_from_env(self) -> ConcurConfig:
        """Load configuration from environment variables."""
        required_vars = {
            'client_id': 'CONCUR_CLIENT_ID',
            'client_secret': 'CONCUR_CLIENT_SECRET',
            'username': 'CONCUR_USERNAME',
            'password': 'CONCUR_PASSWORD'
        }
        
        config_values = {}
        missing_vars = []
        
        for key, env_var in required_vars.items():
            value = os.getenv(env_var)
            if not value:
                missing_vars.append(env_var)
            config_values[key] = value
        
        if missing_vars:
            raise AuthenticationError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        # Optional: load custom base URL and token URL if provided
        if os.getenv('CONCUR_API_BASE_URL'):
            config_values['base_url'] = os.getenv('CONCUR_API_BASE_URL')
        
        if os.getenv('CONCUR_TOKEN_URL'):
            config_values['token_url'] = os.getenv('CONCUR_TOKEN_URL')
        
        if os.getenv('CONCUR_BASE_URL'):
            config_values['login_url'] = os.getenv('CONCUR_BASE_URL')
        
        return ConcurConfig(**config_values)

    def _get_access_token(self) -> str:
        """Get or refresh the access token."""
        if self._access_token and self._token_expiry and datetime.now() < self._token_expiry:
            return self._access_token
        
        payload = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "grant_type": "password",
            "username": self.config.username,
            "password": self.config.password,
        }
        
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        try:
            response = self.session.post(self.config.token_url, data=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            self._access_token = data["access_token"]
            # Assume token expires in 1 hour if not specified
            expires_in = data.get("expires_in", 3600)
            from datetime import timedelta
            self._token_expiry = datetime.now() + timedelta(seconds=expires_in)
            
            logger.info("Successfully obtained access token")
            return self._access_token
            
        except requests.RequestException as e:
            error_msg = f"Error requesting token: {e}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f"\nResponse: {e.response.text}"
            raise AuthenticationError(error_msg)

    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make an authenticated request to the Concur API."""
        access_token = self._get_access_token()
        
        headers = kwargs.pop('headers', {})
        headers.update({
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
        
        # Use direct v4 endpoints like the notebook
        url = f"{self.config.base_url}/{endpoint}"
        
        try:
            response = self.session.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            return response
            
        except requests.HTTPError as e:
            if e.response.status_code == 401:
                # Token might be expired, clear it and retry once
                self._access_token = None
                access_token = self._get_access_token()
                headers["Authorization"] = f"Bearer {access_token}"
                response = self.session.request(method, url, headers=headers, **kwargs)
                response.raise_for_status()
                return response
            elif e.response.status_code == 404:
                raise NotFoundError(f"Resource not found: {e.response.text}")
            elif e.response.status_code == 400:
                raise ValidationError(f"Bad request: {e.response.text}")
            else:
                raise ConcurAPIError(f"API error {e.response.status_code}: {e.response.text}")
        except requests.RequestException as e:
            raise ConcurAPIError(f"Request failed: {e}")

    # REPORT METHODS
    
    def list_reports(self, limit: int = 25, user: Optional[str] = None) -> Dict[str, Any]:
        """
        List expense reports.
        
        Args:
            limit: Maximum number of reports to return (1-100)
            user: User ID to filter reports (optional)
            
        Returns:
            Dictionary containing reports and metadata
        """
        # Get user ID if not provided
        if not user:
            user = self.get_user_id()
            if not user:
                raise AuthenticationError("Could not determine user ID")
        
        # Use v4 endpoint like the notebook
        endpoint = f"expensereports/v4/users/{user}/context/TRAVELER/reports"
        response = self._make_request("GET", endpoint)
        data = response.json()
        
        reports = []
        for item in data.get('content', []):
            report = ExpenseReport(
                id=item.get('reportId'),
                name=item.get('name'),
                purpose=item.get('purpose'),
                business_purpose=item.get('businessPurpose'),
                total=item.get('approvedAmount', {}).get('value') if item.get('approvedAmount') else None,
                currency_code=item.get('approvedAmount', {}).get('currencyCode') if item.get('approvedAmount') else None,
                submission_date=item.get('reportDate'),
                approval_status=item.get('approvalStatus'),
                workflow_step=item.get('workflowStep'),
                owner_name=item.get('ownerName'),
                created_date=item.get('creationDate'),
                last_modified_date=item.get('lastModifiedDate'),
                country=item.get('country'),
                policy_id=item.get('policyId'),
                report_version=item.get('reportVersion')
            )
            reports.append(asdict(report))
        
        return {
            'success': True,
            'reports': reports,
            'count': len(reports),
            'content': data.get('content', []),  # Keep original v4 format too
            'totalElements': data.get('totalElements'),
            'totalPages': data.get('totalPages')
        }

    def get_report_by_id(self, report_id: str, user: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a single expense report by ID including workflow history.
        
        Args:
            report_id: The ID of the report to retrieve
            user: User ID (optional, defaults to current user)
            
        Returns:
            Dictionary containing report details and workflow information
        """
        # Get user ID if not provided
        if not user:
            user = self.get_user_id()
            if not user:
                raise AuthenticationError("Could not determine user ID")
        
        # Use v4 endpoint to get single report
        endpoint = f"expensereports/v4/reports/{report_id}"
        
        try:
            response = self._make_request("GET", endpoint)
            data = response.json()
            
            # The V4 API returns the report object directly
            # Map to our ExpenseReport structure
            report_data = {
                'id': data.get('reportId') or report_id,
                'reportId': data.get('reportId') or report_id,
                'name': data.get('name'),
                'purpose': data.get('purpose'),
                'businessPurpose': data.get('businessPurpose'),
                'total': data.get('approvedAmount', {}).get('value') if data.get('approvedAmount') else None,
                'currencyCode': data.get('approvedAmount', {}).get('currencyCode') if data.get('approvedAmount') else None,
                'reportDate': data.get('reportDate'),
                'submitDate': data.get('submitDate'),
                'approvalStatus': data.get('approvalStatus'),
                'approvalStatusName': data.get('approvalStatusName'),
                'workflowStep': data.get('workflowStep'),
                'ownerName': data.get('ownerName'),
                'creationDate': data.get('creationDate'),
                'lastModifiedDate': data.get('lastModifiedDate'),
                'country': data.get('country'),
                'policyId': data.get('policyId'),
                'policyName': data.get('policyName'),
                'reportVersion': data.get('reportVersion'),
                'ledger': data.get('ledger'),
                'customData': data.get('customData'),
                'expenseEntriesList': data.get('expenseEntriesList'),
                # Include any workflow-related fields
                'workflow': data.get('workflow'),
                'workflowHistory': data.get('workflowHistory'),
                'transitions': data.get('transitions'),
                'approverName': data.get('approverName'),
                'approvalDate': data.get('approvalDate'),
                # Keep all original fields for completeness
                **data
            }
            
            return {
                'success': True,
                'report': report_data,
                'api_version': 'v4',
                'message': f'Successfully retrieved report {report_id}'
            }
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return {
                    'success': False,
                    'report': None,
                    'message': f'Report {report_id} not found',
                    'error_code': 404
                }
            raise

    def get_reports_to_approve(self, user: Optional[str] = None, approval_status: Optional[str] = None) -> Dict[str, Any]:
        """
        Get expense reports that need approval as a manager.
        
        CSV Row #1: Can I see all expense reports I need to approve this week?
        
        Args:
            user: User ID (optional, uses current user if not provided)
            approval_status: Filter by approval status (e.g., 'SUBMITTED', 'PENDING', optional)
            
        Returns:
            Dictionary containing reports to approve and metadata
        """
        # Get user ID if not provided
        if not user:
            user = self.get_user_id()
            if not user:
                raise AuthenticationError("Could not determine user ID")
        
        # Use v4 endpoint with MANAGER context
        endpoint = f"expensereports/v4/users/{user}/context/MANAGER/reportsToApprove"
        
        # Add approval status filter if provided
        params = {}
        if approval_status:
            params['approvalStatus'] = approval_status
        
        response = self._make_request("GET", endpoint, params=params)
        data = response.json()
        
        # Handle both list response and object with content
        items = data if isinstance(data, list) else data.get('content', [])
        
        reports = []
        for item in items:
            report = ExpenseReport(
                id=item.get('reportId'),
                name=item.get('name'),
                purpose=item.get('purpose'),
                business_purpose=item.get('businessPurpose'),
                total=item.get('approvedAmount', {}).get('value') if item.get('approvedAmount') else None,
                currency_code=item.get('approvedAmount', {}).get('currencyCode') if item.get('approvedAmount') else None,
                submission_date=item.get('reportDate'),
                approval_status=item.get('approvalStatus'),
                workflow_step=item.get('workflowStep'),
                owner_name=item.get('ownerName'),
                created_date=item.get('creationDate'),
                last_modified_date=item.get('lastModifiedDate'),
                country=item.get('country'),
                policy_id=item.get('policyId'),
                report_version=item.get('reportVersion')
            )
            reports.append(asdict(report))
        
        return {
            'success': True,
            'reports': reports,
            'count': len(reports),
            'content': items,  # Keep original v4 format too
            'totalElements': data.get('totalElements') if isinstance(data, dict) else len(items),
            'totalPages': data.get('totalPages') if isinstance(data, dict) else 1,
            'message': f'Retrieved {len(reports)} reports to approve'
        }

    def get_overdue_reports_for_approval(self, days_overdue: int = 7, 
                                        approval_status_code: str = "A_PEND",
                                        limit: int = 50) -> Dict[str, Any]:
        """
        Get expense reports that are overdue for approval using v3.0 API.
        
        CSV Row #2: Which expense reports are overdue for approval?
        
        Args:
            days_overdue: Number of days past submission date to consider overdue (default: 7)
            approval_status_code: Approval status code (default: A_PEND for pending)
            limit: Maximum number of reports to return (default: 50)
            
        Returns:
            Dictionary containing overdue reports and metadata
        """
        from datetime import datetime, timedelta
        
        # Calculate the date threshold (7 days ago by default)
        threshold_date = (datetime.now() - timedelta(days=days_overdue)).strftime("%Y-%m-%d")
        
        # Use v3.0 expense reports endpoint with filters
        endpoint = "api/v3.0/expense/reports"
        
        params = {
            'approvalStatusCode': approval_status_code,
            'submitDateBefore': threshold_date,
            'limit': limit,
            'user': 'ALL'  # Get reports from all users that current user can see
        }
        
        try:
            response = self._make_request("GET", endpoint, params=params)
            data = response.json()
            
            # v3 API returns Items array
            items = data.get('Items', [])
            
            reports = []
            for item in items:
                # Calculate days overdue
                submit_date_str = item.get('SubmitDate', '')
                days_since_submission = None
                if submit_date_str:
                    try:
                        submit_date = datetime.fromisoformat(submit_date_str.replace('Z', '+00:00'))
                        days_since_submission = (datetime.now() - submit_date.replace(tzinfo=None)).days
                    except:
                        pass
                
                report = ExpenseReport(
                    id=item.get('ID'),
                    name=item.get('Name'),
                    purpose=item.get('Purpose'),
                    business_purpose=item.get('BusinessPurpose'),
                    total=item.get('Total'),
                    currency_code=item.get('CurrencyCode'),
                    submission_date=submit_date_str,
                    approval_status=item.get('ApprovalStatusName'),
                    workflow_step=item.get('WorkflowStepName'),
                    owner_name=item.get('OwnerName'),
                    created_date=item.get('CreateDate'),
                    last_modified_date=item.get('LastModifiedDate'),
                    country=item.get('Country'),
                    policy_id=item.get('PolicyID')
                )
                
                report_dict = asdict(report)
                report_dict['days_since_submission'] = days_since_submission
                reports.append(report_dict)
            
            return {
                'success': True,
                'reports': reports,
                'count': len(reports),
                'days_threshold': days_overdue,
                'approval_status': approval_status_code,
                'threshold_date': threshold_date,
                'message': f'Retrieved {len(reports)} reports overdue for approval (>{days_overdue} days)'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to retrieve overdue reports: {str(e)}'
            }

    def get_reports_open_more_than_n_days(self, days_open: int = 30, 
                                          approval_status_code: str = "A_PEND",
                                          limit: int = 50) -> Dict[str, Any]:
        """
        Get expense reports that have been open (created but not closed) for more than N days.
        
        CSV Row #23: Which reports have been open for more than 30 days?
        
        This differs from overdue reports - it looks at createDate rather than submitDate.
        A report is "open" from when it's created until it's fully processed/closed.
        
        Args:
            days_open: Number of days since creation to consider "open" (default: 30)
            approval_status_code: Approval status code (default: A_PEND for pending)
            limit: Maximum number of reports to return (default: 50)
            
        Returns:
            Dictionary containing reports open for more than N days and metadata
        """
        from datetime import datetime, timedelta
        
        # Calculate the date threshold (30 days ago by default)
        threshold_date = (datetime.now() - timedelta(days=days_open)).strftime("%Y-%m-%d")
        
        # Use v3.0 expense reports endpoint with filters
        endpoint = "api/v3.0/expense/reports"
        
        params = {
            'approvalStatusCode': approval_status_code,
            'createDateBefore': threshold_date,  # Key difference: createDate vs submitDate
            'limit': limit,
            'user': 'ALL'  # Get reports from all users that current user can see
        }
        
        try:
            response = self._make_request("GET", endpoint, params=params)
            data = response.json()
            
            # v3 API returns Items array
            items = data.get('Items', [])
            
            reports = []
            for item in items:
                # Calculate days since creation
                create_date_str = item.get('CreateDate', '')
                days_since_creation = None
                if create_date_str:
                    try:
                        create_date = datetime.fromisoformat(create_date_str.replace('Z', '+00:00'))
                        days_since_creation = (datetime.now() - create_date.replace(tzinfo=None)).days
                    except:
                        pass
                
                report = ExpenseReport(
                    id=item.get('ID'),
                    name=item.get('Name'),
                    purpose=item.get('Purpose'),
                    business_purpose=item.get('BusinessPurpose'),
                    total=item.get('Total'),
                    currency_code=item.get('CurrencyCode'),
                    submission_date=item.get('SubmitDate'),
                    approval_status=item.get('ApprovalStatusName'),
                    workflow_step=item.get('WorkflowStepName'),
                    owner_name=item.get('OwnerName'),
                    created_date=create_date_str,
                    last_modified_date=item.get('LastModifiedDate'),
                    country=item.get('Country'),
                    policy_id=item.get('PolicyID')
                )
                
                report_dict = asdict(report)
                report_dict['days_since_creation'] = days_since_creation
                report_dict['ApprovalStatusCode'] = item.get('ApprovalStatusCode')
                report_dict['PaymentStatusCode'] = item.get('PaymentStatusCode')
                reports.append(report_dict)
            
            return {
                'success': True,
                'reports': reports,
                'count': len(reports),
                'days_threshold': days_open,
                'approval_status': approval_status_code,
                'threshold_date': threshold_date,
                'message': f'Retrieved {len(reports)} reports open for more than {days_open} days'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to retrieve reports open for more than {days_open} days: {str(e)}'
            }

    def get_draft_reports(self, limit: int = 50) -> Dict[str, Any]:
        """
        Get draft expense reports that haven't been submitted yet using v3.0 API.
        
        CSV Row #16: Show me my draft reports that haven't been submitted yet
        
        Args:
            limit: Maximum number of reports to return (default: 50)
            
        Returns:
            Dictionary containing draft reports and metadata
        """
        # Use v3.0 expense reports endpoint with A_NOTF filter (Not Submitted)
        endpoint = "api/v3.0/expense/reports"
        
        # V3 API requires loginID (username) for the user parameter, not "me"
        params = {
            'approvalStatusCode': 'A_NOTF',  # A_NOTF = Not Submitted (Draft)
            'user': self.config.username,  # Use loginID (username) for current user
            'limit': limit
        }
        
        try:
            response = self._make_request("GET", endpoint, params=params)
            data = response.json()
            
            return {
                'success': True,
                'Items': data.get('Items', []),
                'NextPage': data.get('NextPage'),
                'status_code': response.status_code,
                'count': len(data.get('Items', [])),
                'message': f'Retrieved {len(data.get("Items", []))} draft reports'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to retrieve draft reports: {str(e)}'
            }

    def get_reports_sent_back_to_employees(self, limit: int = 50, user: str = 'ALL') -> Dict[str, Any]:
        """
        Get expense reports that have been sent back to employees (returned for correction).
        
        CSV Row #3: Show me expense reports that were sent back to employees
        
        Args:
            limit: Maximum number of reports to return (default: 50)
            user: User filter - 'ALL' for all users, or specific user ID
            
        Returns:
            Dictionary containing reports sent back and metadata
        """
        from datetime import datetime
        
        # Use v3.0 expense reports endpoint with A_RESU filter
        endpoint = "api/v3.0/expense/reports"
        
        params = {
            'approvalStatusCode': 'A_RESU',  # A_RESU = Approval - Returned to User
            'limit': limit,
            'user': user
        }
        
        try:
            response = self._make_request("GET", endpoint, params=params)
            data = response.json()
            
            # v3 API returns Items array
            items = data.get('Items', [])
            
            reports = []
            for item in items:
                # Get last comment/reason for return if available
                last_comment = item.get('LastComment', '')
                
                # Calculate days since last modification
                last_modified_str = item.get('LastModifiedDate', '')
                days_since_modified = None
                if last_modified_str:
                    try:
                        last_modified = datetime.fromisoformat(last_modified_str.replace('Z', '+00:00'))
                        days_since_modified = (datetime.now() - last_modified.replace(tzinfo=None)).days
                    except:
                        pass
                
                report = ExpenseReport(
                    id=item.get('ID'),
                    name=item.get('Name'),
                    purpose=item.get('Purpose'),
                    business_purpose=item.get('BusinessPurpose'),
                    total=item.get('Total'),
                    currency_code=item.get('CurrencyCode'),
                    submission_date=item.get('SubmitDate'),
                    approval_status=item.get('ApprovalStatusName'),
                    workflow_step=item.get('WorkflowStepName'),
                    owner_name=item.get('OwnerName'),
                    created_date=item.get('CreateDate'),
                    last_modified_date=last_modified_str,
                    country=item.get('Country'),
                    policy_id=item.get('PolicyID')
                )
                
                report_dict = asdict(report)
                report_dict['last_comment'] = last_comment
                report_dict['days_since_modified'] = days_since_modified
                reports.append(report_dict)
            
            return {
                'success': True,
                'reports': reports,
                'count': len(reports),
                'approval_status': 'A_RESU',
                'message': f'Retrieved {len(reports)} reports sent back to employees'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to retrieve reports sent back to employees: {str(e)}'
            }

    def get_pending_reimbursements_total(self, user: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate the total amount in pending reimbursements for the user.
        
        CSV Row #9: What's the total amount in my pending reimbursements?
        
        Args:
            user: User ID (optional, uses current user if not provided)
            
        Returns:
            Dictionary containing total pending reimbursement amount and report details
        """
        # Get user ID if not provided
        if not user:
            user = self.get_user_id()
            if not user:
                raise AuthenticationError("Could not determine user ID")
        
        # Use v4 endpoint to get reports with SUBMITTED and APPROVED status
        endpoint = f"expensereports/v4/users/{user}/context/TRAVELER/reports"
        
        try:
            response = self._make_request("GET", endpoint)
            data = response.json()
            
            # Handle both list response and object with content
            items = data if isinstance(data, list) else data.get('content', [])
            
            total_pending = 0.0
            pending_reports = []
            currency_codes = set()
            
            for item in items:
                # V4 API uses approvalStatusId (not approvalStatus)
                approval_status_id = item.get('approvalStatusId', '').upper()
                
                # Filter for PENDING (A_PEND) or APPROVED (A_APPR) reports
                # A_PEND = Submitted and waiting for approval
                # A_APPR = Approved and waiting for payment/extraction
                if approval_status_id in ['A_PEND', 'A_APPR']:
                    # Get amount due to employee
                    amount_due_employee = item.get('amountDueEmployee', {})
                    amount = amount_due_employee.get('value', 0) if isinstance(amount_due_employee, dict) else 0
                    currency = amount_due_employee.get('currencyCode', 'USD') if isinstance(amount_due_employee, dict) else 'USD'
                    
                    # Only include reports with amount due > 0
                    if amount > 0:
                        # Track currency codes
                        currency_codes.add(currency)
                        
                        # Add to total
                        total_pending += amount
                        
                        # Create report object
                        report = ExpenseReport(
                            id=item.get('reportId'),
                            name=item.get('name'),
                            purpose=item.get('purpose'),
                            business_purpose=item.get('businessPurpose'),
                            total=item.get('approvedAmount', {}).get('value') if item.get('approvedAmount') else None,
                            currency_code=currency,
                            submission_date=item.get('reportDate'),
                            approval_status=approval_status_id,
                            workflow_step=item.get('workflowStep'),
                            owner_name=item.get('ownerName'),
                            created_date=item.get('creationDate'),
                            last_modified_date=item.get('lastModifiedDate'),
                            country=item.get('country'),
                            policy_id=item.get('policyId'),
                            report_version=item.get('reportVersion')
                        )
                        
                        report_dict = asdict(report)
                        report_dict['amount_due_employee'] = amount
                        pending_reports.append(report_dict)
            
            # Determine primary currency (most common or first one)
            primary_currency = list(currency_codes)[0] if currency_codes else 'USD'
            
            return {
                'success': True,
                'total_pending': total_pending,
                'currency_code': primary_currency,
                'currency_codes': list(currency_codes),
                'reports': pending_reports,
                'count': len(pending_reports),
                'message': f'Total pending reimbursements: {total_pending} {primary_currency} across {len(pending_reports)} reports'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to retrieve pending reimbursements: {str(e)}'
            }

    def get_reports_in_exception_review(self, limit: int = 50, user: str = 'ALL') -> Dict[str, Any]:
        """
        Get expense reports that are stuck in exception review.
        
        CSV Row #7: Which of my reports are stuck in exception review?
        
        Args:
            limit: Maximum number of reports to return (default: 50)
            user: User filter - 'ALL' for all users, or specific user ID (default: 'ALL')
            
        Returns:
            Dictionary containing reports in exception review and metadata
        """
        from datetime import datetime
        
        # Use v3.0 expense reports endpoint with A_AAFH filter
        endpoint = "api/v3.0/expense/reports"
        
        params = {
            'approvalStatusCode': 'A_AAFH',  # A_AAFH = Approval - At Audit/Finance Handler (exception review)
            'limit': limit,
            'user': user
        }
        
        try:
            response = self._make_request("GET", endpoint, params=params)
            data = response.json()
            
            # v3 API returns Items array
            items = data.get('Items', [])
            
            reports = []
            for item in items:
                # Get exception information if available
                has_exception = item.get('HasException', False)
                exception_code = item.get('ExceptionCode', '')
                last_comment = item.get('LastComment', '')
                
                # Calculate days since submission
                submit_date_str = item.get('SubmitDate', '')
                days_in_exception = None
                if submit_date_str:
                    try:
                        submit_date = datetime.fromisoformat(submit_date_str.replace('Z', '+00:00'))
                        days_in_exception = (datetime.now() - submit_date.replace(tzinfo=None)).days
                    except:
                        pass
                
                report = ExpenseReport(
                    id=item.get('ID'),
                    name=item.get('Name'),
                    purpose=item.get('Purpose'),
                    business_purpose=item.get('BusinessPurpose'),
                    total=item.get('Total'),
                    currency_code=item.get('CurrencyCode'),
                    submission_date=submit_date_str,
                    approval_status=item.get('ApprovalStatusName'),
                    workflow_step=item.get('WorkflowStepName'),
                    owner_name=item.get('OwnerName'),
                    created_date=item.get('CreateDate'),
                    last_modified_date=item.get('LastModifiedDate'),
                    country=item.get('Country'),
                    policy_id=item.get('PolicyID')
                )
                
                report_dict = asdict(report)
                report_dict['has_exception'] = has_exception
                report_dict['exception_code'] = exception_code
                report_dict['last_comment'] = last_comment
                report_dict['days_in_exception'] = days_in_exception
                reports.append(report_dict)
            
            return {
                'success': True,
                'reports': reports,
                'count': len(reports),
                'approval_status': 'A_AAFH',
                'message': f'Retrieved {len(reports)} reports in exception review'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to retrieve reports in exception review: {str(e)}'
            }

    def get_reports_being_processed_for_payment(self, limit: int = 50, user: str = 'ALL') -> Dict[str, Any]:
        """
        Get expense reports that are currently being processed for payment.
        
        CSV Row #5: What reports are currently being processed for payment?
        
        Args:
            limit: Maximum number of reports to return (default: 50)
            user: User filter - 'ALL' for all users, or specific user ID
            
        Returns:
            Dictionary containing reports being processed for payment and metadata
        """
        from datetime import datetime
        
        # Use v3.0 expense reports endpoint with P_PROC filter
        endpoint = "api/v3.0/expense/reports"
        
        params = {
            'paymentStatusCode': 'P_PROC',  # P_PROC = Payment Processing
            'limit': limit,
            'user': user
        }
        
        try:
            response = self._make_request("GET", endpoint, params=params)
            data = response.json()
            
            # v3 API returns Items array
            items = data.get('Items', [])
            
            reports = []
            for item in items:
                # Get payment status details
                payment_status_name = item.get('PaymentStatusName', '')
                payment_status_code = item.get('PaymentStatusCode', '')
                
                # Calculate days since approval (if approved)
                approval_date_str = item.get('ApprovedDate', '') or item.get('SubmitDate', '')
                days_since_approval = None
                if approval_date_str:
                    try:
                        approval_date = datetime.fromisoformat(approval_date_str.replace('Z', '+00:00'))
                        days_since_approval = (datetime.now() - approval_date.replace(tzinfo=None)).days
                    except:
                        pass
                
                report = ExpenseReport(
                    id=item.get('ID'),
                    name=item.get('Name'),
                    purpose=item.get('Purpose'),
                    business_purpose=item.get('BusinessPurpose'),
                    total=item.get('Total'),
                    currency_code=item.get('CurrencyCode'),
                    submission_date=item.get('SubmitDate'),
                    approval_status=item.get('ApprovalStatusName'),
                    workflow_step=item.get('WorkflowStepName'),
                    owner_name=item.get('OwnerName'),
                    created_date=item.get('CreateDate'),
                    last_modified_date=item.get('LastModifiedDate'),
                    country=item.get('Country'),
                    policy_id=item.get('PolicyID')
                )
                
                report_dict = asdict(report)
                report_dict['payment_status_name'] = payment_status_name
                report_dict['payment_status_code'] = payment_status_code
                report_dict['days_since_approval'] = days_since_approval
                report_dict['approval_date'] = approval_date_str
                reports.append(report_dict)
            
            return {
                'success': True,
                'reports': reports,
                'count': len(reports),
                'payment_status_code': 'P_PROC',
                'message': f'Retrieved {len(reports)} reports being processed for payment'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to retrieve reports being processed for payment: {str(e)}'
            }

    def get_reports_waiting_for_finance_review(self, limit: int = 50, user: str = 'ALL') -> Dict[str, Any]:
        """
        Get expense reports that are approved and being processed for payment (waiting for finance review).
        
        CSV Row #13: What reports are waiting for finance review?
        
        In this Concur configuration, approved reports automatically move to "Processing Payment" (P_PROC)
        status, which represents reports waiting for finance review and payment processing.
        
        Args:
            limit: Maximum number of reports to return (default: 50)
            user: User filter - 'ALL' for all users, or specific user ID
            
        Returns:
            Dictionary containing reports waiting for finance review and metadata
        """
        from datetime import datetime
        
        # Use v3.0 expense reports endpoint with A_APPR and P_PROC filters
        endpoint = "api/v3.0/expense/reports"
        
        params = {
            'approvalStatusCode': 'A_APPR',  # A_APPR = Approved
            'paymentStatusCode': 'P_PROC',   # P_PROC = Processing Payment (finance review)
            'limit': limit,
            'user': user
        }
        
        try:
            response = self._make_request("GET", endpoint, params=params)
            data = response.json()
            
            # v3 API returns Items array
            items = data.get('Items', [])
            
            reports = []
            for item in items:
                # Get payment and approval status details
                payment_status_name = item.get('PaymentStatusName', '')
                payment_status_code = item.get('PaymentStatusCode', '')
                approval_status_name = item.get('ApprovalStatusName', '')
                approval_status_code = item.get('ApprovalStatusCode', '')
                
                # Calculate days since approval
                approval_date_str = item.get('ApprovedDate', '')
                days_since_approval = None
                if approval_date_str:
                    try:
                        approval_date = datetime.fromisoformat(approval_date_str.replace('Z', '+00:00'))
                        days_since_approval = (datetime.now() - approval_date.replace(tzinfo=None)).days
                    except:
                        pass
                
                report = ExpenseReport(
                    id=item.get('ID'),
                    name=item.get('Name'),
                    purpose=item.get('Purpose'),
                    business_purpose=item.get('BusinessPurpose'),
                    total=item.get('Total'),
                    currency_code=item.get('CurrencyCode'),
                    submission_date=item.get('SubmitDate'),
                    approval_status=approval_status_name,
                    workflow_step=item.get('WorkflowStepName'),
                    owner_name=item.get('OwnerName'),
                    created_date=item.get('CreateDate'),
                    last_modified_date=item.get('LastModifiedDate'),
                    country=item.get('Country'),
                    policy_id=item.get('PolicyID')
                )
                
                report_dict = asdict(report)
                report_dict['payment_status_name'] = payment_status_name
                report_dict['payment_status_code'] = payment_status_code
                report_dict['approval_status_code'] = approval_status_code
                report_dict['days_since_approval'] = days_since_approval
                report_dict['approval_date'] = approval_date_str
                reports.append(report_dict)
            
            return {
                'success': True,
                'reports': reports,
                'count': len(reports),
                'approval_status_code': 'A_APPR',
                'payment_status_code': 'P_PROC',
                'message': f'Retrieved {len(reports)} reports waiting for finance review'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to retrieve reports waiting for finance review: {str(e)}'
            }

    def get_reports_pending_processor_approval(self, limit: int = 50, user: str = 'ALL') -> Dict[str, Any]:
        """
        Get expense reports that are approved and pending processor approval (not yet being processed for payment).
        
        CSV Row #27: Which reports are pending processor approval?
        
        These are reports that have been approved by managers but are waiting for the processor
        to review and begin processing for payment. They have status A_APPR (Approved) and 
        P_NOTP (Not Paid), meaning they haven't been extracted/processed yet.
        
        Args:
            limit: Maximum number of reports to return (default: 50)
            user: User filter - 'ALL' for all users, or specific user ID
            
        Returns:
            Dictionary containing reports pending processor approval and metadata
        """
        from datetime import datetime
        
        # Use v3.0 expense reports endpoint with A_APPR and P_NOTP filters
        endpoint = "api/v3.0/expense/reports"
        
        params = {
            'approvalStatusCode': 'A_APPR',  # A_APPR = Approved
            'paymentStatusCode': 'P_NOTP',   # P_NOTP = Not Paid (pending processor)
            'limit': limit,
            'user': user
        }
        
        try:
            response = self._make_request("GET", endpoint, params=params)
            data = response.json()
            
            # v3 API returns Items array
            items = data.get('Items', [])
            
            reports = []
            for item in items:
                # Get payment and approval status details
                payment_status_name = item.get('PaymentStatusName', '')
                payment_status_code = item.get('PaymentStatusCode', '')
                approval_status_name = item.get('ApprovalStatusName', '')
                approval_status_code = item.get('ApprovalStatusCode', '')
                
                # Calculate days since approval (how long waiting for processor)
                approval_date_str = item.get('ApprovedDate', '')
                days_since_approval = None
                if approval_date_str:
                    try:
                        approval_date = datetime.fromisoformat(approval_date_str.replace('Z', '+00:00'))
                        days_since_approval = (datetime.now() - approval_date.replace(tzinfo=None)).days
                    except:
                        pass
                
                report = ExpenseReport(
                    id=item.get('ID'),
                    name=item.get('Name'),
                    purpose=item.get('Purpose'),
                    business_purpose=item.get('BusinessPurpose'),
                    total=item.get('Total'),
                    currency_code=item.get('CurrencyCode'),
                    submission_date=item.get('SubmitDate'),
                    approval_status=approval_status_name,
                    workflow_step=item.get('WorkflowStepName'),
                    owner_name=item.get('OwnerName'),
                    created_date=item.get('CreateDate'),
                    last_modified_date=item.get('LastModifiedDate'),
                    country=item.get('Country'),
                    policy_id=item.get('PolicyID')
                )
                
                report_dict = asdict(report)
                report_dict['payment_status_name'] = payment_status_name
                report_dict['payment_status_code'] = payment_status_code
                report_dict['approval_status_code'] = approval_status_code
                report_dict['days_since_approval'] = days_since_approval
                report_dict['approval_date'] = approval_date_str
                reports.append(report_dict)
            
            return {
                'success': True,
                'reports': reports,
                'count': len(reports),
                'approval_status_code': 'A_APPR',
                'payment_status_code': 'P_NOTP',
                'message': f'Retrieved {len(reports)} reports pending processor approval'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to retrieve reports pending processor approval: {str(e)}'
            }

    def get_reports_eligible_for_early_payment(self, limit: int = 50, user: str = 'ALL', days_since_approval: int = 5) -> Dict[str, Any]:
        """
        Get expense reports that are eligible for early payment.
        Reports must be approved, not yet paid, and approved at least N days ago.
        
        CSV Row #19: Which reports are eligible for early payment?
        
        Args:
            limit: Maximum number of reports to return (default: 50)
            user: User filter - 'ALL' for all users, or specific user ID
            days_since_approval: Minimum days since approval (default: 5)
            
        Returns:
            Dictionary containing eligible reports and metadata
        """
        from datetime import datetime, timedelta
        
        # Calculate the date N days ago
        threshold_date = datetime.now() - timedelta(days=days_since_approval)
        threshold_date_str = threshold_date.strftime('%Y-%m-%d')
        
        # Use v3.0 expense reports endpoint with A_APPR, P_NOTP, and approvedDateBefore filters
        endpoint = "api/v3.0/expense/reports"
        
        params = {
            'approvalStatusCode': 'A_APPR',  # A_APPR = Approved
            'paymentStatusCode': 'P_NOTP',   # P_NOTP = Not Paid
            'approvedDateBefore': threshold_date_str,  # Approved at least N days ago
            'limit': limit,
            'user': user
        }
        
        try:
            response = self._make_request("GET", endpoint, params=params)
            data = response.json()
            
            # v3 API returns Items array
            items = data.get('Items', [])
            
            reports = []
            for item in items:
                # Get payment and approval status details
                payment_status_name = item.get('PaymentStatusName', '')
                payment_status_code = item.get('PaymentStatusCode', '')
                approval_status_name = item.get('ApprovalStatusName', '')
                approval_status_code = item.get('ApprovalStatusCode', '')
                
                # Calculate days since approval
                approval_date_str = item.get('ApprovedDate', '')
                days_since_approval_calc = None
                if approval_date_str:
                    try:
                        approval_date = datetime.fromisoformat(approval_date_str.replace('Z', '+00:00'))
                        days_since_approval_calc = (datetime.now() - approval_date.replace(tzinfo=None)).days
                    except:
                        pass
                
                report = ExpenseReport(
                    id=item.get('ID'),
                    name=item.get('Name'),
                    purpose=item.get('Purpose'),
                    business_purpose=item.get('BusinessPurpose'),
                    total=item.get('Total'),
                    currency_code=item.get('CurrencyCode'),
                    submission_date=item.get('SubmitDate'),
                    approval_status=approval_status_name,
                    workflow_step=item.get('WorkflowStepName'),
                    owner_name=item.get('OwnerName'),
                    created_date=item.get('CreateDate'),
                    last_modified_date=item.get('LastModifiedDate'),
                    country=item.get('Country'),
                    policy_id=item.get('PolicyID')
                )
                
                report_dict = asdict(report)
                report_dict['payment_status_name'] = payment_status_name
                report_dict['payment_status_code'] = payment_status_code
                report_dict['approval_status_code'] = approval_status_code
                report_dict['days_since_approval'] = days_since_approval_calc
                report_dict['approval_date'] = approval_date_str
                reports.append(report_dict)
            
            return {
                'success': True,
                'reports': reports,
                'count': len(reports),
                'approval_status_code': 'A_APPR',
                'payment_status_code': 'P_NOTP',
                'threshold_date': threshold_date_str,
                'days_threshold': days_since_approval,
                'message': f'Retrieved {len(reports)} reports eligible for early payment (approved {days_since_approval}+ days ago)'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to retrieve reports eligible for early payment: {str(e)}'
            }

    def get_reports_with_missing_manager_approval(self, limit: int = 50, user: str = 'ALL') -> Dict[str, Any]:
        """
        Get expense reports that are pending approval but have no manager assigned.
        
        CSV Row #20: Show me expense reports with missing manager approval
        
        This retrieves reports that are in pending approval status (A_PEND) but don't have
        an approver assigned to them, which could indicate a workflow configuration issue
        or missing manager assignment.
        
        Args:
            limit: Maximum number of reports to return (default: 50)
            user: User filter - 'ALL' for all users, or specific user ID
            
        Returns:
            Dictionary containing reports with missing manager approval and metadata
        """
        from datetime import datetime
        
        # Use v3.0 expense reports endpoint with A_PEND filter
        endpoint = "api/v3.0/expense/reports"
        
        params = {
            'approvalStatusCode': 'A_PEND',  # A_PEND = Pending Approval
            'limit': limit,
            'user': user
        }
        
        try:
            response = self._make_request("GET", endpoint, params=params)
            data = response.json()
            
            # v3 API returns Items array
            items = data.get('Items', [])
            
            reports = []
            for item in items:
                # Check if approver name is missing/null
                approver_name = item.get('ApproverName', '')
                approver_login_id = item.get('ApproverLoginID', '')
                
                # Only include reports where approver is not assigned
                if not approver_name or approver_name.strip() == '':
                    # Get approval status details
                    approval_status_name = item.get('ApprovalStatusName', '')
                    approval_status_code = item.get('ApprovalStatusCode', '')
                    
                    # Calculate days since submission
                    submit_date_str = item.get('SubmitDate', '')
                    days_since_submission = None
                    if submit_date_str:
                        try:
                            submit_date = datetime.fromisoformat(submit_date_str.replace('Z', '+00:00'))
                            days_since_submission = (datetime.now() - submit_date.replace(tzinfo=None)).days
                        except:
                            pass
                    
                    report = ExpenseReport(
                        id=item.get('ID'),
                        name=item.get('Name'),
                        purpose=item.get('Purpose'),
                        business_purpose=item.get('BusinessPurpose'),
                        total=item.get('Total'),
                        currency_code=item.get('CurrencyCode'),
                        submission_date=submit_date_str,
                        approval_status=approval_status_name,
                        workflow_step=item.get('WorkflowStepName'),
                        owner_name=item.get('OwnerName'),
                        created_date=item.get('CreateDate'),
                        last_modified_date=item.get('LastModifiedDate'),
                        country=item.get('Country'),
                        policy_id=item.get('PolicyID')
                    )
                    
                    report_dict = asdict(report)
                    report_dict['approval_status_code'] = approval_status_code
                    report_dict['days_since_submission'] = days_since_submission
                    report_dict['approver_name'] = approver_name
                    report_dict['approver_login_id'] = approver_login_id
                    report_dict['owner_login_id'] = item.get('OwnerLoginID', '')
                    reports.append(report_dict)
            
            return {
                'success': True,
                'reports': reports,
                'count': len(reports),
                'approval_status_code': 'A_PEND',
                'message': f'Retrieved {len(reports)} reports with missing manager approval'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to retrieve reports with missing manager approval: {str(e)}'
            }

    def get_reports_needing_receipts(self, limit: int = 50, user: str = 'ALL') -> Dict[str, Any]:
        """
        Get expense reports that need receipts attached before approval.
        
        CSV Row #35: Which reports need receipts attached before approval?
        
        This retrieves reports that are in pending approval status (A_PEND) but don't have
        receipts/images attached. These reports are blocked from approval until proper
        documentation is provided.
        
        Note: The Concur API may not provide explicit hasImages or requiresReceipts fields
        in all API versions. This method will filter on A_PEND status and check available
        receipt-related fields.
        
        Args:
            limit: Maximum number of reports to return (default: 50)
            user: User filter - 'ALL' for all users, or specific user ID
            
        Returns:
            Dictionary containing reports needing receipts and metadata
        """
        from datetime import datetime
        
        # Use v3.0 expense reports endpoint with A_PEND filter
        endpoint = "api/v3.0/expense/reports"
        
        params = {
            'approvalStatusCode': 'A_PEND',  # A_PEND = Pending Approval
            'limit': limit,
            'user': user
        }
        
        try:
            response = self._make_request("GET", endpoint, params=params)
            data = response.json()
            
            # v3 API returns Items array
            items = data.get('Items', [])
            
            reports = []
            for item in items:
                # Check for receipt-related fields
                # Note: Not all API versions return HasImages or ReceiptStatus
                has_images = item.get('HasImages', None)
                receipt_status = item.get('ReceiptStatus', None)
                
                # Get approval status details
                approval_status_name = item.get('ApprovalStatusName', '')
                approval_status_code = item.get('ApprovalStatusCode', '')
                
                # Calculate days since submission
                submit_date_str = item.get('SubmitDate', '')
                days_since_submission = None
                if submit_date_str:
                    try:
                        submit_date = datetime.fromisoformat(submit_date_str.replace('Z', '+00:00'))
                        days_since_submission = (datetime.now() - submit_date.replace(tzinfo=None)).days
                    except:
                        pass
                
                report = ExpenseReport(
                    id=item.get('ID'),
                    name=item.get('Name'),
                    purpose=item.get('Purpose'),
                    business_purpose=item.get('BusinessPurpose'),
                    total=item.get('Total'),
                    currency_code=item.get('CurrencyCode'),
                    submission_date=submit_date_str,
                    approval_status=approval_status_name,
                    workflow_step=item.get('WorkflowStepName'),
                    owner_name=item.get('OwnerName'),
                    created_date=item.get('CreateDate'),
                    last_modified_date=item.get('LastModifiedDate'),
                    country=item.get('Country'),
                    policy_id=item.get('PolicyID')
                )
                
                report_dict = asdict(report)
                report_dict['approval_status_code'] = approval_status_code
                report_dict['days_since_submission'] = days_since_submission
                report_dict['has_images'] = has_images
                report_dict['receipt_status'] = receipt_status
                report_dict['owner_login_id'] = item.get('OwnerLoginID', '')
                reports.append(report_dict)
            
            return {
                'success': True,
                'reports': reports,
                'count': len(reports),
                'approval_status_code': 'A_PEND',
                'message': f'Retrieved {len(reports)} pending reports (check has_images field for receipt status)'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to retrieve reports needing receipts: {str(e)}'
            }

    def get_audited_reports(self, limit: int = 50, user: str = 'ALL', custom_field: Optional[str] = None) -> Dict[str, Any]:
        """
        Get expense reports that have been audited by finance.
        
        CSV Row #37: What reports have been audited by finance?
        
        This retrieves reports that have been marked as audited. The Concur API may use
        either a standard AuditStatus field or a custom audit field depending on the
        company's configuration.
        
        Args:
            limit: Maximum number of reports to return (default: 50)
            user: User filter - 'ALL' for all users, 'me' for current user, or specific user ID
            custom_field: Optional custom field name for audit status (e.g., 'Custom15')
            
        Returns:
            Dictionary containing audited reports and metadata
        """
        from datetime import datetime
        
        # Use v3.0 expense reports endpoint
        endpoint = "api/v3.0/expense/reports"
        
        # Base parameters
        params = {
            'limit': limit,
            'user': user
        }
        
        # Note: The Concur v3.0 API does not directly support filtering by auditStatus
        # We'll retrieve reports and filter them in the response
        
        try:
            response = self._make_request("GET", endpoint, params=params)
            data = response.json()
            
            # v3 API returns Items array
            items = data.get('Items', [])
            
            reports = []
            for item in items:
                # Check for audit status in various possible fields
                # The field name may vary depending on company configuration
                audit_status = item.get('AuditStatus', '')
                audit_date = item.get('AuditDate', '')
                audited_by = item.get('AuditedBy', '')
                
                # Check custom field if specified
                custom_audit_value = None
                if custom_field:
                    custom_audit_value = item.get(custom_field, '')
                
                # Determine if report has been audited
                # Look for "AUDITED" status or similar indicators
                is_audited = False
                audit_indicator = ''
                
                if audit_status and 'AUDITED' in audit_status.upper():
                    is_audited = True
                    audit_indicator = f'AuditStatus={audit_status}'
                elif custom_audit_value and 'AUDITED' in str(custom_audit_value).upper():
                    is_audited = True
                    audit_indicator = f'{custom_field}={custom_audit_value}'
                elif audit_date:
                    # If there's an audit date, consider it audited
                    is_audited = True
                    audit_indicator = f'AuditDate={audit_date}'
                
                # Only include audited reports
                if is_audited:
                    # Get approval and payment status details
                    approval_status_name = item.get('ApprovalStatusName', '')
                    approval_status_code = item.get('ApprovalStatusCode', '')
                    payment_status_name = item.get('PaymentStatusName', '')
                    payment_status_code = item.get('PaymentStatusCode', '')
                    
                    # Calculate days since audit
                    days_since_audit = None
                    if audit_date:
                        try:
                            audit_dt = datetime.fromisoformat(audit_date.replace('Z', '+00:00'))
                            days_since_audit = (datetime.now() - audit_dt.replace(tzinfo=None)).days
                        except:
                            pass
                    
                    report = ExpenseReport(
                        id=item.get('ID'),
                        name=item.get('Name'),
                        purpose=item.get('Purpose'),
                        business_purpose=item.get('BusinessPurpose'),
                        total=item.get('Total'),
                        currency_code=item.get('CurrencyCode'),
                        submission_date=item.get('SubmitDate'),
                        approval_status=approval_status_name,
                        workflow_step=item.get('WorkflowStepName'),
                        owner_name=item.get('OwnerName'),
                        created_date=item.get('CreateDate'),
                        last_modified_date=item.get('LastModifiedDate'),
                        country=item.get('Country'),
                        policy_id=item.get('PolicyID')
                    )
                    
                    report_dict = asdict(report)
                    report_dict['approval_status_code'] = approval_status_code
                    report_dict['payment_status_name'] = payment_status_name
                    report_dict['payment_status_code'] = payment_status_code
                    report_dict['audit_status'] = audit_status
                    report_dict['audit_date'] = audit_date
                    report_dict['audited_by'] = audited_by
                    report_dict['audit_indicator'] = audit_indicator
                    report_dict['days_since_audit'] = days_since_audit
                    report_dict['owner_login_id'] = item.get('OwnerLoginID', '')
                    reports.append(report_dict)
            
            return {
                'success': True,
                'reports': reports,
                'count': len(reports),
                'total_retrieved': len(items),
                'message': f'Retrieved {len(reports)} audited reports out of {len(items)} total reports'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to retrieve audited reports: {str(e)}'
            }

    def get_reports_paid_via_ach_last_month(self, limit: int = 50, user: str = 'ALL') -> Dict[str, Any]:
        """
        Get expense reports that were paid via ACH in the last month.
        
        CSV Row #15: Which reports were paid via ACH last month?
        
        Args:
            limit: Maximum number of reports to return (default: 50)
            user: User filter - 'ALL' for all users, or specific user ID
            
        Returns:
            Dictionary containing ACH-paid reports and metadata
        """
        from datetime import datetime, timedelta
        
        # Calculate last month's date (30 days ago)
        last_month = datetime.now() - timedelta(days=30)
        last_month_str = last_month.strftime('%Y-%m-%d')
        
        # Use v3.0 expense reports endpoint with P_PAID, paidDateAfter, and paymentType filters
        endpoint = "api/v3.0/expense/reports"
        
        params = {
            'paymentStatusCode': 'P_PAID',  # P_PAID = Paid
            'paidDateAfter': last_month_str,
            'limit': limit,
            'user': user
        }
        
        try:
            response = self._make_request("GET", endpoint, params=params)
            data = response.json()
            
            # v3 API returns Items array
            items = data.get('Items', [])
            
            reports = []
            ach_reports = []
            non_ach_payment_types = set()
            
            for item in items:
                # Get payment type information
                payment_type = None
                payment_type_name = None
                
                # Try multiple ways to get payment type
                if 'PaymentType' in item and item['PaymentType']:
                    if isinstance(item['PaymentType'], dict):
                        payment_type_name = item['PaymentType'].get('Name', '')
                        payment_type = item['PaymentType'].get('Code', '')
                    else:
                        payment_type_name = str(item['PaymentType'])
                
                if not payment_type_name and 'PaymentTypeName' in item:
                    payment_type_name = item.get('PaymentTypeName', '')
                
                # Get payment status details
                payment_status_name = item.get('PaymentStatusName', '')
                payment_status_code = item.get('PaymentStatusCode', '')
                paid_date = item.get('PaidDate', '')
                
                # Calculate days since paid
                days_since_paid = None
                if paid_date:
                    try:
                        paid_datetime = datetime.fromisoformat(paid_date.replace('Z', '+00:00'))
                        days_since_paid = (datetime.now() - paid_datetime.replace(tzinfo=None)).days
                    except:
                        pass
                
                report = ExpenseReport(
                    id=item.get('ID'),
                    name=item.get('Name'),
                    purpose=item.get('Purpose'),
                    business_purpose=item.get('BusinessPurpose'),
                    total=item.get('Total'),
                    currency_code=item.get('CurrencyCode'),
                    submission_date=item.get('SubmitDate'),
                    approval_status=item.get('ApprovalStatusName'),
                    workflow_step=item.get('WorkflowStepName'),
                    owner_name=item.get('OwnerName'),
                    created_date=item.get('CreateDate'),
                    last_modified_date=item.get('LastModifiedDate'),
                    country=item.get('Country'),
                    policy_id=item.get('PolicyID')
                )
                
                report_dict = asdict(report)
                report_dict['payment_status_name'] = payment_status_name
                report_dict['payment_status_code'] = payment_status_code
                report_dict['paid_date'] = paid_date
                report_dict['days_since_paid'] = days_since_paid
                report_dict['payment_type'] = payment_type
                report_dict['payment_type_name'] = payment_type_name
                
                # Filter for ACH payment type (case-insensitive)
                if payment_type_name and 'ach' in payment_type_name.lower():
                    ach_reports.append(report_dict)
                else:
                    # Track non-ACH payment types for informational purposes
                    if payment_type_name:
                        non_ach_payment_types.add(payment_type_name)
                
                # Include all paid reports in the general list
                reports.append(report_dict)
            
            return {
                'success': True,
                'reports': ach_reports,  # Only ACH reports
                'all_paid_reports': reports,  # All paid reports for reference
                'count': len(ach_reports),
                'total_paid_reports': len(reports),
                'payment_status_code': 'P_PAID',
                'payment_type_filter': 'ACH',
                'date_filter': f'Paid after {last_month_str}',
                'non_ach_payment_types': list(non_ach_payment_types),
                'message': f'Retrieved {len(ach_reports)} ACH-paid reports out of {len(reports)} total paid reports'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to retrieve ACH-paid reports: {str(e)}'
            }

    def get_expense_reports(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get expense reports with custom parameters using v3.0 API.
        This is a generic method that accepts any valid v3.0 API parameters.
        
        CSV Row #8: Show me all reports pending manager approval for a specific employee
        
        Args:
            params: Dictionary of query parameters (e.g., {'user': 'loginID', 'approvalStatusCode': 'A_PEND'})
                Common parameters:
                - user: User login ID or 'ALL' for all users
                - approvalStatusCode: Filter by approval status code (A_PEND, A_APPR, A_RESU, etc.)
                - paymentStatusCode: Filter by payment status code (P_PROC, P_PAID, etc.)
                - submitDateBefore: Filter by submit date before (YYYY-MM-DD)
                - submitDateAfter: Filter by submit date after (YYYY-MM-DD)
                - limit: Maximum number of reports to return
                
        Returns:
            Dictionary containing expense reports and metadata
        """
        from datetime import datetime
        
        endpoint = "api/v3.0/expense/reports"
        
        # Use provided params or empty dict
        query_params = params or {}
        
        try:
            response = self._make_request("GET", endpoint, params=query_params)
            data = response.json()
            
            # v3 API returns Items array
            items = data.get('Items', [])
            
            reports = []
            for item in items:
                report = ExpenseReport(
                    id=item.get('ID'),
                    name=item.get('ReportName') or item.get('Name'),
                    purpose=item.get('Purpose'),
                    business_purpose=item.get('BusinessPurpose'),
                    total=item.get('Total'),
                    currency_code=item.get('CurrencyCode'),
                    submission_date=item.get('SubmitDate'),
                    approval_status=item.get('ApprovalStatusName'),
                    workflow_step=item.get('WorkflowStepName'),
                    owner_name=item.get('OwnerName'),
                    created_date=item.get('CreateDate'),
                    last_modified_date=item.get('LastModifiedDate'),
                    country=item.get('Country'),
                    policy_id=item.get('PolicyID')
                )
                
                # Convert to dict and add v3 specific fields
                report_dict = asdict(report)
                report_dict.update({
                    'ReportName': item.get('ReportName') or item.get('Name'),
                    'ID': item.get('ID'),
                    'OwnerName': item.get('OwnerName'),
                    'Total': item.get('Total'),
                    'CurrencyCode': item.get('CurrencyCode'),
                    'SubmitDate': item.get('SubmitDate'),
                    'ApprovalStatusName': item.get('ApprovalStatusName'),
                    'ApprovalStatusCode': item.get('ApprovalStatusCode'),
                    'PaymentStatusName': item.get('PaymentStatusName'),
                    'PaymentStatusCode': item.get('PaymentStatusCode'),
                    'HasException': item.get('HasException'),
                    'PolicyID': item.get('PolicyID'),
                    'PolicyName': item.get('PolicyName'),
                    'ApprovedDate': item.get('ApprovedDate'),
                    'approved_date': item.get('ApprovedDate')  # Add both camelCase and snake_case
                })
                reports.append(report_dict)
            
            return {
                'success': True,
                'reports': reports,
                'count': len(reports),
                'params': query_params,
                'message': f'Retrieved {len(reports)} expense reports'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to retrieve expense reports: {str(e)}'
            }


    def get_approved_not_extracted_reports(self, limit: int = 50, user: str = 'ALL') -> Dict[str, Any]:
        """
        Get reports that were approved but not yet extracted to external systems.
        
        CSV Row #10: Can I see reports that were approved but not yet extracted?
        
        This retrieves reports with:
        - approvalStatusCode = A_APPR (Approved)
        - hasException = N (No exceptions)
        - extractedDate = null (Not yet extracted)
        
        Args:
            limit: Maximum number of reports to return (default: 50)
            user: User login ID or 'ALL' for all users (default: 'ALL')
            
        Returns:
            Dictionary containing:
            - success: Boolean indicating success/failure
            - reports: List of approved but not extracted reports
            - count: Number of reports found
            - message: Status message
        """
        params = {
            'approvalStatusCode': 'A_APPR',
            'hasException': 'N',
            'limit': limit
        }
        
        if user and user != 'ALL':
            params['user'] = user
        
        try:
            result = self.get_expense_reports(params)
            
            if result['success']:
                # Filter reports where extractedDate is null or not present
                # Note: The API might not return extractedDate field if null,
                # so we consider both missing field and null value
                filtered_reports = []
                for report in result['reports']:
                    extracted_date = report.get('ExtractedDate')
                    if not extracted_date or extracted_date == 'null':
                        filtered_reports.append(report)
                
                return {
                    'success': True,
                    'reports': filtered_reports,
                    'count': len(filtered_reports),
                    'params': params,
                    'message': f'Retrieved {len(filtered_reports)} approved reports not yet extracted'
                }
            else:
                return result
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to retrieve approved not extracted reports: {str(e)}'
            }


    def create_report(self, name: str, purpose: str = "", business_purpose: str = "", 
                     currency_code: str = "USD", country: str = "US") -> Dict[str, Any]:
        """
        Create a new expense report.
        
        Args:
            name: Report name
            purpose: Report purpose
            business_purpose: Business purpose
            currency_code: Currency code (default: USD)
            country: Country code (default: US)
            
        Returns:
            Dictionary containing created report details
        """
        # Get user ID for v4 endpoint
        user_id = self.get_user_id()
        if not user_id:
            raise AuthenticationError("Could not determine user ID")
        
        # Get user's default policy (required for v4 API)
        policies_endpoint = f"expenseconfig/v4/users/{user_id}/context/TRAVELER/policies"
        policies_response = self._make_request("GET", policies_endpoint)
        policies = policies_response.json()
        
        default_policy_id = None
        for policy in policies:
            if policy.get('isDefault', False):
                default_policy_id = policy.get('policyId') or policy.get('id')
                break
        
        if not default_policy_id and policies:
            # Use first available policy if no default found
            default_policy_id = policies[0].get('policyId') or policies[0].get('id')
        
        if not default_policy_id:
            raise ValidationError("No expense policies found for user")
        
        # Use v4 payload format with required policyId
        v4_payload = {
            "name": name,
            "reportDate": datetime.now().strftime('%Y-%m-%d'),
            "businessPurpose": business_purpose or purpose,
            "policyId": default_policy_id
        }
        
        # Use v4 endpoint
        endpoint = f"expensereports/v4/users/{user_id}/context/TRAVELER/reports"
        response = self._make_request("POST", endpoint, json=v4_payload)
        data = response.json()
        
        # Extract report ID from URI
        report_id = None
        if 'uri' in data:
            report_id = data['uri'].split('/')[-1]
        
        return {
            'success': True,
            'report_id': report_id,
            'uri': data.get('uri'),
            'ID': report_id,  # For compatibility
            'message': f"Successfully created report: {name}",
            'policy_id': default_policy_id
        }


    def delete_report(self, report_id: str) -> Dict[str, Any]:
        """
        Delete an expense report using v4 endpoint (like notebook).
        
        Args:
            report_id: The ID of the report to delete
            
        Returns:
            Dictionary indicating success/failure
        """
        # Get user ID for v4 endpoint
        user_id = self.get_user_id()
        if not user_id:
            raise AuthenticationError("Could not determine user ID")
        
        # Use v4 endpoint like the notebook
        endpoint = f"expensereports/v4/users/{user_id}/context/TRAVELER/reports/{report_id}"
        response = self._make_request("DELETE", endpoint)
        
        return {
            'success': True,
            'message': f"Successfully deleted report {report_id}",
            'api_version': 'v4'
        }

    # EXPENSE ENTRY METHODS
    
    def list_expenses(self, report_id: str, limit: int = 25, offset: int = 0, context: str = "TRAVELER") -> Dict[str, Any]:
        """
        List expense entries for a specific report using v4 endpoint.
        
        Args:
            report_id: The ID of the report
            limit: Maximum number of expenses to return (1-100)
            offset: Number of records to skip
            context: Context to use (TRAVELER, MANAGER, etc.). Default: TRAVELER
            
        Returns:
            Dictionary containing expenses and metadata
        """
        # Try v4 endpoint first with specified context
        user_id = self.get_user_id()
        if not user_id:
            raise AuthenticationError("Could not determine user ID")
        
        # Try v4 endpoint with specified context
        endpoint = f"expensereports/v4/users/{user_id}/context/{context}/reports/{report_id}/expenses"
        try:
            response = self._make_request("GET", endpoint)
            data = response.json()
        except Exception as v4_error:
            # If v4 fails, try v3 endpoint which may be more permissive
            logger.info(f"V4 endpoint failed, trying V3: {str(v4_error)}")
            endpoint = f"api/v3.0/expense/reportdetails/{report_id}"
            response = self._make_request("GET", endpoint)
            data = response.json()
            # V3 returns data differently - extract entries
            if 'Entries' in data:
                data = data['Entries']
            elif 'Items' in data:
                data = data['Items']
        
        expenses = []
        # Handle both v4 (array) and legacy formats
        items = data if isinstance(data, list) else data.get('Items', [])
        
        for item in items:
            # Try v4 format first, fall back to v3 format
            expense = ExpenseEntry(
                id=item.get('expenseId') or item.get('ID'),
                report_id=report_id,
                expense_type=(item.get('expenseType', {}).get('name') if item.get('expenseType') 
                             else item.get('ExpenseTypeName')),
                transaction_amount=(item.get('transactionAmount', {}).get('value') if item.get('transactionAmount') 
                                  else item.get('TransactionAmount')),
                transaction_currency_code=(item.get('transactionAmount', {}).get('currencyCode') if item.get('transactionAmount') 
                                         else item.get('TransactionCurrencyCode')),
                transaction_date=item.get('transactionDate') or item.get('TransactionDate'),
                business_purpose=(
                    item.get('businessPurpose', {}).get('value') if isinstance(item.get('businessPurpose'), dict)
                    else item.get('businessPurpose') or item.get('BusinessPurpose')
                ),
                vendor_description=(item.get('vendor', {}).get('description') if item.get('vendor') 
                                  else item.get('VendorDescription')),
                city_name=(item.get('location', {}).get('city') if item.get('location') 
                          else item.get('LocationName')),
                country_code=(item.get('location', {}).get('countryCode') if item.get('location') 
                            else item.get('CountryCode')),
                payment_type=(item.get('paymentType', {}).get('name') if item.get('paymentType') 
                            else item.get('PaymentTypeName')),
                receipt_required=item.get('receiptRequired') or item.get('ReceiptRequired'),
                has_receipt=item.get('hasReceipt') or item.get('HasReceipt')
            )
            expenses.append(asdict(expense))
        
        return {
            'success': True,
            'expenses': expenses,
            'count': len(expenses),
            'api_version': 'v4',
            'report_id': report_id,
            'message': f'Retrieved {len(expenses)} expenses from report {report_id}'
        }


    def create_expense(self, report_id: str, expense_type: str, amount: float, 
                      currency_code: str = "USD", transaction_date: Optional[str] = None,
                      business_purpose: str = "", vendor_description: str = "",
                      city_name: str = "", country_code: str = "US",
                      payment_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new expense entry in a report using v4 endpoint.
        
        Args:
            report_id: The ID of the report to add the expense to
            expense_type: Type of expense (expense type ID from get_expense_types)
            amount: Transaction amount
            currency_code: Currency code (default: USD)
            transaction_date: Date of transaction in YYYY-MM-DD format (default: today)
            business_purpose: Business purpose of the expense
            vendor_description: Vendor/merchant description
            city_name: City where expense occurred
            country_code: Country code (default: US)
            payment_type: Payment method name (optional)
            
        Returns:
            Dictionary containing created expense details
        """
        if transaction_date is None:
            transaction_date = date.today().strftime("%Y-%m-%d")
        
        # Get user ID for v4 endpoint
        user_id = self.get_user_id()
        if not user_id:
            raise AuthenticationError("Could not determine user ID")
        
        # Get the expense type name for the payload
        expense_type_name = expense_type  # Default to ID
        
        # Try to get the actual name from get_expense_types if possible
        try:
            expense_types_result = self.get_expense_types()
            if expense_types_result['success']:
                for et in expense_types_result['expense_types']:
                    if et['id'] == expense_type:
                        expense_type_name = et['name']
                        break
        except:
            pass  # Use ID as name if lookup fails
        
        # Build v4 payload - try simpler structure based on error analysis
        payload = {
            "expenseSource": "EA",
            "exchangeRate": {
                "value": 1,
                "operation": "MULTIPLY"
            },
            "expenseType": {
                "id": expense_type,
                "name": expense_type_name,
                "isDeleted": False,
                "listItemId": None
            },
            "transactionAmount": {
                "value": amount,
                "currencyCode": currency_code.lower()
            },
            "transactionDate": transaction_date
        }
        
        # Add vendor as object with description field
        if vendor_description and vendor_description.strip():
            payload["vendor"] = {
                "description": vendor_description
            }
        
        # Add business purpose - try as simple string first
        if business_purpose and business_purpose.strip():
            payload["businessPurpose"] = business_purpose
        
        try:
            # Use v4 endpoint like the notebook
            endpoint = f"expensereports/v4/users/{user_id}/context/TRAVELER/reports/{report_id}/expenses"
            response = self._make_request("POST", endpoint, json=payload)
            
            if response.status_code in [200, 201]:
                return {
                    'success': True,
                    'expense_id': None,  # v4 doesn't return ID in response
                    'message': f"Successfully created expense entry for {amount} {currency_code}",
                    'api_version': 'v4',
                    'status_code': response.status_code
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}",
                    'message': f"Failed to create expense entry: HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to create expense entry: {str(e)}"
            }

    def update_expense(self, expense_id: str, report_id: str, amount: Optional[float] = None, 
                      expense_type_id: Optional[str] = None, expense_type_name: Optional[str] = None,
                      date: Optional[str] = None, vendor: Optional[str] = None) -> Dict[str, Any]:
        """
        Update an existing expense entry using v4 endpoint (like notebook).
        
        Args:
            expense_id: The ID of the expense to update
            report_id: The ID of the report containing the expense
            amount: Updated transaction amount
            expense_type_id: Updated expense type ID
            expense_type_name: Updated expense type name
            date: Updated transaction date
            vendor: Updated vendor description
            
        Returns:
            Dictionary indicating success/failure
        """
        # Get user ID for v4 endpoint
        user_id = self.get_user_id()
        if not user_id:
            raise AuthenticationError("Could not determine user ID")
        
        # Build v4 payload like the notebook
        payload = {
            "expenseSource": "EA",
            "exchangeRate": {
                "value": 1,
                "operation": "MULTIPLY"
            }
        }
        
        # Only add fields that are provided (like the notebook)
        if expense_type_id and expense_type_name:
            payload["expenseType"] = {
                "id": expense_type_id,
                "name": expense_type_name,
                "isDeleted": False,
                "listItemId": None
            }
        
        if amount:
            payload["transactionAmount"] = {
                "value": amount,
                "currencyCode": "usd"
            }
        
        if vendor:
            payload["vendor"] = {
                "description": vendor
            }
            
        if date:
            payload["transactionDate"] = date
        
        try:
            # Use v4 endpoint with PATCH like the notebook
            endpoint = f"expensereports/v4/users/{user_id}/context/TRAVELER/reports/{report_id}/expenses/{expense_id}"
            response = self._make_request("PATCH", endpoint, json=payload)
            
            if response.status_code in [200, 201, 204]:  # 204 No Content is success for PATCH
                return {
                    'success': True,
                    'message': f"Successfully updated expense {expense_id}",
                    'api_version': 'v4',
                    'status_code': response.status_code
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}",
                    'message': f"Failed to update expense: HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to update expense: {str(e)}"
            }

    def delete_expense(self, expense_id: str, report_id: str) -> Dict[str, Any]:
        """
        Delete an expense entry using v4 endpoint (like notebook).
        
        Args:
            expense_id: The ID of the expense to delete
            report_id: The ID of the report containing the expense
            
        Returns:
            Dictionary indicating success/failure
        """
        # Get user ID for v4 endpoint
        user_id = self.get_user_id()
        if not user_id:
            raise AuthenticationError("Could not determine user ID")
        
        # Use v4 endpoint like the notebook
        endpoint = f"expensereports/v4/users/{user_id}/context/TRAVELER/reports/{report_id}/expenses/{expense_id}"
        response = self._make_request("DELETE", endpoint)
        
        return {
            'success': True,
            'message': f"Successfully deleted expense {expense_id} from report {report_id}",
            'api_version': 'v4'
        }


    # UTILITY METHODS
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the connection to Concur API.
        
        Returns:
            Dictionary indicating connection status
        """
        try:
            access_token = self._get_access_token()
            return {
                'success': True,
                'message': 'Successfully connected to Concur API',
                'token_length': len(access_token),
                'token_prefix': access_token[:20] + '...' if len(access_token) > 20 else access_token
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to connect to Concur API: {str(e)}'
            }

    def get_user_id(self) -> Optional[str]:
        """Get the current user ID from the profile endpoint."""
        try:
            # Use the profile URL from the JWT token
            access_token = self._get_access_token()
            # Decode JWT to get profile URL
            import json
            import base64
            
            parts = access_token.split('.')
            payload = parts[1]
            # Add padding if needed
            payload += '=' * (4 - len(payload) % 4)
            payload_decoded = json.loads(base64.urlsafe_b64decode(payload))
            
            profile_url = payload_decoded.get('concur.profile')
            if profile_url:
                # Extract user ID from profile URL
                user_id = profile_url.split('/')[-1]
                return user_id
            
            return None
        except Exception as e:
            logger.error(f"Failed to get user ID: {e}")
            return None

    def get_expense_types(self) -> Dict[str, Any]:
        """
        Get available expense types using user-specific v4 endpoint (like notebook).
        
        Returns:
            Dictionary containing expense types for the specific user
        """
        try:
            # Get user ID for user-specific endpoint
            user_id = self.get_user_id()
            if not user_id:
                raise AuthenticationError("Could not determine user ID")
            
            # Use user-specific expense types endpoint like the notebook
            endpoint = f"expenseconfig/v4/users/{user_id}/context/TRAVELER/expensetypes"
            response = self._make_request("GET", endpoint)
            data = response.json()
            
            expense_types = []
            for item in data:
                # Filter out items that start with '0' like the notebook
                if not item.get('expenseTypeId', '').startswith('0'):
                    expense_types.append({
                        'name': item.get('name'),
                        'id': item.get('expenseTypeId'),
                        'code': item.get('expenseCategoryCode'),
                        'expense_type_id': item.get('expenseTypeId'),  # For compatibility
                        'description': item.get('description'),
                        'is_deleted': item.get('isDeleted', False)
                    })
            
            return {
                'success': True,
                'expense_types': expense_types,
                'Items': expense_types,  # For compatibility with old format
                'count': len(expense_types),
                'api_version': 'v4_user_specific',
                'message': f'Retrieved {len(expense_types)} expense types from user-specific configuration'
            }
                
        except Exception as e:
            # Final fallback: Try v3 API (though it usually fails with 403)
            try:
                logger.info(f"v4 APIs failed: {e}, trying v3 API fallback")
                response = self._make_request("GET", "expense/expensetypes")
                data = response.json()
                
                expense_types = []
                for item in data.get('Items', []):
                    expense_types.append({
                        'code': item.get('Code'),
                        'name': item.get('Name'),
                        'category': item.get('CategoryCode'),
                        'spend_category': None,
                        'expense_type_id': item.get('ID'),
                        'description': None,
                        'is_deleted': False,
                        'show_on_mobile': True
                    })
                
                return {
                    'success': True,
                    'expense_types': expense_types,
                    'count': len(expense_types),
                    'api_version': 'v3',
                    'message': f'Retrieved {len(expense_types)} expense types from v3 API'
                }
            except Exception as v3_error:
                return {
                    'success': False,
                    'error': str(e),
                    'fallback_error': str(v3_error),
                    'message': f'Failed to retrieve expense types from all APIs: v4_user_policy, v4_company ({e}) and v3 ({v3_error})'
                }

    def approve_report(self, report_id: str, comment: str = "") -> Dict[str, Any]:
        """
        Approve an expense report as a manager.
        
        This first gets the report details to find the WorkflowActionURL, then uses it to approve.
        
        Args:
            report_id: The report ID (GUID) to approve
            comment: Optional comment for the approval (default: "")
            
        Returns:
            Dictionary containing:
            - success: Boolean indicating success/failure
            - message: Status message
            - report_id: The report ID that was approved
        """
        try:
            # Step 1: Get report details to find WorkflowActionURL
            details_endpoint = f"api/expense/expensereport/v2.0/report/{report_id}"
            details_response = self._make_request("GET", details_endpoint)
            
            if details_response.status_code != 200:
                return {
                    'success': False,
                    'error': f'Could not get report details: HTTP {details_response.status_code}',
                    'message': f'Failed to get report details for {report_id}',
                    'report_id': report_id
                }
            
            report_details = details_response.json()
            workflow_url = report_details.get('WorkflowActionURL', '')
            
            if not workflow_url:
                return {
                    'success': False,
                    'error': 'No WorkflowActionURL found in report details',
                    'message': f'Report {report_id} does not have a workflow action URL',
                    'report_id': report_id
                }
            
            # Step 2: Extract the endpoint path from the URL
            # URL format: https://integration.concursolutions.com/api/expense/expensereport/v1.1/report/{encoded_key}/WorkFlowAction
            # We need just the path part: api/expense/expensereport/v1.1/report/{encoded_key}/WorkFlowAction
            import re
            match = re.search(r'/api/expense/expensereport/v1\.1/report/[^/]+/WorkFlowAction', workflow_url)
            if not match:
                return {
                    'success': False,
                    'error': f'Could not parse WorkflowActionURL: {workflow_url}',
                    'message': f'Invalid workflow URL format',
                    'report_id': report_id
                }
            
            endpoint_path = match.group(0)[1:]  # Remove leading slash
            
            # Step 3: POST the approval action
            payload = {
                "WorkflowAction": {
                    "Action": "Approve",
                    "Comment": comment or "Approved via SDK"
                }
            }
            
            response = self._make_request("POST", endpoint_path, json=payload)
            
            # A 200 or 204 response indicates success
            if response.status_code in [200, 204]:
                return {
                    'success': True,
                    'message': f'Successfully approved report {report_id}',
                    'report_id': report_id,
                    'comment': payload['WorkflowAction']['Comment']
                }
            else:
                # Try to get error details from response
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', error_data.get('Message', 'Unknown error'))
                except:
                    error_msg = response.text or f'HTTP {response.status_code}'
                
                return {
                    'success': False,
                    'error': error_msg,
                    'message': f'Failed to approve report {report_id}: {error_msg}',
                    'report_id': report_id,
                    'status_code': response.status_code
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to approve report {report_id}: {str(e)}',
                'report_id': report_id
            }

    def get_payment_types(self) -> Dict[str, Any]:
        """
        Get available payment types using v4 API.
        
        Returns:
            Dictionary containing payment types
        """
        try:
            # Try v3 API first
            try:
                response = self._make_request("GET", "expense/paymenttypes")
                data = response.json()
                
                payment_types = []
                for item in data.get('Items', []):
                    payment_types.append({
                        'code': item.get('Code'),
                        'name': item.get('Name'),
                        'id': item.get('ID')
                    })
                
                return {
                    'success': True,
                    'payment_types': payment_types,
                    'count': len(payment_types)
                }
            except Exception as v3_error:
                logger.info(f"v3 API failed: {v3_error}, trying v4 API")
                
                # Try v4 API with user ID
                user_id = self.get_user_id()
                if not user_id:
                    raise Exception("Could not get user ID for v4 API")
                
                # Use v4 endpoint
                url = f"{self.config.base_url}/expenseconfig/v4/users/{user_id}/paymenttypes"
                headers = {
                    "Authorization": f"Bearer {self._get_access_token()}",
                    "Accept": "application/json"
                }
                
                response = self.session.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                payment_types = []
                # Handle both list and dict responses
                items = data if isinstance(data, list) else data.get('content', data.get('items', []))
                
                for item in items:
                    payment_types.append({
                        'code': item.get('paymentTypeId'),  # v4 uses paymentTypeId
                        'name': item.get('paymentTypeName'),  # v4 uses paymentTypeName
                        'id': item.get('paymentTypeId'),  # Use paymentTypeId as both code and id
                        'is_default': item.get('isDefault', False)
                    })
                
                return {
                    'success': True,
                    'payment_types': payment_types,
                    'count': len(payment_types),
                    'api_version': 'v4'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to retrieve payment types: {str(e)}'
            }

    def get_reports_with_foreign_currency(self, limit: int = 50) -> Dict[str, Any]:
        """
        Get expense reports that contain foreign currency expenses.
        
        This finds reports where expenses were incurred in a currency different from
        the report's base currency. Useful for identifying international expenses
        and foreign exchange transactions.
        
        Note: The Concur API doesn't have a direct hasForeignCurrency filter in v3,
        so we retrieve reports and analyze their currency fields.
        
        Args:
            limit: Maximum number of reports to retrieve (default: 50)
            
        Returns:
            Dictionary containing:
            - success: Boolean indicating success/failure
            - reports: List of reports with foreign currency expenses
            - count: Number of reports found
            - message: Status message
        """
        try:
            # Get all reports with limit
            endpoint = f"api/v3.0/expense/reports"
            params = {
                'limit': limit,
                'user': 'ALL'
            }
            
            response = self._make_request("GET", endpoint, params=params)
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': f'API request failed with status {response.status_code}'
                }
            
            data = response.json()
            all_reports = data.get('Items', [])
            
            # For each report, check if it has expenses in different currencies
            foreign_currency_reports = []
            
            for item in all_reports:
                report_currency = item.get('CurrencyCode', item.get('ReportCurrency', 'USD'))
                
                # Get report details to check expense currencies
                report_id = item.get('ID')
                if not report_id:
                    continue
                
                # Check if report has entries with different currency
                # Method 1: Check if report has OrgUnit fields that might indicate different countries
                country = item.get('Country', '')
                
                # Get the report entries to check transaction currencies
                try:
                    entries_result = self.get_report_entries(report_id)
                    if entries_result.get('success'):
                        entries = entries_result.get('entries', [])
                        has_foreign = False
                        foreign_currencies = set()
                        
                        for entry in entries:
                            transaction_currency = entry.get('transaction_currency_code', 
                                                            entry.get('TransactionCurrencyCode', ''))
                            if transaction_currency and transaction_currency != report_currency:
                                has_foreign = True
                                foreign_currencies.add(transaction_currency)
                        
                        if has_foreign:
                            report_data = {
                                'id': report_id,
                                'name': item.get('ReportName', ''),
                                'owner_name': item.get('OwnerName', ''),
                                'total': item.get('Total', 0),
                                'report_currency': report_currency,
                                'foreign_currencies': list(foreign_currencies),
                                'foreign_currency_count': len(foreign_currencies),
                                'approval_status': item.get('ApprovalStatusName', ''),
                                'approval_status_code': item.get('ApprovalStatusCode', ''),
                                'country': country,
                                'created_date': item.get('CreateDate', ''),
                                'submit_date': item.get('SubmitDate', '')
                            }
                            foreign_currency_reports.append(report_data)
                except Exception as e:
                    # If we can't get entries, skip this report
                    logger.debug(f"Could not check entries for report {report_id}: {str(e)}")
                    continue
            
            return {
                'success': True,
                'reports': foreign_currency_reports,
                'count': len(foreign_currency_reports),
                'total_checked': len(all_reports),
                'message': f'Found {len(foreign_currency_reports)} reports with foreign currency expenses out of {len(all_reports)} reports checked'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to retrieve reports with foreign currency: {str(e)}'
            }

    def get_reports_where_im_delegate(self, limit: int = 50) -> Dict[str, Any]:
        """
        Get expense reports where the current user is listed as a delegate.
        
        CSV Row #34: Can I see reports where I'm listed as a delegate?
        
        This retrieves reports where the current authenticated user has been assigned
        as a delegate, allowing them to act on behalf of the report owner.
        
        Args:
            limit: Maximum number of reports to return (default: 50)
            
        Returns:
            Dictionary containing reports where user is delegate and metadata
        """
        from datetime import datetime
        
        # Use v3.0 expense reports endpoint with delegateLoginID filter
        endpoint = "api/v3.0/expense/reports"
        
        params = {
            'delegateLoginID': 'me',  # 'me' refers to the current authenticated user
            'limit': limit
        }
        
        try:
            response = self._make_request("GET", endpoint, params=params)
            data = response.json()
            
            # v3 API returns Items array
            items = data.get('Items', [])
            
            reports = []
            for item in items:
                # Get approval status details
                approval_status_name = item.get('ApprovalStatusName', '')
                approval_status_code = item.get('ApprovalStatusCode', '')
                payment_status_name = item.get('PaymentStatusName', '')
                payment_status_code = item.get('PaymentStatusCode', '')
                
                # Calculate days since submission/creation
                submit_date_str = item.get('SubmitDate', '')
                create_date_str = item.get('CreateDate', '')
                days_since_submission = None
                days_since_creation = None
                
                if submit_date_str:
                    try:
                        submit_date = datetime.fromisoformat(submit_date_str.replace('Z', '+00:00'))
                        days_since_submission = (datetime.now() - submit_date.replace(tzinfo=None)).days
                    except:
                        pass
                
                if create_date_str:
                    try:
                        create_date = datetime.fromisoformat(create_date_str.replace('Z', '+00:00'))
                        days_since_creation = (datetime.now() - create_date.replace(tzinfo=None)).days
                    except:
                        pass
                
                report = ExpenseReport(
                    id=item.get('ID'),
                    name=item.get('Name'),
                    purpose=item.get('Purpose'),
                    business_purpose=item.get('BusinessPurpose'),
                    total=item.get('Total'),
                    currency_code=item.get('CurrencyCode'),
                    submission_date=submit_date_str,
                    approval_status=approval_status_name,
                    workflow_step=item.get('WorkflowStepName'),
                    owner_name=item.get('OwnerName'),
                    created_date=create_date_str,
                    last_modified_date=item.get('LastModifiedDate'),
                    country=item.get('Country'),
                    policy_id=item.get('PolicyID')
                )
                
                report_dict = asdict(report)
                report_dict['approval_status_code'] = approval_status_code
                report_dict['payment_status_name'] = payment_status_name
                report_dict['payment_status_code'] = payment_status_code
                report_dict['days_since_submission'] = days_since_submission
                report_dict['days_since_creation'] = days_since_creation
                report_dict['owner_login_id'] = item.get('OwnerLoginID', '')
                report_dict['delegate_login_id'] = item.get('DelegateLoginID', '')
                report_dict['delegate_name'] = item.get('DelegateName', '')
                reports.append(report_dict)
            
            return {
                'success': True,
                'reports': reports,
                'count': len(reports),
                'message': f'Retrieved {len(reports)} reports where you are listed as delegate'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to retrieve reports where you are delegate: {str(e)}'
            }

    def get_reports_with_corporate_card(self, limit: int = 50, user: str = 'ALL') -> Dict[str, Any]:
        """
        Get expense reports with expenses paid via corporate card.
        
        CSV Row #36: Show me reports with expenses from my corporate card
        
        This retrieves reports containing expenses paid with a corporate card (CBCP).
        CBCP = Company Billed Corporate Pay (expenses charged directly to company card).
        
        Useful for:
        - Reconciling corporate card statements
        - Identifying card-based expenses vs reimbursable expenses
        - Auditing corporate card usage
        - Tracking company-paid vs employee-paid expenses
        
        Args:
            limit: Maximum number of reports to return (default: 50)
            user: User filter - 'ALL', 'me', or specific loginID (default: 'ALL')
            
        Returns:
            Dictionary containing:
            - success: Boolean indicating success/failure
            - reports: List of reports with corporate card expenses
            - count: Number of reports found
            - payment_type_summary: Breakdown of reports by payment type
            - message: Status message
        """
        from datetime import datetime
        
        # Use v3.0 expense reports endpoint
        endpoint = "api/v3.0/expense/reports"
        
        # If user is 'me', use the actual username from config
        if user.lower() == 'me':
            user = self.config.username
        
        params = {
            'user': user,
            'limit': limit
        }
        
        try:
            response = self._make_request("GET", endpoint, params=params)
            data = response.json()
            
            # v3 API returns Items array
            items = data.get('Items', [])
            
            # Filter reports with corporate card payment type
            corporate_card_reports = []
            payment_type_summary = {}
            all_payment_types_seen = set()
            
            for item in items:
                # Get payment type information
                payment_type_code = None
                payment_type_name = None
                
                # Payment type can be in different formats
                if 'PaymentType' in item and item['PaymentType']:
                    if isinstance(item['PaymentType'], dict):
                        payment_type_name = item['PaymentType'].get('Name', '')
                        payment_type_code = item['PaymentType'].get('Code', '')
                    else:
                        payment_type_name = str(item['PaymentType'])
                
                if not payment_type_name and 'PaymentTypeName' in item:
                    payment_type_name = item.get('PaymentTypeName', '')
                
                if not payment_type_code and 'PaymentTypeCode' in item:
                    payment_type_code = item.get('PaymentTypeCode', '')
                
                # Track all payment types seen for diagnostics
                if payment_type_name:
                    all_payment_types_seen.add(f"{payment_type_name} ({payment_type_code or 'N/A'})")
                    if payment_type_name not in payment_type_summary:
                        payment_type_summary[payment_type_name] = 0
                    payment_type_summary[payment_type_name] += 1
                
                # Check if this is a corporate card payment (CBCP code or corporate card in name)
                is_corporate_card = False
                if payment_type_code and payment_type_code.upper() in ['CBCP', 'CORP', 'CARD']:
                    is_corporate_card = True
                elif payment_type_name:
                    # Check for common corporate card indicators in name
                    corp_indicators = ['corporate card', 'company card', 'corp card', 'cbcp', 'business card']
                    if any(indicator in payment_type_name.lower() for indicator in corp_indicators):
                        is_corporate_card = True
                
                if is_corporate_card:
                    # Get approval status details
                    approval_status_name = item.get('ApprovalStatusName', '')
                    approval_status_code = item.get('ApprovalStatusCode', '')
                    payment_status_name = item.get('PaymentStatusName', '')
                    payment_status_code = item.get('PaymentStatusCode', '')
                    
                    # Calculate days since submission
                    submit_date_str = item.get('SubmitDate', '')
                    days_since_submission = None
                    
                    if submit_date_str:
                        try:
                            submit_date = datetime.fromisoformat(submit_date_str.replace('Z', '+00:00'))
                            days_since_submission = (datetime.now() - submit_date.replace(tzinfo=None)).days
                        except:
                            pass
                    
                    report = ExpenseReport(
                        id=item.get('ID'),
                        name=item.get('Name'),
                        purpose=item.get('Purpose'),
                        business_purpose=item.get('BusinessPurpose'),
                        total=item.get('Total'),
                        currency_code=item.get('CurrencyCode'),
                        submission_date=submit_date_str,
                        approval_status=approval_status_name,
                        workflow_step=item.get('WorkflowStepName'),
                        owner_name=item.get('OwnerName'),
                        created_date=item.get('CreateDate'),
                        last_modified_date=item.get('LastModifiedDate'),
                        country=item.get('Country'),
                        policy_id=item.get('PolicyID')
                    )
                    
                    report_dict = asdict(report)
                    report_dict['approval_status_code'] = approval_status_code
                    report_dict['payment_status_name'] = payment_status_name
                    report_dict['payment_status_code'] = payment_status_code
                    report_dict['days_since_submission'] = days_since_submission
                    report_dict['payment_type_name'] = payment_type_name
                    report_dict['payment_type_code'] = payment_type_code
                    report_dict['owner_login_id'] = item.get('OwnerLoginID', '')
                    
                    corporate_card_reports.append(report_dict)
            
            return {
                'success': True,
                'reports': corporate_card_reports,
                'count': len(corporate_card_reports),
                'total_reports_checked': len(items),
                'payment_type_summary': payment_type_summary,
                'all_payment_types_seen': sorted(list(all_payment_types_seen)),
                'message': f'Found {len(corporate_card_reports)} reports with corporate card expenses out of {len(items)} total reports'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to retrieve reports with corporate card: {str(e)}'
            }

    def get_report_full_details(self, report_id: str) -> Dict[str, Any]:
        """
        Get the full details of a specific expense report including entries and allocations.
        
        CSV Row #32: Show me the full details of a specific expense report
        
        This uses the V2.0 API which returns complete report information including:
        - Report header fields (name, purpose, total, etc.)
        - All expense entries with details
        - Expense allocations
        - Workflow information
        - Custom fields
        
        Args:
            report_id: The report ID (GUID) to retrieve
            
        Returns:
            Dictionary containing:
            - success: Boolean indicating success/failure
            - report: Complete report details with entries and allocations
            - report_id: The report ID that was requested
            - message: Status message
        """
        try:
            # Use V2.0 API endpoint for complete report details
            endpoint = f"api/expense/expensereport/v2.0/report/{report_id}"
            
            response = self._make_request("GET", endpoint)
            
            if response.status_code == 404:
                return {
                    'success': False,
                    'error': 'Report not found',
                    'message': f'Report {report_id} does not exist',
                    'report_id': report_id
                }
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': f'API request failed with status {response.status_code}',
                    'report_id': report_id,
                    'response_text': response.text[:500] if hasattr(response, 'text') else None
                }
            
            report_data = response.json()
            
            # Extract key information for easy access
            # Note: V2.0 API uses slightly different field names than V3.0
            # Handle both string and numeric values for amounts
            report_total = report_data.get('ReportTotal', 0)
            if isinstance(report_total, str):
                try:
                    report_total = float(report_total)
                except (ValueError, TypeError):
                    report_total = 0.0
            
            summary = {
                'report_id': report_id,
                'report_name': report_data.get('ReportName', ''),
                'report_total': report_total,
                'currency_code': report_data.get('CurrencyCode', ''),
                'approval_status_name': report_data.get('ApprovalStatusName', ''),
                'payment_status_name': report_data.get('PaymentStatusName', ''),
                'owner_name': report_data.get('EmployeeName', report_data.get('OwnerName', '')),
                'owner_login_id': report_data.get('UserLoginID', report_data.get('OwnerLoginID', '')),
                'create_date': report_data.get('ReportDate', report_data.get('CreateDate', '')),
                'submit_date': report_data.get('SubmitDate', ''),
                'approved_date': report_data.get('ApprovedDate', ''),
                'expense_entries_count': len(report_data.get('ExpenseEntriesList', [])),
                'has_exception': report_data.get('HasException', 'N'),
                'business_purpose': report_data.get('ReportPurpose', report_data.get('BusinessPurpose', '')),
                'country': report_data.get('Country', report_data.get('CountryCode', '')),
                'policy_id': report_data.get('PolicyID', ''),
                'custom_fields': report_data.get('ReportCustomFields', [])
            }
            
            return {
                'success': True,
                'report': report_data,
                'summary': summary,
                'report_id': report_id,
                'message': f'Successfully retrieved full details for report {report_id}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to retrieve report details: {str(e)}',
                'report_id': report_id
            }
