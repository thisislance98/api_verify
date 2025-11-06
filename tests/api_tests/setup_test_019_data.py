#!/usr/bin/env python3
"""
Setup Test Data for Test 019: Reports Eligible for Early Payment

This script attempts to create test data for reports eligible for early payment.
Requirements:
- Approval Status: A_APPR (Approved)
- Payment Status: P_NOTP (Not Paid)
- Approved Date: At least 5 days ago

Strategy:
1. First check for existing approved reports (A_APPR + P_NOTP)
2. Try to approve pending reports programmatically
3. Provide manual instructions if programmatic approval fails
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from concur_expense_sdk import ConcurExpenseSDK, ConcurConfig
from tests.config import get_test_credentials
import json


class TestDataSetup:
    """Setup test data for reports eligible for early payment"""
    
    def __init__(self):
        self.sdk = None
    
    def setup(self):
        """Initialize SDK and authenticate"""
        print("=" * 80)
        print("Setup Test Data for Test 019: Reports Eligible for Early Payment")
        print("=" * 80)
        print()
        
        print("Initializing SDK...")
        try:
            creds = get_test_credentials('manager_approver', 'integration')
            config = ConcurConfig(
                client_id=creds['client_id'],
                client_secret=creds['client_secret'],
                username=creds['username'],
                password=creds['password'],
                base_url=creds['base_url'],
                token_url=creds['token_url']
            )
            
            self.sdk = ConcurExpenseSDK(config)
            print(f"  ✓ SDK initialized")
            print(f"  Environment: {creds['environment']}")
            print(f"  Username: {self.sdk.config.username}")
            print()
            
            result = self.sdk.test_connection()
            if result['success']:
                print(f"  ✓ Authentication successful")
                print()
            else:
                raise Exception(f"Authentication failed: {result['message']}")
            
            return True
            
        except Exception as e:
            print(f"  ✗ Setup failed: {str(e)}")
            return False
    
    def check_existing_approved_reports(self):
        """Check for existing approved reports that might meet criteria"""
        print("=" * 80)
        print("Step 1: Checking for Existing Approved Reports (A_APPR + P_NOTP)")
        print("=" * 80)
        print()
        
        endpoint = "api/v3.0/expense/reports"
        
        # Check for approved, not paid reports (regardless of date)
        params = {
            'approvalStatusCode': 'A_APPR',
            'paymentStatusCode': 'P_NOTP',
            'limit': 100,
            'user': 'ALL'
        }
        
        try:
            response = self.sdk._make_request("GET", endpoint, params=params)
            data = response.json()
            items = data.get('Items', [])
            
            print(f"Found {len(items)} approved, not-paid reports")
            
            if len(items) > 0:
                print("\nAnalyzing approval dates:")
                print("-" * 80)
                
                old_enough = []
                too_recent = []
                no_date = []
                
                for item in items:
                    report_id = item.get('ID')
                    report_name = item.get('Name')
                    approval_date_str = item.get('ApprovedDate', '')
                    total = item.get('Total', 0)
                    currency = item.get('CurrencyCode', '')
                    
                    if approval_date_str:
                        try:
                            approval_date = datetime.fromisoformat(approval_date_str.replace('Z', '+00:00'))
                            days_ago = (datetime.now() - approval_date.replace(tzinfo=None)).days
                            
                            if days_ago >= 5:
                                old_enough.append({
                                    'id': report_id,
                                    'name': report_name,
                                    'days_ago': days_ago,
                                    'total': total,
                                    'currency': currency,
                                    'approval_date': approval_date_str
                                })
                            else:
                                too_recent.append({
                                    'id': report_id,
                                    'name': report_name,
                                    'days_ago': days_ago,
                                    'total': total,
                                    'currency': currency
                                })
                        except:
                            no_date.append({'id': report_id, 'name': report_name})
                    else:
                        no_date.append({'id': report_id, 'name': report_name})
                
                print(f"\n✅ Reports approved 5+ days ago: {len(old_enough)}")
                if old_enough:
                    for r in old_enough[:5]:  # Show first 5
                        print(f"   - {r['name']} (ID: {r['id']})")
                        print(f"     Amount: {r['total']} {r['currency']}")
                        print(f"     Days since approval: {r['days_ago']}")
                
                print(f"\n⏰ Reports approved less than 5 days ago: {len(too_recent)}")
                if too_recent:
                    for r in too_recent[:3]:
                        print(f"   - {r['name']} (ID: {r['id']})")
                        print(f"     Days since approval: {r['days_ago']} (needs {5 - r['days_ago']} more days)")
                
                print(f"\n❓ Reports without approval date: {len(no_date)}")
                
                if old_enough:
                    print("\n" + "=" * 80)
                    print("✅ SUCCESS: Found suitable test data!")
                    print("=" * 80)
                    print(f"\nYou already have {len(old_enough)} report(s) that meet the criteria.")
                    print("Test 019 should now return data when you run it.")
                    return True
                
                if too_recent:
                    print("\n" + "=" * 80)
                    print("⏰ WAITING PERIOD REQUIRED")
                    print("=" * 80)
                    print(f"\nYou have {len(too_recent)} approved report(s), but they are too recent.")
                    oldest = min(too_recent, key=lambda x: x['days_ago'])
                    days_needed = 5 - oldest['days_ago']
                    print(f"Wait {days_needed} more day(s) and the test will have data.")
                    return False
            else:
                print("No approved, not-paid reports found in the system.")
            
            return False
            
        except Exception as e:
            print(f"✗ Error checking existing reports: {str(e)}")
            return False
    
    def check_pending_reports(self):
        """Check for pending reports that could be approved"""
        print("\n" + "=" * 80)
        print("Step 2: Checking for Pending Reports That Could Be Approved")
        print("=" * 80)
        print()
        
        try:
            # Use the v4 endpoint which works better
            result = self.sdk.get_reports_to_approve()
            
            if result['success']:
                reports = result.get('reports', [])
                print(f"Found {len(reports)} pending reports")
                
                if len(reports) > 0:
                    print("\nReports ready for approval:")
                    print("-" * 80)
                    
                    items = []
                    for i, report in enumerate(reports[:5], 1):  # Show first 5
                        print(f"{i}. {report.get('name')} (ID: {report.get('id')})")
                        print(f"   Owner: {report.get('owner_name')}")
                        print(f"   Amount: {report.get('total')} {report.get('currency_code')}")
                        print(f"   Submitted: {report.get('submission_date')}")
                        print()
                        
                        # Convert to V3 format for compatibility
                        items.append({
                            'ID': report.get('id'),
                            'Name': report.get('name'),
                            'OwnerName': report.get('owner_name'),
                            'Total': report.get('total'),
                            'CurrencyCode': report.get('currency_code'),
                            'SubmitDate': report.get('submission_date')
                        })
                    
                    return items
                else:
                    print("No pending reports found.")
                    return []
            else:
                print(f"✗ Error: {result.get('message')}")
                return []
            
        except Exception as e:
            print(f"✗ Error checking pending reports: {str(e)}")
            return []
    
    def try_programmatic_approval(self, reports):
        """Try to approve reports programmatically"""
        print("=" * 80)
        print("Step 3: Attempting Programmatic Approval")
        print("=" * 80)
        print()
        
        if not reports:
            print("No pending reports to approve.")
            return False
        
        # Try to approve the first report
        report = reports[0]
        report_id = report.get('ID')
        report_name = report.get('Name')
        
        print(f"Attempting to approve: {report_name} (ID: {report_id})")
        
        try:
            result = self.sdk.approve_report(report_id)
            
            if result['success']:
                print(f"✅ Successfully approved report!")
                print(f"\nNOTE: The report needs to be approved for 5 days before it shows up in test 019.")
                print(f"      Current approval date: {datetime.now().strftime('%Y-%m-%d')}")
                print(f"      Will be eligible on: {(datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')}")
                return True
            else:
                print(f"✗ Failed to approve report: {result.get('message')}")
                return False
                
        except Exception as e:
            print(f"✗ Exception during approval: {str(e)}")
            return False
    
    def provide_manual_instructions(self, pending_reports):
        """Provide manual instructions for creating test data"""
        print("\n" + "=" * 80)
        print("📋 MANUAL SETUP REQUIRED")
        print("=" * 80)
        print()
        print("Programmatic approval is not available. Please follow these steps:")
        print()
        print("1. Log into Concur UI:")
        print("   URL: https://integration.api.concursolutions.com")
        print("   Username: mgr3@p10005178e93.com")
        print("   Password: password12")
        print()
        print("2. Navigate to: Expense Reports > Pending Approvals")
        print()
        
        if pending_reports:
            print("3. Approve one of these reports:")
            for i, report in enumerate(pending_reports[:3], 1):
                print(f"   Option {i}: \"{report.get('Name')}\" (ID: {report.get('ID')})")
                print(f"            Amount: {report.get('Total')} {report.get('CurrencyCode')}")
        else:
            print("3. Approve any pending report you find")
        
        print()
        print("4. IMPORTANT: Do NOT process the report for payment")
        print("   - The report should stay in 'Not Paid' (P_NOTP) status")
        print("   - Do NOT extract or move to payment processing")
        print()
        print("5. Wait 5 days (or adjust report date if possible)")
        print()
        print("6. Run Test 019 again to verify data is available")
        print()
        print("=" * 80)
    
    def run(self):
        """Run the setup process"""
        if not self.setup():
            return False
        
        # Step 1: Check for existing suitable reports
        has_data = self.check_existing_approved_reports()
        
        if has_data:
            return True
        
        # Step 2: Check for pending reports
        pending_reports = self.check_pending_reports()
        
        # Step 3: Try programmatic approval
        if pending_reports:
            success = self.try_programmatic_approval(pending_reports)
            
            if success:
                return True
        
        # Step 4: Provide manual instructions
        self.provide_manual_instructions(pending_reports)
        
        return False


def main():
    """Main execution"""
    setup = TestDataSetup()
    setup.run()


if __name__ == "__main__":
    main()

