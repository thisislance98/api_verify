#!/usr/bin/env python3
"""
Test Case #019: Reports Eligible for Early Payment
User Query: Which reports are eligible for early payment?
Service: Expense Reports & Status
API: GET /api/v3.0/expense/reports

This test verifies retrieving expense reports that are eligible for early payment.
Reports must be:
- Approved (A_APPR)
- Not yet paid (P_NOTP)
- Approved at least 5 days ago
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from concur_expense_sdk import ConcurExpenseSDK, ConcurConfig
from tests.config import get_test_credentials
import json
from datetime import datetime, timedelta


class TestReportsEligibleForEarlyPayment:
    """Test suite for reports eligible for early payment endpoint"""
    
    def __init__(self):
        self.sdk = None
        self.results = {
            'test_case': '019',
            'user_query': 'Which reports are eligible for early payment?',
            'api_endpoint': 'GET /api/v3.0/expense/reports',
            'service': 'Expense Reports & Status',
            'tests': [],
            'summary': {}
        }
    
    def setup(self):
        """Initialize SDK and authenticate"""
        print("=" * 80)
        print("Test Case #019: Reports Eligible for Early Payment")
        print("=" * 80)
        print()
        
        print("Setup: Initializing SDK...")
        try:
            # Load credentials from config
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
            
            print()
            return True
            
        except Exception as e:
            print(f"  ✗ Setup failed: {str(e)}")
            return False
    
    def test_019_basic_retrieval(self):
        """Test 1: Basic retrieval of reports eligible for early payment"""
        test_name = "Basic retrieval of reports eligible for early payment (5+ days)"
        print(f"Test 1: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports?approvalStatusCode=A_APPR&paymentStatusCode=P_NOTP&approvedDateBefore={5daysAgo}',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.get_reports_eligible_for_early_payment()
            
            if result['success']:
                test_result['passed'] = True
                test_result['response'] = {
                    'count': result['count'],
                    'approval_status_code': result['approval_status_code'],
                    'payment_status_code': result['payment_status_code'],
                    'threshold_date': result['threshold_date'],
                    'days_threshold': result['days_threshold']
                }
                
                print(f"  ✓ Request successful")
                print(f"  Reports eligible for early payment: {result['count']}")
                print(f"  Approval status filter: {result['approval_status_code']} (Approved)")
                print(f"  Payment status filter: {result['payment_status_code']} (Not Paid)")
                print(f"  Threshold: Approved before {result['threshold_date']} ({result['days_threshold']}+ days ago)")
                
                if result['count'] > 0:
                    print(f"\n  Sample report eligible for early payment:")
                    report = result['reports'][0]
                    print(f"    - Name: {report['name']}")
                    print(f"    - Report ID: {report['id']}")
                    print(f"    - Owner: {report.get('owner_name', 'N/A')}")
                    print(f"    - Approval Status: {report.get('approval_status', 'N/A')}")
                    print(f"    - Payment Status: {report.get('payment_status_name', 'N/A')}")
                    print(f"    - Amount: {report.get('total', 'N/A')} {report.get('currency_code', '')}")
                    print(f"    - Approved Date: {report.get('approval_date', 'N/A')}")
                    if report.get('days_since_approval') is not None:
                        print(f"    - Days since approval: {report['days_since_approval']}")
                else:
                    print(f"  ℹ No reports are currently eligible for early payment")
                    print(f"  ℹ This may indicate:")
                    print(f"    - No approved reports older than 5 days")
                    print(f"    - All eligible reports have been paid")
                    print(f"    - Reports are in P_PROC (Processing Payment) status")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_019_custom_threshold(self):
        """Test 2: Retrieval with custom day threshold (10 days)"""
        test_name = "Retrieval with custom day threshold (10 days)"
        print(f"Test 2: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports?approvalStatusCode=A_APPR&paymentStatusCode=P_NOTP&approvedDateBefore={10daysAgo}',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.get_reports_eligible_for_early_payment(days_since_approval=10)
            
            if result['success']:
                test_result['passed'] = True
                test_result['response'] = {
                    'count': result['count'],
                    'days_threshold': result['days_threshold'],
                    'threshold_date': result['threshold_date']
                }
                
                print(f"  ✓ Request with custom threshold successful")
                print(f"  Reports found (10+ days old): {result['count']}")
                print(f"  Threshold: Approved before {result['threshold_date']}")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_019_with_limit(self):
        """Test 3: Retrieval with custom limit"""
        test_name = "Retrieval with custom limit"
        print(f"Test 3: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports?approvalStatusCode=A_APPR&paymentStatusCode=P_NOTP&approvedDateBefore={5daysAgo}&limit=10',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.get_reports_eligible_for_early_payment(limit=10)
            
            if result['success']:
                test_result['passed'] = True
                test_result['response'] = {
                    'count': result['count'],
                    'limit_applied': 10
                }
                
                print(f"  ✓ Request with custom limit successful")
                print(f"  Reports found (limit=10): {result['count']}")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_019_filter_validation(self):
        """Test 4: Validate that correct filters are applied"""
        test_name = "Filter validation (A_APPR, P_NOTP, date threshold)"
        print(f"Test 4: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'validations': [],
            'error': None
        }
        
        try:
            result = self.sdk.get_reports_eligible_for_early_payment()
            
            validations = []
            
            # Verify correct status codes are applied
            if result.get('approval_status_code') == 'A_APPR':
                validations.append({'check': 'Approval status = A_APPR', 'passed': True})
            else:
                validations.append({'check': 'Approval status = A_APPR', 'passed': False})
            
            if result.get('payment_status_code') == 'P_NOTP':
                validations.append({'check': 'Payment status = P_NOTP', 'passed': True})
            else:
                validations.append({'check': 'Payment status = P_NOTP', 'passed': False})
            
            # Verify threshold date is set
            if result.get('threshold_date'):
                validations.append({'check': 'Threshold date is set', 'passed': True})
            else:
                validations.append({'check': 'Threshold date is set', 'passed': False})
            
            # If we have reports, verify they match the filters
            if result.get('count', 0) > 0:
                report = result['reports'][0]
                
                # Check approval status code
                if report.get('approval_status_code') == 'A_APPR':
                    validations.append({'check': 'Report approval status = A_APPR', 'passed': True})
                else:
                    validations.append({'check': f"Report approval status = A_APPR (got {report.get('approval_status_code')})", 'passed': False})
                
                # Check payment status code
                if report.get('payment_status_code') == 'P_NOTP':
                    validations.append({'check': 'Report payment status = P_NOTP', 'passed': True})
                else:
                    validations.append({'check': f"Report payment status = P_NOTP (got {report.get('payment_status_code')})", 'passed': False})
                
                # Check that report was approved at least 5 days ago
                if report.get('days_since_approval') is not None and report.get('days_since_approval') >= 5:
                    validations.append({'check': f"Report approved 5+ days ago (actual: {report.get('days_since_approval')} days)", 'passed': True})
                elif report.get('days_since_approval') is not None:
                    validations.append({'check': f"Report approved 5+ days ago (actual: {report.get('days_since_approval')} days)", 'passed': False})
            
            test_result['validations'] = validations
            test_result['passed'] = all(v['passed'] for v in validations)
            
            for v in validations:
                status = "✓" if v['passed'] else "✗"
                print(f"  {status} {v['check']}")
            
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_019_response_structure(self):
        """Test 5: Validate response structure"""
        test_name = "Response structure validation"
        print(f"Test 5: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'validations': [],
            'error': None
        }
        
        try:
            result = self.sdk.get_reports_eligible_for_early_payment()
            
            validations = []
            
            # Check required fields in response
            required_fields = [
                'success', 'reports', 'count', 'approval_status_code',
                'payment_status_code', 'threshold_date', 'days_threshold', 'message'
            ]
            
            for field in required_fields:
                if field in result:
                    validations.append({'field': field, 'present': True})
                else:
                    validations.append({'field': field, 'present': False})
            
            # If we have reports, validate report structure
            if result.get('count', 0) > 0:
                report = result['reports'][0]
                report_fields = ['id', 'name', 'total', 'currency_code', 
                                'approval_status', 'payment_status_name', 
                                'approval_date', 'days_since_approval']
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
        results_file = Path(__file__).parent / "results" / "test_019_results.json"
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
        self.test_019_basic_retrieval()
        self.test_019_custom_threshold()
        self.test_019_with_limit()
        self.test_019_filter_validation()
        self.test_019_response_structure()
        
        # Generate report
        return self.generate_report()


def main():
    """Main test execution"""
    test_suite = TestReportsEligibleForEarlyPayment()
    success = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

