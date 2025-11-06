#!/usr/bin/env python3
"""
Test script to verify the manager approval endpoint
Tests: GET /expensereports/v4/users/{userId}/context/MANAGER/reportsToApprove
"""

import os
from dotenv import load_dotenv
from concur_expense_sdk import ConcurExpenseSDK
import json

# Load environment variables
load_dotenv()

def test_manager_approval_endpoint():
    """Test the manager reports to approve endpoint"""
    
    print("=" * 80)
    print("Testing Manager Approval Endpoint")
    print("=" * 80)
    print()
    
    # Initialize SDK
    print("1. Initializing Concur SDK with admin credentials...")
    sdk = ConcurExpenseSDK()
    
    print(f"   Base URL: {sdk.config.base_url}")
    print(f"   Token URL: {sdk.config.token_url}")
    print(f"   Username: {sdk.config.username}")
    print()
    
    # Test connection
    print("2. Testing connection...")
    result = sdk.test_connection()
    if result['success']:
        print(f"   ✓ Connection successful")
        print(f"   Token prefix: {result['token_prefix']}")
    else:
        print(f"   ✗ Connection failed: {result['message']}")
        return
    print()
    
    # Get user ID
    print("3. Getting user ID...")
    user_id = sdk.get_user_id()
    if user_id:
        print(f"   ✓ User ID: {user_id}")
    else:
        print("   ✗ Could not get user ID")
        return
    print()
    
    # Test the manager approval endpoint
    print("4. Testing GET /expensereports/v4/users/{userId}/context/MANAGER/reportsToApprove")
    print("   Endpoint: GET /expensereports/v4/users/{}/context/MANAGER/reportsToApprove".format(user_id))
    print()
    
    try:
        result = sdk.get_reports_to_approve()
        
        if result['success']:
            print(f"   ✓ Request successful!")
            print(f"   Total reports to approve: {result['count']}")
            print(f"   Total elements: {result.get('totalElements', 'N/A')}")
            print()
            
            if result['count'] > 0:
                print("   Reports to approve:")
                print("   " + "-" * 76)
                for i, report in enumerate(result['reports'], 1):
                    print(f"   {i}. {report['name']}")
                    print(f"      Report ID: {report['id']}")
                    print(f"      Owner: {report.get('owner_name', 'N/A')}")
                    print(f"      Status: {report.get('approval_status', 'N/A')}")
                    print(f"      Amount: {report.get('total', 'N/A')} {report.get('currency_code', '')}")
                    print(f"      Submission Date: {report.get('submission_date', 'N/A')}")
                    print()
            else:
                print("   ℹ No reports need approval at this time")
            
            print()
            print("5. Testing with approval status filter...")
            try:
                result_filtered = sdk.get_reports_to_approve(approval_status='SUBMITTED')
                print(f"   ✓ Filter request successful!")
                print(f"   Reports with status 'SUBMITTED': {result_filtered['count']}")
            except Exception as e:
                print(f"   ℹ Filter test note: {str(e)}")
            
        else:
            print(f"   ✗ Request failed: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        import traceback
        print()
        print("   Full error details:")
        print("   " + "-" * 76)
        traceback.print_exc()
    
    print()
    print("=" * 80)
    print("Test Complete")
    print("=" * 80)

if __name__ == "__main__":
    test_manager_approval_endpoint()

