#!/usr/bin/env python3
"""
Helper script to find approved reports in the test environment
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from concur_expense_sdk import ConcurExpenseSDK, ConcurConfig
from tests.config import get_test_credentials
from datetime import datetime

def main():
    print("Searching for approved reports...")
    print("=" * 80)
    
    # Load credentials
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
    
    # Search for any approved reports
    print("\n1. Searching for ANY approved reports (no date filter)...")
    result = sdk.get_expense_reports(params={
        'approvalStatusCode': 'A_APPR',
        'limit': 10
    })
    
    if result['success']:
        print(f"   Found {result['count']} approved reports")
        if result['count'] > 0:
            print("\n   Sample reports:")
            for idx, report in enumerate(result['reports'][:5], 1):
                print(f"   {idx}. {report.get('Name', 'N/A')}")
                print(f"      Report ID: {report.get('ID', 'N/A')}")
                print(f"      Submit Date: {report.get('SubmitDate', 'N/A')}")
                print(f"      Approved Date: {report.get('ApprovedDate', 'N/A')}")
                print(f"      Last Modified: {report.get('LastModifiedDate', 'N/A')}")
                print(f"      Status: {report.get('ApprovalStatusName', 'N/A')}")
                print(f"      Total: {report.get('CurrencyCode', '')} {report.get('Total', 0)}")
                print()
    
    # Search for reports with different status codes
    print("\n2. Checking different approval statuses...")
    statuses = ['A_APPR', 'A_PEND', 'A_RESU', 'A_NOTF']
    for status in statuses:
        result = sdk.get_expense_reports(params={
            'approvalStatusCode': status,
            'limit': 1
        })
        if result['success']:
            print(f"   {status}: {result['count']} reports")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()

