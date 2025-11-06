#!/usr/bin/env python3
"""
Search for any approved reports in the entire history
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from concur_expense_sdk import ConcurExpenseSDK, ConcurConfig
from tests.config import get_test_credentials

def main():
    print("Searching for historical approved reports...")
    print("=" * 80)
    
    # Try manager account
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
    
    # Search for any reports from 2020 onwards (very broad search)
    print("\n1. Searching for ANY reports from 2020 onwards...")
    result = sdk.get_expense_reports(params={
        'submitDateAfter': '2020-01-01',
        'limit': 10
    })
    
    if result['success']:
        print(f"   Found {result['count']} total reports")
        if result['count'] > 0:
            print("\n   Breakdown by status:")
            statuses = {}
            for report in result['reports']:
                status = report.get('ApprovalStatusCode', 'UNKNOWN')
                status_name = report.get('ApprovalStatusName', 'UNKNOWN')
                if status not in statuses:
                    statuses[status] = {'count': 0, 'name': status_name, 'reports': []}
                statuses[status]['count'] += 1
                statuses[status]['reports'].append(report)
            
            for status, data in statuses.items():
                print(f"   {status} ({data['name']}): {data['count']} reports")
                
                # Show sample reports for each status
                if data['reports']:
                    sample = data['reports'][0]
                    print(f"      Sample: {sample.get('ID', 'N/A')}")
                    print(f"      Submit: {sample.get('SubmitDate', 'N/A')}")
                    print(f"      Approved: {sample.get('ApprovedDate', 'N/A')}")
                    print(f"      LastModified: {sample.get('LastModifiedDate', 'N/A')}")
    
    # Try searching with user=ALL to see across all users
    print("\n2. Searching with user=ALL...")
    result = sdk.get_expense_reports(params={
        'user': 'ALL',
        'submitDateAfter': '2020-01-01',
        'limit': 20
    })
    
    if result['success']:
        print(f"   Found {result['count']} reports across all users")
        if result['count'] > 0:
            statuses = {}
            for report in result['reports']:
                status = report.get('ApprovalStatusCode', 'UNKNOWN')
                if status not in statuses:
                    statuses[status] = 0
                statuses[status] += 1
            
            print("   Status breakdown:")
            for status, count in statuses.items():
                print(f"      {status}: {count} reports")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()

