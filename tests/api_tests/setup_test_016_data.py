#!/usr/bin/env python3
"""
Test Data Setup for Test #016: Average Approval Time

This script approves pending reports to create test data for the average
approval time calculation test.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from concur_expense_sdk import ConcurExpenseSDK, ConcurConfig
from tests.config import get_test_credentials

def main():
    print("=" * 80)
    print("Test Data Setup for Test #016: Average Approval Time")
    print("=" * 80)
    print()
    
    # First, find pending reports as the expense user
    print("Step 1: Finding pending reports...")
    print("-" * 80)
    
    user_creds = get_test_credentials('expense_user', 'integration')
    user_config = ConcurConfig(
        client_id=user_creds['client_id'],
        client_secret=user_creds['client_secret'],
        username=user_creds['username'],
        password=user_creds['password'],
        base_url=user_creds['base_url'],
        token_url=user_creds['token_url']
    )
    
    user_sdk = ConcurExpenseSDK(user_config)
    
    # Get pending reports
    result = user_sdk.get_expense_reports(params={
        'approvalStatusCode': 'A_PEND',
        'limit': 5
    })
    
    if not result['success'] or result['count'] == 0:
        print("  ✗ No pending reports found to approve")
        return False
    
    print(f"  ✓ Found {result['count']} pending reports")
    pending_reports = result['reports']
    
    for idx, report in enumerate(pending_reports, 1):
        print(f"  {idx}. Report {report.get('ID', 'N/A')}")
        print(f"     Submit Date: {report.get('SubmitDate', 'N/A')}")
        print(f"     Status: {report.get('ApprovalStatusName', 'N/A')}")
    
    print()
    
    # Now approve reports as manager
    print("Step 2: Approving reports as manager...")
    print("-" * 80)
    
    mgr_creds = get_test_credentials('manager_approver', 'integration')
    mgr_config = ConcurConfig(
        client_id=mgr_creds['client_id'],
        client_secret=mgr_creds['client_secret'],
        username=mgr_creds['username'],
        password=mgr_creds['password'],
        base_url=mgr_creds['base_url'],
        token_url=mgr_creds['token_url']
    )
    
    mgr_sdk = ConcurExpenseSDK(mgr_config)
    
    # Try to approve each report
    approved_count = 0
    for idx, report in enumerate(pending_reports[:3], 1):  # Try to approve first 3
        report_id = report.get('ID')
        
        print(f"\n  Attempting to approve report {idx}: {report_id}")
        
        # Try to approve the report
        result = mgr_sdk.approve_report(
            report_id=report_id,
            comment="Approved for Test #016 - Average Approval Time calculation"
        )
        
        if result['success']:
            print(f"    ✓ Report approved successfully")
            approved_count += 1
        else:
            print(f"    ✗ Failed to approve: {result.get('message', 'Unknown error')}")
    
    print()
    print("-" * 80)
    print(f"Summary: Approved {approved_count} out of {min(3, len(pending_reports))} reports")
    print("=" * 80)
    
    if approved_count > 0:
        print("\n✓ Test data setup complete!")
        print("You can now run test_016_average_approval_time.py")
        return True
    else:
        print("\n✗ Could not approve any reports")
        print("The manager account may not have permission to approve these reports")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

