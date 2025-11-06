#!/usr/bin/env python3
"""
Test Case #004: Reports Sent Back to Employees
User Query: Show me expense reports that were sent back to employees
Service: Expense Reports & Status
API: GET /api/v3.0/expense/reports

This test verifies retrieving expense reports that have been returned
to employees for correction using approval status code A_RESU.
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


class TestReportsSentBackToEmployees:
    """Test suite for reports sent back to employees endpoint"""
    
    def __init__(self):
        self.sdk = None
        self.results = {
            'test_case': '004',
            'user_query': 'Show me expense reports that were sent back to employees',
            'api_endpoint': 'GET /api/v3.0/expense/reports',
            'service': 'Expense Reports & Status',
            'tests': [],
            'summary': {}
        }
    
    def setup(self):
        """Initialize SDK and authenticate"""
        print("=" * 80)
        print("Test Case #004: Reports Sent Back to Employees")
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
    
    def test_004_basic_retrieval(self):
        """Test 1: Basic retrieval of reports sent back to employees"""
        test_name = "Basic retrieval of reports with A_RESU status"
        print(f"Test 1: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports?approvalStatusCode=A_RESU',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.get_reports_sent_back_to_employees()
            
            if result['success']:
                test_result['passed'] = True
                test_result['response'] = {
                    'count': result['count'],
                    'approval_status': result['approval_status']
                }
                
                print(f"  ✓ Request successful")
                print(f"  Reports sent back: {result['count']}")
                print(f"  Approval status filter: {result['approval_status']}")
                
                if result['count'] > 0:
                    print(f"\n  Sample report sent back:")
                    report = result['reports'][0]
                    print(f"    - Name: {report['name']}")
                    print(f"    - Report ID: {report['id']}")
                    print(f"    - Owner: {report.get('owner_name', 'N/A')}")
                    print(f"    - Status: {report.get('approval_status', 'N/A')}")
                    print(f"    - Last Modified: {report.get('last_modified_date', 'N/A')}")
                    if report.get('days_since_modified') is not None:
                        print(f"    - Days since returned: {report['days_since_modified']}")
                    if report.get('last_comment'):
                        print(f"    - Last Comment: {report['last_comment'][:100]}...")
                else:
                    print(f"  ℹ No reports are currently sent back to employees")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_004_with_limit(self):
        """Test 2: Retrieval with custom limit"""
        test_name = "Custom limit parameter"
        print(f"Test 2: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports?approvalStatusCode=A_RESU&limit=10',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.get_reports_sent_back_to_employees(limit=10)
            
            if result['success']:
                test_result['passed'] = True
                test_result['response'] = {
                    'count': result['count'],
                    'limit_requested': 10
                }
                
                print(f"  ✓ Request with limit=10 successful")
                print(f"  Reports returned: {result['count']}")
                
                # Verify limit is respected
                if result['count'] <= 10:
                    print(f"  ✓ Limit parameter respected")
                else:
                    print(f"  ⚠ Warning: Returned more than requested limit")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_004_response_structure(self):
        """Test 3: Validate response structure"""
        test_name = "Response structure validation"
        print(f"Test 3: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'validations': [],
            'error': None
        }
        
        try:
            result = self.sdk.get_reports_sent_back_to_employees()
            
            validations = []
            
            # Check required fields in response
            required_fields = [
                'success', 'reports', 'count', 
                'approval_status', 'message'
            ]
            
            for field in required_fields:
                if field in result:
                    validations.append({'field': field, 'present': True})
                else:
                    validations.append({'field': field, 'present': False})
            
            # Verify approval_status is A_RESU
            if result.get('approval_status') == 'A_RESU':
                validations.append({'field': 'approval_status == A_RESU', 'present': True})
            else:
                validations.append({'field': 'approval_status == A_RESU', 'present': False})
            
            # If we have reports, validate report structure
            if result.get('count', 0) > 0:
                report = result['reports'][0]
                report_fields = ['id', 'name', 'owner_name', 'approval_status', 'last_modified_date']
                for field in report_fields:
                    if field in report and report[field] is not None:
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
    
    def test_004_compare_with_raw_api(self):
        """Test 4: Compare SDK method with raw API call"""
        test_name = "Comparison with raw API call"
        print(f"Test 4: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'comparison': {},
            'error': None
        }
        
        try:
            # Get results using SDK method
            sdk_result = self.sdk.get_reports_sent_back_to_employees(limit=10)
            
            # Make raw API call
            endpoint = "api/v3.0/expense/reports"
            params = {
                'approvalStatusCode': 'A_RESU',
                'limit': 10,
                'user': 'ALL'
            }
            raw_response = self.sdk._make_request("GET", endpoint, params=params)
            raw_data = raw_response.json()
            raw_count = len(raw_data.get('Items', []))
            
            # Compare results
            sdk_count = sdk_result.get('count', 0)
            
            test_result['comparison'] = {
                'sdk_count': sdk_count,
                'raw_count': raw_count,
                'match': sdk_count == raw_count
            }
            
            test_result['passed'] = sdk_count == raw_count
            
            print(f"  SDK method count: {sdk_count}")
            print(f"  Raw API count: {raw_count}")
            
            if sdk_count == raw_count:
                print(f"  ✓ Results match")
            else:
                print(f"  ✗ Results do not match")
                
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
        results_file = Path(__file__).parent / "results" / "test_004_results.json"
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
        self.test_004_basic_retrieval()
        self.test_004_with_limit()
        self.test_004_response_structure()
        self.test_004_compare_with_raw_api()
        
        # Generate report
        return self.generate_report()


def main():
    """Main test execution"""
    test_suite = TestReportsSentBackToEmployees()
    success = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

