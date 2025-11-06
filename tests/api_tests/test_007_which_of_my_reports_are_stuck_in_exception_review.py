#!/usr/bin/env python3
"""
Test Case #007: Reports in Exception Review
User Query: Which of my reports are stuck in exception review?
Service: Expense Reports & Status
API: GET /api/v3.0/expense/reports?approvalStatusCode=A_AAFH

This test verifies the ability to retrieve expense reports that are stuck in
exception review (awaiting audit/finance handler review).
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


class TestReportsInExceptionReview:
    """Test suite for reports in exception review endpoint"""
    
    def __init__(self):
        self.sdk = None
        self.user_id = None
        self.results = {
            'test_case': '007',
            'user_query': 'Which of my reports are stuck in exception review?',
            'api_endpoint': 'GET /api/v3.0/expense/reports?approvalStatusCode=A_AAFH',
            'service': 'Expense Reports & Status',
            'tests': [],
            'summary': {}
        }
    
    def setup(self):
        """Initialize SDK and authenticate"""
        print("=" * 80)
        print("Test Case #007: Reports in Exception Review")
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
    
    def test_007_basic_retrieval(self):
        """Test 1: Basic retrieval of reports in exception review"""
        test_name = "Basic retrieval with A_AAFH filter"
        print(f"Test 1: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports?approvalStatusCode=A_AAFH',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.get_reports_in_exception_review()
            
            if result['success']:
                test_result['passed'] = True
                test_result['response'] = {
                    'count': result['count'],
                    'approval_status': result.get('approval_status'),
                    'message': result.get('message')
                }
                
                print(f"  ✓ Request successful")
                print(f"  Reports in exception review: {result['count']}")
                
                if result['count'] > 0:
                    print(f"\n  Sample report:")
                    report = result['reports'][0]
                    print(f"    - Name: {report['name']}")
                    print(f"    - Report ID: {report['id']}")
                    print(f"    - Owner: {report.get('owner_name', 'N/A')}")
                    print(f"    - Status: {report.get('approval_status', 'N/A')}")
                    print(f"    - Amount: {report.get('total', 'N/A')} {report.get('currency_code', '')}")
                    if report.get('days_in_exception') is not None:
                        print(f"    - Days in exception: {report['days_in_exception']}")
                    if report.get('has_exception'):
                        print(f"    - Has exception: Yes")
                        if report.get('exception_code'):
                            print(f"    - Exception code: {report['exception_code']}")
                else:
                    print(f"\n  Note: No reports found in exception review (A_AAFH status)")
                    print(f"  This is normal if no reports are currently stuck in exception review")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_007_with_user_filter(self):
        """Test 2: Retrieval with user='ALL' filter"""
        test_name = "Retrieval with user='ALL' filter"
        print(f"Test 2: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': "/api/v3.0/expense/reports?approvalStatusCode=A_AAFH&user=ALL",
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.get_reports_in_exception_review(user='ALL')
            
            if result['success']:
                test_result['passed'] = True
                test_result['response'] = {
                    'count': result['count'],
                    'approval_status': result.get('approval_status'),
                    'user_filter': 'ALL'
                }
                
                print(f"  ✓ Request with user=ALL filter successful")
                print(f"  Reports in exception review (all users): {result['count']}")
                
                # Show breakdown by owner if we have multiple reports
                if result['count'] > 1:
                    owners = {}
                    for report in result['reports']:
                        owner = report.get('owner_name', 'Unknown')
                        owners[owner] = owners.get(owner, 0) + 1
                    
                    print(f"\n  Reports by owner:")
                    for owner, count in sorted(owners.items()):
                        print(f"    - {owner}: {count} report(s)")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_007_with_limit(self):
        """Test 3: Retrieval with limit parameter"""
        test_name = "Retrieval with limit parameter"
        print(f"Test 3: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports?approvalStatusCode=A_AAFH&limit=10',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.get_reports_in_exception_review(limit=10)
            
            if result['success']:
                test_result['passed'] = True
                test_result['response'] = {
                    'count': result['count'],
                    'limit_applied': 10,
                    'limit_respected': result['count'] <= 10
                }
                
                print(f"  ✓ Request with limit=10 successful")
                print(f"  Reports returned: {result['count']}")
                print(f"  Limit respected: {result['count'] <= 10}")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_007_response_structure(self):
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
            result = self.sdk.get_reports_in_exception_review()
            
            validations = []
            
            # Check required fields in response
            if 'success' in result:
                validations.append({'field': 'success', 'present': True})
            else:
                validations.append({'field': 'success', 'present': False})
            
            if 'reports' in result and isinstance(result['reports'], list):
                validations.append({'field': 'reports (array)', 'present': True})
            else:
                validations.append({'field': 'reports (array)', 'present': False})
            
            if 'count' in result:
                validations.append({'field': 'count', 'present': True})
            else:
                validations.append({'field': 'count', 'present': False})
            
            if 'approval_status' in result and result['approval_status'] == 'A_AAFH':
                validations.append({'field': 'approval_status (A_AAFH)', 'present': True})
            else:
                validations.append({'field': 'approval_status (A_AAFH)', 'present': False})
            
            # If we have reports, validate report structure
            if result.get('count', 0) > 0:
                report = result['reports'][0]
                required_fields = ['id', 'name', 'approval_status']
                for field in required_fields:
                    if field in report and report[field] is not None:
                        validations.append({'field': f'report.{field}', 'present': True})
                    else:
                        validations.append({'field': f'report.{field}', 'present': False})
                
                # Check exception-specific fields
                exception_fields = ['has_exception', 'exception_code', 'days_in_exception']
                for field in exception_fields:
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
        results_file = Path(__file__).parent / "results" / "test_007_results.json"
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
        self.test_007_basic_retrieval()
        self.test_007_with_user_filter()
        self.test_007_with_limit()
        self.test_007_response_structure()
        
        # Generate report
        return self.generate_report()


def main():
    """Main test execution"""
    test_suite = TestReportsInExceptionReview()
    success = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

