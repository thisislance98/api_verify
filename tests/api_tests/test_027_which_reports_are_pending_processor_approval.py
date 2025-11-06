#!/usr/bin/env python3
"""
Test Case #027: Reports Pending Processor Approval
User Query: Which reports are pending processor approval?
Service: Expense Reports & Status
API: GET /api/v3.0/expense/reports
CSV Row: 27

This test verifies the retrieval of expense reports that have been approved
and are waiting for the processor to extract and process them for payment.
These reports have approvalStatusCode=A_APPR and paymentStatusCode=P_NOTP.

This differs from Test 010 in that:
- Test 010: Focuses on "not extracted" reports (includes hasException=N filter)
- Test 024: Focuses on processor's work queue (all approved reports awaiting payment processing)
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from concur_expense_sdk import ConcurExpenseSDK, ConcurConfig
from tests.config import get_test_credentials
import json
from datetime import datetime


class TestReportsPendingProcessorApproval:
    """Test suite for reports pending processor approval endpoint"""
    
    def __init__(self):
        self.sdk = None
        self.user_id = None
        self.results = {
            'test_case': '027',
            'user_query': "Which reports are pending processor approval?",
            'api_endpoint': 'GET /api/v3.0/expense/reports',
            'service': 'Expense Reports & Status',
            'csv_row': 27,
            'tests': [],
            'summary': {}
        }
    
    def setup(self):
        """Initialize SDK and authenticate"""
        print("=" * 80)
        print("Test Case #027: Reports Pending Processor Approval")
        print("=" * 80)
        print()
        
        print("Setup: Initializing SDK...")
        try:
            # Load credentials from config (using manager_approver to see more reports)
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
            print(f"  Base URL: {self.sdk.config.base_url}")
            print(f"  Username: {self.sdk.config.username}")
            print(f"  Role: {creds['role']}")
            
            # Test connection
            result = self.sdk.test_connection()
            if result['success']:
                print(f"  ✓ Authentication successful")
            else:
                raise Exception(f"Authentication failed: {result['message']}")
            
            # Get user ID
            self.user_id = self.sdk.get_user_id()
            if self.user_id:
                print(f"  ✓ User ID: {self.user_id}")
            else:
                raise Exception("Could not retrieve user ID")
            
            print()
            return True
            
        except Exception as e:
            print(f"  ✗ Setup failed: {str(e)}")
            return False
    
    def test_027_basic_retrieval(self):
        """Test 1: Basic retrieval of reports pending processor approval"""
        test_name = "Basic retrieval - approved reports awaiting payment processing"
        print(f"Test 1: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports',
            'method': 'GET',
            'params': {
                'approvalStatusCode': 'A_APPR',
                'paymentStatusCode': 'P_NOTP',
                'user': 'ALL'
            },
            'passed': False,
            'response': None,
            'error': None,
            'test_data_available': False
        }
        
        try:
            # Get approved reports that haven't been paid yet
            result = self.sdk.get_expense_reports({
                'approvalStatusCode': 'A_APPR',
                'paymentStatusCode': 'P_NOTP',
                'user': 'ALL'
            })
            
            if result['success']:
                count = result['count']
                test_result['response'] = {
                    'count': count,
                    'params': result['params']
                }
                test_result['test_data_available'] = count > 0
                
                print(f"  ✓ Request successful")
                print(f"  Retrieved {count} reports pending processor approval")
                
                if count > 0:
                    test_result['passed'] = True
                    
                    # Calculate total amount pending processing
                    total_amount = sum(float(report.get('Total', 0)) for report in result['reports'])
                    
                    print(f"  Total Amount Pending: ${total_amount:,.2f}")
                    print(f"\n  Sample report details:")
                    report = result['reports'][0]
                    print(f"    - Report Name: {report.get('ReportName', report.get('name', 'N/A'))}")
                    print(f"    - Report ID: {report.get('ID', report.get('id', 'N/A'))}")
                    print(f"    - Owner: {report.get('OwnerName', 'N/A')}")
                    print(f"    - Total: ${float(report.get('Total', 0)):,.2f} {report.get('CurrencyCode', '')}")
                    print(f"    - Approval Status: {report.get('ApprovalStatusName', 'N/A')} ({report.get('ApprovalStatusCode', 'N/A')})")
                    print(f"    - Payment Status: {report.get('PaymentStatusName', 'N/A')} ({report.get('PaymentStatusCode', 'N/A')})")
                    print(f"    - Submit Date: {report.get('SubmitDate', 'N/A')}")
                    print(f"    - Approval Date: {report.get('ApprovalDate', 'N/A')}")
                    
                    # Show all reports if there aren't too many
                    if count <= 10:
                        print(f"\n  All {count} reports in processor queue:")
                        for i, report in enumerate(result['reports'], 1):
                            print(f"    {i}. {report.get('ReportName', 'N/A')} - ${float(report.get('Total', 0)):,.2f} - Owner: {report.get('OwnerName', 'N/A')}")
                else:
                    # No test data available - provide guidance
                    test_result['passed'] = False
                    test_result['error'] = 'NO_TEST_DATA'
                    print(f"  ⚠ No test data available")
                    print(f"\n  Test Requirements:")
                    print(f"    This test requires reports with:")
                    print(f"    1. Approval Status: A_APPR (Approved)")
                    print(f"    2. Payment Status: P_NOTP (Not Paid - awaiting processor)")
                    print(f"\n  To create test data:")
                    print(f"    1. Submit an expense report via Concur UI")
                    print(f"    2. Approve it (as manager) to move it to A_APPR status")
                    print(f"    3. Do NOT process it for payment yet")
                    print(f"\n  Checking for pending reports that can be approved:")
                    try:
                        pending = self.sdk.get_expense_reports({'approvalStatusCode': 'A_PEND', 'user': 'ALL', 'limit': 5})
                        if pending['success'] and pending.get('count', 0) > 0:
                            print(f"    Found {pending['count']} pending reports that could be approved:")
                            for i, report in enumerate(pending['reports'][:5]):
                                print(f"      {i+1}. {report.get('ReportName', 'N/A')} - ${float(report.get('Total', 0)):,.2f} (ID: {report.get('ID', 'N/A')})")
                        else:
                            print(f"    No pending reports found")
                    except Exception as check_err:
                        print(f"    Error checking pending reports: {check_err}")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_027_approval_status_verification(self):
        """Test 2: Verify all returned reports have approved status"""
        test_name = "Approval status verification (A_APPR)"
        print(f"Test 2: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'validations': [],
            'error': None
        }
        
        try:
            result = self.sdk.get_expense_reports({
                'approvalStatusCode': 'A_APPR',
                'paymentStatusCode': 'P_NOTP',
                'user': 'ALL'
            })
            
            if result['success'] and result['count'] > 0:
                validations = []
                all_valid = True
                
                # Check that all returned reports have approved status
                for report in result['reports']:
                    status_code = report.get('ApprovalStatusCode', '').upper()
                    is_valid = status_code == 'A_APPR'
                    
                    if not is_valid:
                        all_valid = False
                        validations.append({
                            'report_id': report.get('ID'),
                            'report_name': report.get('ReportName'),
                            'status_code': status_code,
                            'valid': False
                        })
                        print(f"  ✗ Invalid approval status: {status_code} for report {report.get('ReportName')}")
                
                if all_valid:
                    test_result['passed'] = True
                    test_result['response'] = {
                        'all_reports_valid': True,
                        'total_reports_checked': len(result['reports'])
                    }
                    print(f"  ✓ All reports have approved status (A_APPR)")
                    print(f"  Total reports checked: {len(result['reports'])}")
                else:
                    test_result['error'] = f"Found {len(validations)} reports with invalid approval status"
                    test_result['validations'] = validations
            elif result['success'] and result['count'] == 0:
                # No data but API call succeeded - pass the validation
                test_result['passed'] = True
                test_result['response'] = {'no_data': True, 'message': 'No reports to validate'}
                print(f"  ✓ No reports to validate (test passes)")
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_027_payment_status_verification(self):
        """Test 3: Verify all reports have 'Not Paid' payment status"""
        test_name = "Payment status verification (P_NOTP)"
        print(f"Test 3: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'validations': [],
            'error': None
        }
        
        try:
            result = self.sdk.get_expense_reports({
                'approvalStatusCode': 'A_APPR',
                'paymentStatusCode': 'P_NOTP',
                'user': 'ALL'
            })
            
            if result['success'] and result['count'] > 0:
                validations = []
                all_valid = True
                
                # Check that all returned reports have not paid status
                for report in result['reports']:
                    payment_code = report.get('PaymentStatusCode', '').upper()
                    is_valid = payment_code == 'P_NOTP'
                    
                    if not is_valid:
                        all_valid = False
                        validations.append({
                            'report_id': report.get('ID'),
                            'report_name': report.get('ReportName'),
                            'payment_code': payment_code,
                            'valid': False
                        })
                        print(f"  ✗ Invalid payment status: {payment_code} for report {report.get('ReportName')}")
                
                if all_valid:
                    test_result['passed'] = True
                    test_result['response'] = {
                        'all_reports_valid': True,
                        'total_reports_checked': len(result['reports'])
                    }
                    print(f"  ✓ All reports have 'Not Paid' status (P_NOTP)")
                    print(f"  Total reports checked: {len(result['reports'])}")
                else:
                    test_result['error'] = f"Found {len(validations)} reports with invalid payment status"
                    test_result['validations'] = validations
            elif result['success'] and result['count'] == 0:
                # No data but API call succeeded - pass the validation
                test_result['passed'] = True
                test_result['response'] = {'no_data': True, 'message': 'No reports to validate'}
                print(f"  ✓ No reports to validate (test passes)")
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_027_processor_workflow_readiness(self):
        """Test 4: Verify reports are ready for processor workflow"""
        test_name = "Processor workflow readiness verification"
        print(f"Test 4: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.get_expense_reports({
                'approvalStatusCode': 'A_APPR',
                'paymentStatusCode': 'P_NOTP',
                'user': 'ALL'
            })
            
            if result['success']:
                if result['count'] > 0:
                    # Check that reports are in correct state for processor
                    ready_for_processor = []
                    not_ready = []
                    
                    for report in result['reports']:
                        approval_status = report.get('ApprovalStatusCode', '').upper()
                        payment_status = report.get('PaymentStatusCode', '').upper()
                        
                        # Ready if: Approved (A_APPR) AND Not Paid (P_NOTP)
                        if approval_status == 'A_APPR' and payment_status == 'P_NOTP':
                            ready_for_processor.append(report)
                        else:
                            not_ready.append({
                                'report_id': report.get('ID'),
                                'report_name': report.get('ReportName'),
                                'approval_status': approval_status,
                                'payment_status': payment_status
                            })
                    
                    if len(ready_for_processor) == result['count']:
                        test_result['passed'] = True
                        test_result['response'] = {
                            'ready_for_processor': len(ready_for_processor),
                            'total_reports': result['count']
                        }
                        print(f"  ✓ All {len(ready_for_processor)} reports are ready for processor workflow")
                        print(f"    - Status: Approved (A_APPR)")
                        print(f"    - Payment: Not Paid (P_NOTP)")
                        print(f"    - Action: Ready for extraction and payment processing")
                    else:
                        test_result['error'] = f"Found {len(not_ready)} reports not ready for processor"
                        test_result['response'] = {'not_ready': not_ready}
                        print(f"  ✗ {len(not_ready)} reports are not in correct state")
                        for r in not_ready:
                            print(f"    - {r['report_name']}: {r['approval_status']} / {r['payment_status']}")
                else:
                    # No data but API call succeeded - pass the validation
                    test_result['passed'] = True
                    test_result['response'] = {'no_data': True, 'message': 'No reports to validate'}
                    print(f"  ✓ No reports to validate (test passes)")
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_027_payment_summary_by_owner(self):
        """Test 5: Generate payment summary grouped by report owner"""
        test_name = "Payment summary by report owner"
        print(f"Test 5: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.get_expense_reports({
                'approvalStatusCode': 'A_APPR',
                'paymentStatusCode': 'P_NOTP',
                'user': 'ALL'
            })
            
            if result['success']:
                if result['count'] > 0:
                    # Group reports by owner
                    owner_summary = {}
                    
                    for report in result['reports']:
                        owner = report.get('OwnerName', 'Unknown')
                        total = float(report.get('Total', 0))
                        
                        if owner not in owner_summary:
                            owner_summary[owner] = {
                                'report_count': 0,
                                'total_amount': 0
                            }
                        
                        owner_summary[owner]['report_count'] += 1
                        owner_summary[owner]['total_amount'] += total
                    
                    test_result['passed'] = True
                    test_result['response'] = {
                        'owner_count': len(owner_summary),
                        'owner_summary': owner_summary
                    }
                    
                    print(f"  ✓ Payment summary generated for {len(owner_summary)} report owners")
                    print(f"\n  Summary by Owner:")
                    for owner, summary in sorted(owner_summary.items(), key=lambda x: x[1]['total_amount'], reverse=True):
                        print(f"    - {owner}:")
                        print(f"      Reports: {summary['report_count']}")
                        print(f"      Total: ${summary['total_amount']:,.2f}")
                else:
                    # No data but API call succeeded - pass the validation
                    test_result['passed'] = True
                    test_result['response'] = {'no_data': True, 'message': 'No reports to summarize'}
                    print(f"  ✓ No reports to summarize (test passes)")
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_027_response_structure(self):
        """Test 6: Validate response structure"""
        test_name = "Response structure validation"
        print(f"Test 6: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'validations': [],
            'error': None
        }
        
        try:
            result = self.sdk.get_expense_reports({
                'approvalStatusCode': 'A_APPR',
                'paymentStatusCode': 'P_NOTP',
                'user': 'ALL'
            })
            
            validations = []
            
            # Check required fields in response
            required_fields = ['success', 'reports', 'count', 'params', 'message']
            
            for field in required_fields:
                if field in result:
                    validations.append({'field': field, 'present': True})
                else:
                    validations.append({'field': field, 'present': False})
            
            # Validate data types
            if 'reports' in result and isinstance(result['reports'], list):
                validations.append({'field': 'reports (array)', 'present': True})
            else:
                validations.append({'field': 'reports (array)', 'present': False})
            
            if 'count' in result and isinstance(result['count'], int):
                validations.append({'field': 'count (integer)', 'present': True})
            else:
                validations.append({'field': 'count (integer)', 'present': False})
            
            # If we have reports, validate report structure
            if result.get('count', 0) > 0:
                report = result['reports'][0]
                report_fields = [
                    'ID', 'ReportName', 'OwnerName', 'Total', 
                    'CurrencyCode', 'ApprovalStatusCode', 'ApprovalStatusName',
                    'PaymentStatusCode', 'PaymentStatusName'
                ]
                for field in report_fields:
                    if field in report:
                        validations.append({'field': f'report.{field}', 'present': True})
                    else:
                        validations.append({'field': f'report.{field}', 'present': False})
            
            test_result['validations'] = validations
            test_result['passed'] = all(v['present'] for v in validations)
            
            for v in validations:
                status = "✓" if v['present'] else "✗"
                print(f"  {status} {v['field']}")
            
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def generate_report(self):
        """Generate test report"""
        print("=" * 80)
        print("Test Summary")
        print("=" * 80)
        
        total_tests = len(self.results['tests'])
        passed_tests = sum(1 for t in self.results['tests'] if t.get('passed', False))
        failed_tests = total_tests - passed_tests
        
        self.results['summary'] = {
            'total': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'success_rate': f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%",
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {self.results['summary']['success_rate']}")
        print()
        
        # Show failed tests if any
        if failed_tests > 0:
            print("Failed Tests:")
            for test in self.results['tests']:
                if not test.get('passed', False):
                    print(f"  ✗ {test['test_name']}")
                    if test.get('error'):
                        print(f"    Error: {test['error']}")
            print()
        
        # Save results to JSON
        results_file = Path(__file__).parent / "results" / "test_027_results.json"
        results_file.parent.mkdir(exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"Results saved to: {results_file}")
        print("=" * 80)
        
        return passed_tests == total_tests
    
    def run_all_tests(self):
        """Run all tests"""
        if not self.setup():
            return False
        
        # Run tests
        self.test_027_basic_retrieval()
        self.test_027_approval_status_verification()
        self.test_027_payment_status_verification()
        self.test_027_processor_workflow_readiness()
        self.test_027_payment_summary_by_owner()
        self.test_027_response_structure()
        
        # Generate report
        return self.generate_report()


def main():
    """Main test execution"""
    test_suite = TestReportsPendingProcessorApproval()
    success = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

