#!/usr/bin/env python3
"""
Setup Test Data for Test #041: Reports Submitted On Behalf of Manager

This script creates test data for the delegate submission scenario where
a delegate submits expense reports on behalf of another user (manager).

Prerequisites:
- delegate_user or expense_user must have delegate permissions
- Target manager/user must grant delegate access to the delegate user

Note: The Concur V3/V4 APIs do not provide a method to programmatically
      submit reports on behalf of another user. This requires manual steps.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from concur_expense_sdk import ConcurExpenseSDK, ConcurConfig
from tests.config import get_test_credentials
from datetime import datetime


def check_delegate_permissions():
    """Check if the user has delegate access to any users"""
    print("=" * 80)
    print("Test #041 Data Setup: Delegate Submission")
    print("=" * 80)
    print()
    
    print("Step 1: Checking delegate permissions...")
    print("-" * 80)
    
    # Try to authenticate as delegate
    accounts_to_try = [
        ('expense_user', 'integration'),
        ('delegate_user', 'integration')
    ]
    
    sdk = None
    delegate_login = None
    
    for account_role, environment in accounts_to_try:
        try:
            print(f"  Trying {account_role}...")
            creds = get_test_credentials(account_role, environment)
            config = ConcurConfig(
                client_id=creds['client_id'],
                client_secret=creds['client_secret'],
                username=creds['username'],
                password=creds['password'],
                base_url=creds['base_url'],
                token_url=creds['token_url']
            )
            
            sdk = ConcurExpenseSDK(config)
            delegate_login = creds['username']
            
            result = sdk.test_connection()
            if result['success']:
                print(f"  ✓ Authenticated as {delegate_login}")
                break
            else:
                print(f"  ✗ Authentication failed: {result['message']}")
                continue
        except Exception as e:
            print(f"  ✗ Failed: {str(e)}")
            continue
    
    if not sdk:
        print()
        print("❌ Unable to authenticate with any delegate user")
        return False
    
    print()
    print(f"✓ Successfully authenticated as: {delegate_login}")
    print()
    
    # Check for existing delegate-submitted reports
    print("Step 2: Checking for existing delegate-submitted reports...")
    print("-" * 80)
    
    result = sdk.get_expense_reports(params={'limit': 100, 'user': 'ALL'})
    
    if result['success']:
        all_reports = result.get('reports', [])
        
        # Filter for delegate-submitted reports
        delegate_submitted = [
            r for r in all_reports
            if r.get('submitter_login_id') and 
               r.get('submitter_login_id').lower() == delegate_login.lower() and
               r.get('owner_login_id') and
               r.get('owner_login_id').lower() != delegate_login.lower()
        ]
        
        print(f"  Total reports in system: {len(all_reports)}")
        print(f"  Reports submitted by delegate on behalf of others: {len(delegate_submitted)}")
        
        if len(delegate_submitted) > 0:
            print()
            print("  ✓ Test data already exists!")
            print()
            print("  Sample delegate-submitted reports:")
            for i, report in enumerate(delegate_submitted[:3], 1):
                print(f"\n    Report #{i}:")
                print(f"      ID: {report.get('id')}")
                print(f"      Name: {report.get('name')}")
                print(f"      Owner: {report.get('owner_name')} ({report.get('owner_login_id')})")
                print(f"      Submitter: {report.get('submitter_name')} ({report.get('submitter_login_id')})")
                print(f"      Status: {report.get('approval_status')}")
            
            print()
            print("=" * 80)
            print("✓ Test data exists. Test #041 is ready to run!")
            print("=" * 80)
            return True
        else:
            print()
            print("  ⚠️  No delegate-submitted reports found")
    else:
        print(f"  ✗ Failed to retrieve reports: {result.get('error')}")
        return False
    
    print()
    print("=" * 80)
    print("MANUAL SETUP REQUIRED")
    print("=" * 80)
    print()
    print("⚠️  API LIMITATION: Concur V3/V4 APIs do not provide a method to")
    print("    programmatically submit reports on behalf of another user.")
    print()
    print("📋 MANUAL STEPS TO CREATE TEST DATA:")
    print()
    print("1. Configure Delegate Access (if not already done):")
    print("   a. Log into Concur UI as the manager/user who will grant access")
    print("      Suggested: mgr3@p10005178e93.com (password: password12)")
    print("   b. Go to Profile > Profile Settings > Expense Delegates")
    print("   c. Add delegate: user11@p10005178e93.com")
    print("   d. Grant permissions: 'Can Prepare', 'Can Submit', 'Can View Receipts'")
    print("   e. Save")
    print()
    print("2. Create & Submit Report as Delegate:")
    print(f"   a. Log into Concur UI as delegate: {delegate_login}")
    print("      (Integration: https://integration.concursolutions.com)")
    print("   b. Navigate to: Expense > Act On Behalf Of")
    print("   c. Select the manager you added in step 1 (e.g., mgr3@p10005178e93.com)")
    print("   d. Create a new expense report:")
    print("      - Report Name: 'Delegate Test Report'")
    print("      - Add an expense (e.g., Parking, $25)")
    print("      - Business Purpose: 'Test delegate submission'")
    print("   e. Submit the report")
    print()
    print("3. Verify Test Data:")
    print("   - Run: python tests/api_tests/test_041_reports_submitted_on_behalf_of_manager.py")
    print("   - Should now find 1+ delegate-submitted reports")
    print()
    print("4. Expected Behavior:")
    print("   - Report Owner: Manager (e.g., mgr3@p10005178e93.com)")
    print("   - Report Submitter: Delegate (e.g., user11@p10005178e93.com)")
    print("   - When querying as delegate, can see status of reports submitted on behalf")
    print()
    print("=" * 80)
    print()
    print("💡 TIP: You can also check in Concur UI:")
    print("   - As delegate: 'Expense' > 'Reports' > filter by 'On Behalf Of'")
    print("   - As manager: 'Expense' > 'Reports' > see submitted reports")
    print()
    
    return False


def main():
    """Main setup function"""
    result = check_delegate_permissions()
    
    if result:
        print("\n✓ Setup complete - test data exists")
        sys.exit(0)
    else:
        print("\n⚠️  Setup incomplete - manual steps required")
        print("    See instructions above")
        sys.exit(1)


if __name__ == "__main__":
    main()

