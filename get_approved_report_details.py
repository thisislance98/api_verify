#!/usr/bin/env python3
"""
Get details of the approved report
"""

import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent))

from concur_expense_sdk import ConcurExpenseSDK, ConcurConfig
from tests.config import get_test_credentials

def main():
    print("Getting approved report details...")
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
    
    # Search for approved reports
    result = sdk.get_expense_reports(params={
        'user': 'ALL',
        'approvalStatusCode': 'A_APPR',
        'submitDateAfter': '2020-01-01',
        'limit': 10
    })
    
    if result['success'] and result['count'] > 0:
        print(f"\nFound {result['count']} approved report(s):\n")
        
        for idx, report in enumerate(result['reports'], 1):
            print(f"Report #{idx}:")
            print(f"  ID: {report.get('ID', 'N/A')}")
            print(f"  Name: {report.get('Name', 'N/A')}")
            print(f"  Owner: {report.get('OwnerName', 'N/A')} ({report.get('OwnerLoginID', 'N/A')})")
            print(f"  Submit Date: {report.get('SubmitDate', 'N/A')}")
            print(f"  Approved Date: {report.get('ApprovedDate', 'N/A')}")
            print(f"  Last Modified: {report.get('LastModifiedDate', 'N/A')}")
            print(f"  Status: {report.get('ApprovalStatusName', 'N/A')} ({report.get('ApprovalStatusCode', 'N/A')})")
            print(f"  Total: {report.get('CurrencyCode', '')} {report.get('Total', 0)}")
            
            # Calculate approval time if both dates exist
            submit_date = report.get('SubmitDate')
            approved_date = report.get('ApprovedDate') or report.get('LastModifiedDate')
            
            if submit_date and approved_date:
                from datetime import datetime
                
                try:
                    if 'T' in submit_date:
                        submit_dt = datetime.fromisoformat(submit_date.replace('Z', '+00:00'))
                    else:
                        submit_dt = datetime.strptime(submit_date, '%Y-%m-%d')
                    
                    if 'T' in approved_date:
                        approved_dt = datetime.fromisoformat(approved_date.replace('Z', '+00:00'))
                    else:
                        approved_dt = datetime.strptime(approved_date, '%Y-%m-%d')
                    
                    delta = approved_dt - submit_dt
                    days = delta.total_seconds() / 86400
                    
                    print(f"  Approval Time: {days:.2f} days ({days * 24:.1f} hours)")
                except Exception as e:
                    print(f"  Approval Time: Could not calculate ({e})")
            
            print()
            
            # Show full JSON for debugging
            if idx == 1:
                print("  Full report data:")
                print(json.dumps(report, indent=4))
                print()
    else:
        print("  No approved reports found")
    
    print("=" * 80)

if __name__ == "__main__":
    main()

