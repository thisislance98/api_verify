#!/usr/bin/env python3
"""
Helper script to find ANY reports in the test environment
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from concur_expense_sdk import ConcurExpenseSDK, ConcurConfig
from tests.config import get_test_credentials

def main():
    print("Searching for ANY reports in the system...")
    print("=" * 80)
    
    # Try different accounts
    accounts = ['manager_approver', 'expense_user', 'expense_processor']
    
    for account_name in accounts:
        try:
            print(f"\nChecking account: {account_name}")
            print("-" * 80)
            
            creds = get_test_credentials(account_name, 'integration')
            config = ConcurConfig(
                client_id=creds['client_id'],
                client_secret=creds['client_secret'],
                username=creds['username'],
                password=creds['password'],
                base_url=creds['base_url'],
                token_url=creds['token_url']
            )
            
            sdk = ConcurExpenseSDK(config)
            
            # Search for any reports (no filters)
            result = sdk.get_expense_reports(params={'limit': 5})
            
            if result['success']:
                print(f"   Found {result['count']} reports")
                if result['count'] > 0:
                    print("\n   Sample reports:")
                    for idx, report in enumerate(result['reports'][:3], 1):
                        print(f"   {idx}. {report.get('Name', 'N/A')}")
                        print(f"      Report ID: {report.get('ID', 'N/A')}")
                        print(f"      Submit Date: {report.get('SubmitDate', 'N/A')}")
                        print(f"      Approved Date: {report.get('ApprovedDate', 'N/A')}")
                        print(f"      Status: {report.get('ApprovalStatusName', 'N/A')} ({report.get('ApprovalStatusCode', 'N/A')})")
                        print()
        except Exception as e:
            print(f"   Error: {e}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()

