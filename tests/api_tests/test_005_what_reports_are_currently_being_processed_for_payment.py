#!/usr/bin/env python3
"""
Test Case #005: Reports Being Processed for Payment
User Query: What reports are currently being processed for payment?
Service: Expense Reports & Status
API: GET /api/v3.0/expense/reports

This test verifies retrieving expense reports that are currently being processed for payment
using payment status code P_PROC.
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


class TestReportsBeingProcessedForPayment:
    """Test suite for reports being processed for payment endpoint"""
    
    def __init__(self):
        self.sdk = None
        self.results = {
            'test_case': '005',
            'user_query': 'What reports are currently being processed for payment?',
            'api_endpoint': 'GET /api/v3.0/expense/reports',
            'service': 'Expense Reports & Status',
            'tests': [],
            'summary': {}
        }
    
    def setup(self):
        """Initialize SDK and authenticate"""
        print("=" * 80)
        print("Test Case #005: Reports Being Processed for Payment")
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
    
    def test_005_basic_payment_processing_retrieval(self):
        """Test 1: Basic retrieval of reports being processed for payment"""
        test_name = "Basic payment processing reports retrieval"
        print(f"Test 1: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports?paymentStatusCode=P_PROC',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.get_reports_being_processed_for_payment()
            
            if result['success']:
                test_result['passed'] = True
                test_result['response'] = {
                    'count': result['count'],
                    'payment_status_code': result.get('payment_status_code', 'N/A')
                }
                
                print(f"  ✓ Request successful")
                print(f"  Reports being processed for payment: {result['count']}")
                print(f"  Payment status filter: {result.get('payment_status_code', 'N/A')}")
                
                if result['count'] > 0:
                    print(f"\n  Sample report being processed:")
                    report = result['reports'][0]
                    print(f"    - Name: {report['name']}")
                    print(f"    - Report ID: {report['id']}")
                    print(f"    - Owner: {report.get('owner_name', 'N/A')}")
                    print(f"    - Total: {report.get('total', 'N/A')} {report.get('currency_code', '')}")
                    print(f"    - Payment Status: {report.get('payment_status_name', 'N/A')}")
                    print(f"    - Approval Status: {report.get('approval_status', 'N/A')}")
                    if report.get('approval_date'):
                        print(f"    - Approved: {report['approval_date']}")
                    if report.get('days_since_approval') is not None:
                        print(f"    - Days in processing: {report['days_since_approval']}")
                else:
                    print(f"  ℹ No reports are currently being processed for payment")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_005_limited_results(self):
        """Test 2: Test with limited result set"""
        test_name = "Limited results retrieval (10 reports)"
        print(f"Test 2: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports?paymentStatusCode=P_PROC&limit=10',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.get_reports_being_processed_for_payment(limit=10)
            
            if result['success']:
                test_result['passed'] = True
                test_result['response'] = {
                    'count': result['count'],
                    'limit_applied': 10
                }
                
                print(f"  ✓ Request with limit successful")
                print(f"  Reports returned: {result['count']}")
                print(f"  Limit: 10")
                
                if result['count'] <= 10:
                    print(f"  ✓ Result count within limit")
                else:
                    print(f"  ⚠ Result count exceeds limit (API may have different limits)")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_005_user_filter(self):
        """Test 3: Test with user filter"""
        test_name = "User filter (ALL users)"
        print(f"Test 3: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports?paymentStatusCode=P_PROC&user=ALL',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.get_reports_being_processed_for_payment(user='ALL')
            
            if result['success']:
                test_result['passed'] = True
                test_result['response'] = {
                    'count': result['count'],
                    'user_filter': 'ALL'
                }
                
                print(f"  ✓ Request with user filter successful")
                print(f"  Reports found (all users): {result['count']}")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_005_response_structure(self):
        """Test 4: Validate response structure"""
        test_name = "Response structure validation"
        print(f"Test 4: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'validations': [],
            'error': None
        }
        
        try:
            result = self.sdk.get_reports_being_processed_for_payment()
            
            validations = []
            
            # Check required fields in response
            required_fields = [
                'success', 'reports', 'count', 'payment_status_code', 'message'
            ]
            
            for field in required_fields:
                if field in result:
                    validations.append({'field': field, 'present': True})
                else:
                    validations.append({'field': field, 'present': False})
            
            # If we have reports, validate report structure
            if result.get('count', 0) > 0:
                report = result['reports'][0]
                report_fields = [
                    'id', 'name', 'total', 'currency_code', 
                    'payment_status_name', 'payment_status_code', 'approval_status'
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
    
    def test_005_payment_status_data(self):
        """Test 5: Verify payment status data in response"""
        test_name = "Payment status data verification"
        print(f"Test 5: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'validations': [],
            'error': None
        }
        
        try:
            result = self.sdk.get_reports_being_processed_for_payment()
            
            if result['success']:
                validations = []
                
                # Check that payment_status_code is P_PROC
                payment_status_correct = result.get('payment_status_code') == 'P_PROC'
                validations.append({
                    'check': 'payment_status_code == P_PROC',
                    'passed': payment_status_correct
                })
                
                # If reports exist, verify they have payment status data
                if result.get('count', 0) > 0:
                    report = result['reports'][0]
                    
                    # Check payment_status_code
                    has_payment_code = 'payment_status_code' in report
                    validations.append({
                        'check': 'report has payment_status_code',
                        'passed': has_payment_code
                    })
                    
                    # Check payment_status_name
                    has_payment_name = 'payment_status_name' in report
                    validations.append({
                        'check': 'report has payment_status_name',
                        'passed': has_payment_name
                    })
                    
                    # Check days_since_approval exists
                    has_days_since = 'days_since_approval' in report
                    validations.append({
                        'check': 'report has days_since_approval',
                        'passed': has_days_since
                    })
                
                test_result['validations'] = validations
                test_result['passed'] = all(v['passed'] for v in validations)
                
                for v in validations:
                    status = "✓" if v['passed'] else "✗"
                    print(f"  {status} {v['check']}")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
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
        results_file = Path(__file__).parent / "results" / "test_005_results.json"
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
        self.test_005_basic_payment_processing_retrieval()
        self.test_005_limited_results()
        self.test_005_user_filter()
        self.test_005_response_structure()
        self.test_005_payment_status_data()
        
        # Generate report
        return self.generate_report()


def main():
    """Main test execution"""
    test_suite = TestReportsBeingProcessedForPayment()
    success = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

