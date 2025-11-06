#!/usr/bin/env python3
"""
Test Case #033: Payment Method for Approved Reports
User Query: What's the payment method for my approved reports?
Service: Expense Reports & Status
API: GET /api/v3.0/expense/reports

This test retrieves all approved expense reports and analyzes their payment methods.
This is useful for understanding how reimbursements will be processed (ACH, Check,
Wire Transfer, etc.) and identifying reports that may need payment method updates.

CSV Row #33:
- Query: "What's the payment method for my approved reports?"
- Service: Expense Reports & Status
- Method: GET
- Endpoint: /api/v3.0/expense/reports
- Filter: paymentStatusCode=A_APPR, check PaymentType field
"""

import sys
import os
import json
from datetime import datetime
from collections import defaultdict

# Add parent directory to path to import config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tests.config import get_test_credentials
from concur_expense_sdk import ConcurExpenseSDK, ConcurConfig


class TestApprovedReportsPaymentMethod:
    """Test suite for analyzing payment methods of approved reports"""
    
    def __init__(self):
        """Initialize test suite"""
        self.sdk = None
        self.user_id = None
        self.test_results = []
        
    def setup(self):
        """Initialize SDK with test credentials"""
        print("=" * 80)
        print("TEST CASE #033: Payment Method for Approved Reports")
        print("=" * 80)
        
        # Get expense user credentials to see their own approved reports
        creds = get_test_credentials('expense_user', 'integration')
        
        config = ConcurConfig(
            client_id=creds['client_id'],
            client_secret=creds['client_secret'],
            username=creds['username'],
            password=creds['password'],
            base_url=creds['base_url'],
            token_url=creds['token_url']
        )
        
        self.sdk = ConcurExpenseSDK(config)
        print(f"✓ SDK initialized")
        print(f"  Environment: {creds['environment']}")
        print(f"  Base URL: {self.sdk.config.base_url}")
        print(f"  Username: {self.sdk.config.username}")
        print(f"  Role: {creds['role']}")
        
        # Test connection
        print(f"\n✓ Authenticating as {creds['username']}...")
        result = self.sdk.test_connection()
        if not result['success']:
            raise Exception(f"Authentication failed: {result['message']}")
        print("✓ Authentication successful")
        
        # Get user ID
        self.user_id = self.sdk.get_user_id()
        print(f"✓ User ID: {self.user_id}")
        print()
    
    def test_1_get_approved_reports_with_payment_types(self):
        """Test 1: Retrieve approved reports and analyze payment methods"""
        print("\n" + "=" * 80)
        print("TEST 1: Get Approved Reports with Payment Methods")
        print("=" * 80)
        
        try:
            # Get approved reports (A_APPR status)
            print("\n📋 Fetching approved reports...")
            params = {
                'approvalStatusCode': 'A_APPR',
                'user': 'me',
                'limit': 100
            }
            
            response = self.sdk.get_expense_reports(params)
            reports = response.get('Items', [])
            
            print(f"✓ Found {len(reports)} approved reports")
            
            if len(reports) == 0:
                print("\n⚠️  No approved reports found")
                print("   To create test data:")
                print("   1. Submit an expense report")
                print("   2. Have it approved by a manager")
                print("   3. Ensure report has payment method configured")
                
                self.test_results.append({
                    'test_name': 'Get approved reports with payment methods',
                    'endpoint': '/api/v3.0/expense/reports?approvalStatusCode=A_APPR&user=me',
                    'method': 'GET',
                    'passed': True,
                    'response': {
                        'total_reports': 0,
                        'message': 'No approved reports found - test data needed'
                    },
                    'error': None
                })
                return
            
            # Analyze payment methods
            payment_methods = defaultdict(list)
            payment_type_counts = defaultdict(int)
            reports_without_payment_type = []
            total_amount_by_payment = defaultdict(float)
            
            print("\n📊 Analyzing payment methods...")
            print("-" * 80)
            
            for report in reports:
                report_id = report.get('ID', 'Unknown')
                report_name = report.get('Name', 'Unnamed')
                total_amount = float(report.get('Total', 0))
                payment_type = report.get('PaymentType', '')
                payment_status = report.get('PaymentStatusName', 'Unknown')
                owner_name = report.get('OwnerName', 'Unknown')
                
                # Track by payment type
                if payment_type:
                    payment_methods[payment_type].append({
                        'report_id': report_id,
                        'report_name': report_name,
                        'amount': total_amount,
                        'owner_name': owner_name,
                        'payment_status': payment_status
                    })
                    payment_type_counts[payment_type] += 1
                    total_amount_by_payment[payment_type] += total_amount
                else:
                    # Reports without payment type
                    reports_without_payment_type.append({
                        'report_id': report_id,
                        'report_name': report_name,
                        'amount': total_amount,
                        'owner_name': owner_name,
                        'payment_status': payment_status
                    })
                
                # Print individual report details
                payment_display = payment_type if payment_type else "NOT SET"
                print(f"\n  Report: {report_name}")
                print(f"    ID: {report_id}")
                print(f"    Owner: {owner_name}")
                print(f"    Amount: ${total_amount:,.2f}")
                print(f"    Payment Type: {payment_display}")
                print(f"    Payment Status: {payment_status}")
            
            # Summary by payment method
            print("\n" + "=" * 80)
            print("PAYMENT METHOD SUMMARY")
            print("=" * 80)
            
            if payment_methods:
                print("\n✓ Reports by Payment Method:")
                for payment_type, report_list in sorted(payment_methods.items()):
                    count = len(report_list)
                    total = total_amount_by_payment[payment_type]
                    print(f"\n  {payment_type}:")
                    print(f"    Count: {count} report(s)")
                    print(f"    Total: ${total:,.2f}")
                    
                    # List reports under this payment type
                    for rpt in report_list:
                        print(f"      - {rpt['report_name']} (${rpt['amount']:,.2f}) - {rpt['owner_name']}")
            else:
                print("\n⚠️  No reports have payment methods configured")
            
            # Reports without payment type
            if reports_without_payment_type:
                print(f"\n⚠️  Reports WITHOUT Payment Method: {len(reports_without_payment_type)}")
                for rpt in reports_without_payment_type:
                    print(f"    - {rpt['report_name']} (${rpt['amount']:,.2f}) - {rpt['owner_name']}")
                print("\n   These reports may need payment method configuration before processing.")
            
            # Overall statistics
            print("\n" + "=" * 80)
            print("OVERALL STATISTICS")
            print("=" * 80)
            total_reports = len(reports)
            reports_with_payment = total_reports - len(reports_without_payment_type)
            coverage_pct = (reports_with_payment / total_reports * 100) if total_reports > 0 else 0
            
            print(f"  Total Approved Reports: {total_reports}")
            print(f"  Reports with Payment Method: {reports_with_payment} ({coverage_pct:.1f}%)")
            print(f"  Reports without Payment Method: {len(reports_without_payment_type)}")
            print(f"  Unique Payment Methods: {len(payment_methods)}")
            print(f"  Total Amount: ${sum(total_amount_by_payment.values()):,.2f}")
            
            # Store test result
            self.test_results.append({
                'test_name': 'Get approved reports with payment methods',
                'endpoint': '/api/v3.0/expense/reports?approvalStatusCode=A_APPR&user=me',
                'method': 'GET',
                'passed': True,
                'response': {
                    'total_reports': total_reports,
                    'reports_with_payment_method': reports_with_payment,
                    'reports_without_payment_method': len(reports_without_payment_type),
                    'payment_method_coverage': f"{coverage_pct:.1f}%",
                    'unique_payment_methods': len(payment_methods),
                    'payment_methods': dict(payment_type_counts),
                    'total_amount_by_payment': {k: f"${v:,.2f}" for k, v in total_amount_by_payment.items()},
                    'reports': reports
                },
                'error': None
            })
            
            print("\n✅ TEST PASSED - Successfully analyzed payment methods for approved reports")
            
        except Exception as e:
            print(f"\n❌ TEST FAILED: {str(e)}")
            self.test_results.append({
                'test_name': 'Get approved reports with payment methods',
                'endpoint': '/api/v3.0/expense/reports?approvalStatusCode=A_APPR&user=me',
                'method': 'GET',
                'passed': False,
                'response': None,
                'error': str(e)
            })
    
    def test_2_get_approved_reports_by_specific_payment_method(self):
        """Test 2: Filter approved reports by specific payment method (ACH)"""
        print("\n" + "=" * 80)
        print("TEST 2: Get Approved Reports by Specific Payment Method (ACH)")
        print("=" * 80)
        
        try:
            # Note: Concur API doesn't support PaymentType as a direct filter parameter
            # We need to fetch all approved reports and filter client-side
            print("\n📋 Fetching approved reports and filtering for ACH...")
            params = {
                'approvalStatusCode': 'A_APPR',
                'user': 'me',
                'limit': 100
            }
            
            response = self.sdk.get_expense_reports(params)
            all_reports = response.get('Items', [])
            
            # Filter for ACH payment method
            ach_reports = [r for r in all_reports if r.get('PaymentType', '').upper() == 'ACH']
            
            print(f"✓ Found {len(all_reports)} total approved reports")
            print(f"✓ Found {len(ach_reports)} reports with ACH payment method")
            
            if len(ach_reports) > 0:
                print("\n📊 ACH Payment Reports:")
                print("-" * 80)
                total_ach_amount = 0
                
                for report in ach_reports:
                    report_name = report.get('Name', 'Unnamed')
                    report_id = report.get('ID', 'Unknown')
                    amount = float(report.get('Total', 0))
                    owner_name = report.get('OwnerName', 'Unknown')
                    payment_status = report.get('PaymentStatusName', 'Unknown')
                    
                    total_ach_amount += amount
                    
                    print(f"\n  Report: {report_name}")
                    print(f"    ID: {report_id}")
                    print(f"    Owner: {owner_name}")
                    print(f"    Amount: ${amount:,.2f}")
                    print(f"    Payment Status: {payment_status}")
                
                print("\n" + "-" * 80)
                print(f"  Total ACH Amount: ${total_ach_amount:,.2f}")
                print(f"  Average ACH Amount: ${total_ach_amount / len(ach_reports):,.2f}")
            else:
                print("\n⚠️  No ACH payment reports found")
                print("   Payment methods available in approved reports:")
                payment_types = set([r.get('PaymentType', 'NOT SET') for r in all_reports])
                for pt in sorted(payment_types):
                    count = len([r for r in all_reports if r.get('PaymentType', 'NOT SET') == pt])
                    print(f"     - {pt}: {count} report(s)")
            
            # Store test result
            self.test_results.append({
                'test_name': 'Get approved reports with ACH payment method',
                'endpoint': '/api/v3.0/expense/reports?approvalStatusCode=A_APPR&user=me (filtered for PaymentType=ACH)',
                'method': 'GET',
                'passed': True,
                'response': {
                    'total_approved_reports': len(all_reports),
                    'ach_reports_count': len(ach_reports),
                    'ach_reports': ach_reports if ach_reports else [],
                    'note': 'PaymentType filter applied client-side (not supported as API parameter)'
                },
                'error': None
            })
            
            print("\n✅ TEST PASSED - Successfully filtered for ACH payment method")
            
        except Exception as e:
            print(f"\n❌ TEST FAILED: {str(e)}")
            self.test_results.append({
                'test_name': 'Get approved reports with ACH payment method',
                'endpoint': '/api/v3.0/expense/reports?approvalStatusCode=A_APPR&user=me (filtered for PaymentType=ACH)',
                'method': 'GET',
                'passed': False,
                'response': None,
                'error': str(e)
            })
    
    def test_3_get_approved_reports_without_payment_method(self):
        """Test 3: Find approved reports that need payment method configuration"""
        print("\n" + "=" * 80)
        print("TEST 3: Get Approved Reports WITHOUT Payment Method")
        print("=" * 80)
        
        try:
            print("\n📋 Fetching approved reports without payment method...")
            params = {
                'approvalStatusCode': 'A_APPR',
                'user': 'me',
                'limit': 100
            }
            
            response = self.sdk.get_expense_reports(params)
            all_reports = response.get('Items', [])
            
            # Filter for reports without payment method
            reports_no_payment = [r for r in all_reports if not r.get('PaymentType')]
            
            print(f"✓ Found {len(all_reports)} total approved reports")
            print(f"✓ Found {len(reports_no_payment)} reports WITHOUT payment method")
            
            if len(reports_no_payment) > 0:
                print("\n⚠️  ATTENTION: These reports need payment method configuration:")
                print("-" * 80)
                
                total_amount_pending = 0
                
                for report in reports_no_payment:
                    report_name = report.get('Name', 'Unnamed')
                    report_id = report.get('ID', 'Unknown')
                    amount = float(report.get('Total', 0))
                    owner_name = report.get('OwnerName', 'Unknown')
                    payment_status = report.get('PaymentStatusName', 'Unknown')
                    
                    total_amount_pending += amount
                    
                    print(f"\n  Report: {report_name}")
                    print(f"    ID: {report_id}")
                    print(f"    Owner: {owner_name}")
                    print(f"    Amount: ${amount:,.2f}")
                    print(f"    Payment Status: {payment_status}")
                    print(f"    ⚠️  Action Required: Configure payment method")
                
                print("\n" + "-" * 80)
                print(f"  Total Amount Pending Configuration: ${total_amount_pending:,.2f}")
                print(f"  Reports Needing Action: {len(reports_no_payment)}")
                
                coverage_pct = ((len(all_reports) - len(reports_no_payment)) / len(all_reports) * 100) if len(all_reports) > 0 else 0
                print(f"  Payment Method Coverage: {coverage_pct:.1f}%")
                
            else:
                print("\n✓ All approved reports have payment methods configured!")
                print("  Payment method coverage: 100%")
            
            # Store test result
            self.test_results.append({
                'test_name': 'Get approved reports without payment method',
                'endpoint': '/api/v3.0/expense/reports?approvalStatusCode=A_APPR&user=me (filtered for empty PaymentType)',
                'method': 'GET',
                'passed': True,
                'response': {
                    'total_approved_reports': len(all_reports),
                    'reports_without_payment_method': len(reports_no_payment),
                    'reports': reports_no_payment if reports_no_payment else [],
                    'note': 'Empty PaymentType filter applied client-side'
                },
                'error': None
            })
            
            print("\n✅ TEST PASSED - Successfully identified reports without payment methods")
            
        except Exception as e:
            print(f"\n❌ TEST FAILED: {str(e)}")
            self.test_results.append({
                'test_name': 'Get approved reports without payment method',
                'endpoint': '/api/v3.0/expense/reports?approvalStatusCode=A_APPR&user=me (filtered for empty PaymentType)',
                'method': 'GET',
                'passed': False,
                'response': None,
                'error': str(e)
            })
    
    def generate_report(self):
        """Generate test results report"""
        print("\n" + "=" * 80)
        print("TEST RESULTS SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for t in self.test_results if t['passed'])
        failed_tests = total_tests - passed_tests
        
        print(f"\nTotal Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        # Save results to JSON file
        results_dir = os.path.join(os.path.dirname(__file__), 'results')
        os.makedirs(results_dir, exist_ok=True)
        
        output = {
            'test_case': '033',
            'user_query': "What's the payment method for my approved reports?",
            'api_endpoint': 'GET /api/v3.0/expense/reports',
            'service': 'Expense Reports & Status',
            'tests': self.test_results,
            'summary': {
                'total': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'success_rate': f"{(passed_tests/total_tests*100):.1f}%",
                'timestamp': datetime.now().isoformat()
            }
        }
        
        output_file = os.path.join(results_dir, 'test_033_results.json')
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n✓ Results saved to: {output_file}")
        
        return output
    
    def run_all_tests(self):
        """Execute all tests in sequence"""
        try:
            self.setup()
            self.test_1_get_approved_reports_with_payment_types()
            self.test_2_get_approved_reports_by_specific_payment_method()
            self.test_3_get_approved_reports_without_payment_method()
            self.generate_report()
            
            print("\n" + "=" * 80)
            print("ALL TESTS COMPLETED")
            print("=" * 80)
            
        except Exception as e:
            print(f"\n❌ FATAL ERROR: {str(e)}")
            raise


if __name__ == "__main__":
    test_suite = TestApprovedReportsPaymentMethod()
    test_suite.run_all_tests()

