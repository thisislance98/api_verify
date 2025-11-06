#!/usr/bin/env python3
"""
Test Case #023: Reports Open for More Than 30 Days
User Query: Which reports have been open for more than 30 days?
Service: Expense Reports & Status
API: GET /api/v3.0/expense/reports

This test verifies retrieving expense reports that have been open (created but not closed)
for more than 30 days. This uses createDateBefore filter to find long-standing open reports.

Key difference from overdue reports:
- Uses createDate (when report was first created)
- Not submitDate (when submitted for approval)
- Identifies reports that have been in the system for a long time
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


class TestReportsOpenMoreThan30Days:
    """Test suite for reports open for more than 30 days"""
    
    def __init__(self):
        self.sdk = None
        self.results = {
            'test_case': '023',
            'user_query': 'Which reports have been open for more than 30 days?',
            'api_endpoint': 'GET /api/v3.0/expense/reports',
            'service': 'Expense Reports & Status',
            'tests': [],
            'summary': {}
        }
    
    def setup(self):
        """Initialize SDK and authenticate"""
        print("=" * 80)
        print("Test Case #023: Reports Open for More Than 30 Days")
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
    
    def test_023_reports_open_30_days(self):
        """Test 1: Basic retrieval of reports open for more than 30 days"""
        test_name = "Reports open for more than 30 days"
        print(f"Test 1: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports?approvalStatusCode=A_PEND&createDateBefore={30daysAgo}',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.get_reports_open_more_than_n_days(days_open=30)
            
            if result['success']:
                test_result['passed'] = True
                test_result['response'] = {
                    'count': result['count'],
                    'days_threshold': result['days_threshold'],
                    'threshold_date': result['threshold_date'],
                    'approval_status': result['approval_status']
                }
                
                print(f"  ✓ Request successful")
                print(f"  Reports open >30 days: {result['count']}")
                print(f"  Threshold date: {result['threshold_date']}")
                print(f"  Approval status filter: {result['approval_status']}")
                
                if result['count'] > 0:
                    print(f"\n  Sample report open >30 days:")
                    report = result['reports'][0]
                    print(f"    - Name: {report['name']}")
                    print(f"    - Report ID: {report['id']}")
                    print(f"    - Owner: {report.get('owner_name', 'N/A')}")
                    print(f"    - Status: {report.get('approval_status', 'N/A')}")
                    print(f"    - Created: {report.get('created_date', 'N/A')}")
                    if report.get('days_since_creation'):
                        print(f"    - Days open: {report['days_since_creation']}")
                    print(f"    - Total: {report.get('currency_code', '')} {report.get('total', 0):.2f}")
                else:
                    print(f"  ℹ No reports have been open for more than 30 days")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_023_reports_open_60_days(self):
        """Test 2: Reports open for more than 60 days"""
        test_name = "Reports open for more than 60 days"
        print(f"Test 2: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports?approvalStatusCode=A_PEND&createDateBefore={60daysAgo}',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.get_reports_open_more_than_n_days(days_open=60)
            
            if result['success']:
                test_result['passed'] = True
                test_result['response'] = {
                    'count': result['count'],
                    'days_threshold': result['days_threshold'],
                    'threshold_date': result['threshold_date']
                }
                
                print(f"  ✓ Request successful")
                print(f"  Reports open >60 days: {result['count']}")
                print(f"  Threshold date: {result['threshold_date']}")
                
                if result['count'] > 0:
                    # Show summary of all reports
                    total_amount = sum(r.get('total', 0) for r in result['reports'])
                    print(f"  Total amount in reports: {result['reports'][0].get('currency_code', 'USD')} {total_amount:.2f}")
                    print(f"\n  Top 3 oldest reports:")
                    sorted_reports = sorted(
                        result['reports'], 
                        key=lambda x: x.get('days_since_creation', 0), 
                        reverse=True
                    )
                    for i, report in enumerate(sorted_reports[:3], 1):
                        print(f"    {i}. {report['name']} - {report.get('days_since_creation', 'N/A')} days open")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_023_reports_open_90_days(self):
        """Test 3: Reports open for more than 90 days (quarterly threshold)"""
        test_name = "Reports open for more than 90 days"
        print(f"Test 3: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports?approvalStatusCode=A_PEND&createDateBefore={90daysAgo}',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.get_reports_open_more_than_n_days(days_open=90)
            
            if result['success']:
                test_result['passed'] = True
                test_result['response'] = {
                    'count': result['count'],
                    'days_threshold': result['days_threshold']
                }
                
                print(f"  ✓ Request successful")
                print(f"  Reports open >90 days (>1 quarter): {result['count']}")
                
                if result['count'] > 0:
                    print(f"  ⚠️  Warning: These reports have been open for over 3 months!")
                    print(f"  Consider reviewing or closing these aged reports.")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_023_comparison_with_overdue(self):
        """Test 4: Compare createDate vs submitDate filters"""
        test_name = "Comparison of createDate vs submitDate filtering"
        print(f"Test 4: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            # Get reports using createDate filter (open reports)
            open_result = self.sdk.get_reports_open_more_than_n_days(days_open=30)
            
            # Get reports using submitDate filter (overdue reports)
            overdue_result = self.sdk.get_overdue_reports_for_approval(days_overdue=30)
            
            if open_result['success'] and overdue_result['success']:
                test_result['passed'] = True
                test_result['response'] = {
                    'open_reports_createDate': open_result['count'],
                    'overdue_reports_submitDate': overdue_result['count'],
                    'difference': abs(open_result['count'] - overdue_result['count'])
                }
                
                print(f"  ✓ Comparison successful")
                print(f"  Reports open >30 days (createDate): {open_result['count']}")
                print(f"  Reports overdue >30 days (submitDate): {overdue_result['count']}")
                print(f"  Difference: {abs(open_result['count'] - overdue_result['count'])}")
                print()
                print(f"  💡 Insight:")
                print(f"     - 'Open' reports = created >30 days ago")
                print(f"     - 'Overdue' reports = submitted >30 days ago")
                print(f"     - A report can be open but not yet submitted")
                
            else:
                error_msg = open_result.get('message', '') or overdue_result.get('message', '')
                test_result['error'] = error_msg
                print(f"  ✗ Request failed: {error_msg}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_023_response_structure(self):
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
            result = self.sdk.get_reports_open_more_than_n_days(days_open=30)
            
            validations = []
            
            # Check required fields in response
            required_fields = [
                'success', 'reports', 'count', 'days_threshold', 
                'approval_status', 'threshold_date', 'message'
            ]
            
            for field in required_fields:
                if field in result:
                    validations.append({'field': field, 'present': True})
                else:
                    validations.append({'field': field, 'present': False})
            
            # If we have reports, validate report structure
            if result.get('count', 0) > 0:
                report = result['reports'][0]
                report_fields = ['id', 'name', 'created_date', 'days_since_creation']
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
        results_file = Path(__file__).parent / "results" / "test_023_results.json"
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
        self.test_023_reports_open_30_days()
        self.test_023_reports_open_60_days()
        self.test_023_reports_open_90_days()
        self.test_023_comparison_with_overdue()
        self.test_023_response_structure()
        
        # Generate report
        return self.generate_report()


def main():
    """Main test execution"""
    test_suite = TestReportsOpenMoreThan30Days()
    success = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

