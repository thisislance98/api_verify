#!/usr/bin/env python3
"""
Setup script for Test 006: Reports in Exception Review

This script helps create the test data needed for test_006_reports_in_exception_review.py

IMPORTANT: A_AAFH status (At Audit/Finance Handler) typically occurs when:
1. A report is submitted 
2. It gets flagged for exception review due to:
   - Policy violations
   - Missing required receipts
   - Amount thresholds exceeded
   - Manual routing for audit

Since programmatically forcing a report into A_AAFH status is challenging,
this script provides guidance and helper functions.

MANUAL STEPS REQUIRED:
1. Log into Concur UI (https://integration.api.concursolutions.com)
2. Create a new expense report
3. Add expenses that violate policy (e.g., missing receipts, over limits)
4. Submit the report
5. If configured, the report should route to exception review (A_AAFH)

Alternatively, as an administrator, you can manually route a submitted report
to exception review through the Concur admin interface.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from concur_expense_sdk import ConcurExpenseSDK, ConcurConfig
from tests.config import get_test_credentials
from datetime import datetime, timedelta


def check_existing_exception_reports():
    """Check if any reports already exist in exception review"""
    print("Checking for existing reports in exception review (A_AAFH)...")
    print("=" * 80)
    
    creds = get_test_credentials('manager_approver', 'integration')
    config = ConcurConfig(
        client_id=creds['client_id'],
        client_secret=creds['client_secret'],
        username=creds['username'],
        password=creds['password'],
        base_url=creds['base_url'],
        token_url=creds['token_url']
    )
    
    sdk = ConcurExpenseSDK(config)
    
    # Check for A_AAFH reports
    result = sdk.get_reports_in_exception_review(user='ALL')
    
    if result.get('success'):
        count = result.get('count', 0)
        print(f"Found {count} reports in exception review (A_AAFH)")
        
        if count > 0:
            print("\n✅ Test data already exists! The following reports are in exception review:")
            for report in result.get('reports', []):
                print(f"  - {report.get('name', 'N/A')}")
                print(f"    ID: {report.get('id', 'N/A')}")
                print(f"    Owner: {report.get('owner_name', 'N/A')}")
                print(f"    Amount: {report.get('total', 'N/A')} {report.get('currency_code', 'USD')}")
                print()
            return True
        else:
            print("\n❌ No reports found in exception review (A_AAFH)")
            return False
    else:
        print(f"❌ Error checking for reports: {result.get('message', 'Unknown error')}")
        return False


def check_other_report_statuses():
    """Check what other report statuses exist in the system"""
    print("\nChecking other report statuses in the system...")
    print("=" * 80)
    
    creds = get_test_credentials('manager_approver', 'integration')
    config = ConcurConfig(
        client_id=creds['client_id'],
        client_secret=creds['client_secret'],
        username=creds['username'],
        password=creds['password'],
        base_url=creds['base_url'],
        token_url=creds['token_url']
    )
    
    sdk = ConcurExpenseSDK(config)
    
    status_codes = {
        'A_PEND': 'Pending Approval',
        'A_APPR': 'Approved',
        'A_RESU': 'Resubmitted',
        'A_AAFH': 'At Audit/Finance Handler (Exception Review)',
        'A_NOTF': 'Not Submitted',
        'A_ACCO': 'Approved by Cost Object Approver'
    }
    
    for code, description in status_codes.items():
        result = sdk.get_expense_reports({
            'approvalStatusCode': code,
            'user': 'ALL',
            'limit': 5
        })
        
        if result.get('success'):
            count = result.get('count', 0)
            print(f"{code}: {count} reports - {description}")
            
            if count > 0 and count <= 2:
                for report in result.get('reports', [])[:2]:
                    print(f"  - {report.get('name', report.get('ReportName', 'N/A'))}")


def print_manual_instructions():
    """Print instructions for manually creating exception review data"""
    print("\n" + "=" * 80)
    print("MANUAL STEPS TO CREATE TEST DATA")
    print("=" * 80)
    print()
    print("Since A_AAFH status requires specific policy configuration, follow these steps:")
    print()
    print("1. Log into Concur UI:")
    print("   URL: https://integration.api.concursolutions.com")
    print("   Use credentials from: tests/config/test_accounts.json")
    print()
    print("2. Create a new expense report:")
    print("   - Click 'Expense' > 'Create New Report'")
    print("   - Name: 'Test Report - Exception Review'")
    print("   - Purpose: 'Testing A_AAFH status for automated tests'")
    print()
    print("3. Add expenses with policy violations:")
    print("   Option A - Missing Receipt:")
    print("     - Add an expense > $50 without attaching a receipt")
    print("     - This should trigger a receipt required exception")
    print()
    print("   Option B - Over Policy Limit:")
    print("     - Add a meal expense over the policy limit (e.g., $200)")
    print("     - This should trigger a policy violation")
    print()
    print("   Option C - Personal Expense:")
    print("     - Mark an expense as 'Personal'")
    print("     - This may trigger additional review")
    print()
    print("4. Submit the report:")
    print("   - Click 'Submit Report'")
    print("   - If policies are configured correctly, it should route to exception review")
    print()
    print("5. Verify the report is in A_AAFH status:")
    print("   - Run this script again to check")
    print("   - Or run: python tests/api_tests/test_007_reports_in_exception_review.py")
    print()
    print("ALTERNATIVE: Use Admin Functions")
    print("   - If you have admin access, you can manually route a submitted report")
    print("   - Go to Expense > Admin > Reports")
    print("   - Select a report and route it to exception review/audit")
    print()
    print("=" * 80)


def main():
    """Main execution"""
    print("\n" + "=" * 80)
    print("TEST 007 DATA SETUP: Reports in Exception Review (A_AAFH)")
    print("=" * 80)
    print()
    
    # Check if test data already exists
    if check_existing_exception_reports():
        print("\n✅ Test data exists! You can now run test_007.")
        print("   python tests/api_tests/test_007_reports_in_exception_review.py")
        return 0
    
    # Show other report statuses
    check_other_report_statuses()
    
    # Print manual instructions
    print_manual_instructions()
    
    print("\nAfter creating test data, run this script again to verify.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

