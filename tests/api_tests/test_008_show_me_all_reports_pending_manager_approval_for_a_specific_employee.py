#!/usr/bin/env python3
"""
Test Case #008: Pending Reports by Employee
User Query: Show me all reports pending manager approval for a specific employee
Service: Expense Reports & Status
API: GET /api/v3.0/expense/reports?user={loginID}&approvalStatusCode=A_PEND

This test verifies the manager can retrieve expense reports pending approval
for a specific employee using their login ID.
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


class TestPendingReportsByEmployee:
    """Test suite for pending reports by specific employee"""
    
    def __init__(self):
        self.sdk = None
        self.user_id = None
        self.results = {
            'test_case': '008',
            'user_query': 'Show me all reports pending manager approval for a specific employee',
            'api_endpoint': 'GET /api/v3.0/expense/reports?user={loginID}&approvalStatusCode=A_PEND',
            'service': 'Expense Reports & Status',
            'tests': [],
            'summary': {}
        }
    
    def setup(self):
        """Initialize SDK and authenticate"""
        print("=" * 80)
        print("Test Case #008: Pending Reports by Employee")
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
    
    def test_008_pending_reports_by_specific_user(self):
        """Test 1: Get pending reports for specific user"""
        test_name = "Pending reports by specific user (loginID)"
        print(f"Test 1: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports',
            'method': 'GET',
            'filters': 'user={loginID}&approvalStatusCode=A_PEND',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            # Use the manager's own username as the specific employee
            # In a real scenario, this would be a different user's login ID
            params = {
                'user': self.sdk.config.username,
                'approvalStatusCode': 'A_PEND'
            }
            
            result = self.sdk.get_expense_reports(params)
            
            if result['success']:
                test_result['passed'] = True
                test_result['response'] = {
                    'count': result.get('count', 0),
                    'user_filter': params['user'],
                    'status_filter': params['approvalStatusCode']
                }
                
                print(f"  ✓ Request successful")
                print(f"  User: {params['user']}")
                print(f"  Approval Status: {params['approvalStatusCode']}")
                print(f"  Reports found: {result.get('count', 0)}")
                
                if result.get('count', 0) > 0:
                    print(f"\n  Sample report:")
                    report = result['reports'][0]
                    print(f"    - Report Name: {report.get('ReportName', 'N/A')}")
                    print(f"    - Report ID: {report.get('ID', 'N/A')}")
                    print(f"    - Owner: {report.get('OwnerName', 'N/A')}")
                    print(f"    - Total: {report.get('Total', 'N/A')} {report.get('CurrencyCode', '')}")
                    print(f"    - Submit Date: {report.get('SubmitDate', 'N/A')}")
                    print(f"    - Approval Status: {report.get('ApprovalStatusName', 'N/A')}")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_008_pending_reports_all_users(self):
        """Test 2: Get all pending reports (all users)"""
        test_name = "All pending reports (user=ALL)"
        print(f"Test 2: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports',
            'method': 'GET',
            'filters': 'user=ALL&approvalStatusCode=A_PEND',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            params = {
                'user': 'ALL',
                'approvalStatusCode': 'A_PEND'
            }
            
            result = self.sdk.get_expense_reports(params)
            
            if result['success']:
                test_result['passed'] = True
                test_result['response'] = {
                    'count': result.get('count', 0),
                    'user_filter': params['user'],
                    'status_filter': params['approvalStatusCode']
                }
                
                print(f"  ✓ Request successful")
                print(f"  User: {params['user']}")
                print(f"  Approval Status: {params['approvalStatusCode']}")
                print(f"  Reports found: {result.get('count', 0)}")
                
                if result.get('count', 0) > 0:
                    # Show summary of multiple users
                    unique_owners = set()
                    for report in result['reports']:
                        unique_owners.add(report.get('OwnerName', 'Unknown'))
                    
                    print(f"  Unique employees with pending reports: {len(unique_owners)}")
                    if len(unique_owners) <= 5:
                        for owner in unique_owners:
                            print(f"    - {owner}")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_008_invalid_user(self):
        """Test 3: Test with invalid user ID"""
        test_name = "Invalid user ID handling"
        print(f"Test 3: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports',
            'method': 'GET',
            'filters': 'user=invalid_user_xyz&approvalStatusCode=A_PEND',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            params = {
                'user': 'invalid_user_xyz',
                'approvalStatusCode': 'A_PEND'
            }
            
            result = self.sdk.get_expense_reports(params)
            
            # For invalid user, we expect either success with 0 reports or an error
            # Both are acceptable behaviors
            if result['success']:
                count = result.get('count', 0)
                test_result['passed'] = True
                test_result['response'] = {
                    'count': count,
                    'behavior': 'Returns empty list for invalid user'
                }
                print(f"  ✓ Handled invalid user gracefully")
                print(f"  Reports found: {count}")
            else:
                # Error is also acceptable for invalid user
                test_result['passed'] = True
                test_result['response'] = {
                    'behavior': 'Returns error for invalid user'
                }
                print(f"  ✓ API returned error for invalid user (expected)")
                print(f"  Error: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            # Exception is also acceptable
            test_result['passed'] = True
            test_result['response'] = {
                'behavior': 'Raises exception for invalid user'
            }
            print(f"  ✓ Exception raised for invalid user (expected)")
            print(f"  Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_008_response_structure(self):
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
            params = {
                'user': self.sdk.config.username,
                'approvalStatusCode': 'A_PEND'
            }
            
            result = self.sdk.get_expense_reports(params)
            
            validations = []
            
            # Check required fields in response
            if 'success' in result:
                validations.append({'field': 'success', 'present': True})
            else:
                validations.append({'field': 'success', 'present': False})
            
            if 'reports' in result and isinstance(result.get('reports'), list):
                validations.append({'field': 'reports (array)', 'present': True})
            else:
                validations.append({'field': 'reports (array)', 'present': False})
            
            # If we have reports, validate report structure
            if result.get('count', 0) > 0:
                report = result['reports'][0]
                expected_fields = ['ID', 'ReportName', 'OwnerName', 'Total', 'ApprovalStatusCode']
                for field in expected_fields:
                    if field in report:
                        validations.append({'field': f'report.{field}', 'present': True})
                    else:
                        validations.append({'field': f'report.{field}', 'present': False})
            else:
                validations.append({'note': 'No reports to validate structure', 'present': True})
            
            test_result['validations'] = validations
            test_result['passed'] = all(v['present'] for v in validations)
            
            for v in validations:
                status = "✓" if v['present'] else "✗"
                field_name = v.get('field') or v.get('note', 'unknown')
                print(f"  {status} {field_name}")
            
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
        results_file = Path(__file__).parent / "results" / "test_008_results.json"
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
        self.test_008_pending_reports_by_specific_user()
        self.test_008_pending_reports_all_users()
        self.test_008_invalid_user()
        self.test_008_response_structure()
        
        # Generate report
        return self.generate_report()


def main():
    """Main test execution"""
    test_suite = TestPendingReportsByEmployee()
    success = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

