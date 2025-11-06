#!/usr/bin/env python3
"""
Test Case #021: Reports Approved Yesterday
User Query: What reports did I approve yesterday?
Service: Expense Reports & Status
API: GET /api/v3.0/expense/reports with approvedDateAfter and approvedDateBefore filters

This test verifies that a manager can retrieve expense reports they approved yesterday.

IMPORTANT API LIMITATION:
The Concur V3 API accepts approvedDateAfter and approvedDateBefore filter parameters,
but does NOT return an ApprovedDate field in the response. The API also has inconsistent
behavior with these filters in sandbox environments. 

Alternative approaches:
1. Use LastModifiedDate as a proxy (when report status changes to approved, it's modified)
2. Filter for A_APPR (Approved) status and use LastModifiedDate within date range
3. Track approval actions separately in your own system

For this test, we demonstrate the API filter parameters and show reports that have
recently changed to approved status using LastModifiedDate as a proxy.
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


class TestReportsApprovedYesterday:
    """Test suite for reports approved yesterday"""
    
    def __init__(self):
        self.sdk = None
        self.user_id = None
        self.username = None
        self.results = {
            'test_case': '021',
            'user_query': 'What reports did I approve yesterday?',
            'api_endpoint': 'GET /api/v3.0/expense/reports with approvedDateAfter and approvedDateBefore filters',
            'service': 'Expense Reports & Status',
            'tests': [],
            'summary': {}
        }
    
    def setup(self):
        """Initialize SDK and authenticate"""
        print("=" * 80)
        print("Test Case #021: Reports Approved Yesterday")
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
            self.username = creds['username']
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
    
    def test_021_reports_approved_yesterday(self):
        """Test 1: Retrieve approved reports using LastModifiedDate as proxy"""
        test_name = "Reports approved yesterday (using LastModifiedDate proxy)"
        print(f"Test 1: {test_name}")
        print("-" * 80)
        
        # Calculate yesterday's date range
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        yesterday_start = yesterday.strftime('%Y-%m-%d')
        today_start = today.strftime('%Y-%m-%d')
        
        print(f"  Searching for approved reports modified on: {yesterday_start}")
        print(f"  Date range: {yesterday_start} to {today_start}")
        print(f"  Note: Using LastModifiedDate as proxy (API doesn't return ApprovedDate)")
        print()
        
        test_result = {
            'test_name': test_name,
            'endpoint': f'/api/v3.0/expense/reports?approvalStatusCode=A_APPR&modifiedDateAfter={yesterday_start}&modifiedDateBefore={today_start}',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None,
            'date_filter': {
                'yesterday': yesterday_start,
                'today': today_start
            }
        }
        
        try:
            # Use V3 API with approved status and modified date filters
            # LastModifiedDate is updated when approval status changes
            params = {
                'approvalStatusCode': 'A_APPR',  # Only approved reports
                'modifiedDateAfter': yesterday_start,
                'modifiedDateBefore': today_start,
                'user': 'ALL',
                'limit': 100
            }
            
            result = self.sdk.get_expense_reports(params)
            
            if result['success']:
                reports = result['reports']
                count = len(reports)
                
                test_result['passed'] = True
                test_result['response'] = {
                    'count': count,
                    'params': params
                }
                
                print(f"  ✓ Request successful")
                print(f"  Approved reports modified yesterday: {count}")
                
                if count > 0:
                    print(f"\n  Sample approved reports:")
                    for i, report in enumerate(reports[:5], 1):  # Show first 5
                        print(f"    {i}. {report.get('ReportName', report.get('name', 'N/A'))}")
                        print(f"       - Report ID: {report.get('ID', report.get('id', 'N/A'))}")
                        print(f"       - Owner: {report.get('OwnerName', report.get('owner_name', 'N/A'))}")
                        print(f"       - Total: {report.get('Total', report.get('total', 'N/A'))} {report.get('CurrencyCode', report.get('currency_code', ''))}")
                        print(f"       - Approval Status: {report.get('ApprovalStatusName', report.get('approval_status', 'N/A'))}")
                        print(f"       - Last Modified: {report.get('LastModifiedDate', 'N/A')}")
                    
                    if count > 5:
                        print(f"    ... and {count - 5} more reports")
                else:
                    print(f"\n  ℹ️  No approved reports were modified yesterday")
                    print(f"  This is expected if:")
                    print(f"    - No reports were approved on {yesterday_start}")
                    print(f"    - The sandbox doesn't have recent approval activity")
                    print(f"\n  💡 To create test data:")
                    print(f"    1. Submit reports to your manager")
                    print(f"    2. Approve them via Concur UI")
                    print(f"    3. Check LastModifiedDate changes to today's date")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_021_reports_approved_last_7_days(self):
        """Test 2: Retrieve approved reports modified in last 7 days (fallback if yesterday has no data)"""
        test_name = "Approved reports modified in last 7 days"
        print(f"Test 2: {test_name}")
        print("-" * 80)
        
        # Calculate date range for last 7 days
        today = datetime.now().date()
        seven_days_ago = today - timedelta(days=7)
        seven_days_ago_str = seven_days_ago.strftime('%Y-%m-%d')
        today_str = today.strftime('%Y-%m-%d')
        
        print(f"  Searching for approved reports modified in last 7 days")
        print(f"  Date range: {seven_days_ago_str} to {today_str}")
        print()
        
        test_result = {
            'test_name': test_name,
            'endpoint': f'/api/v3.0/expense/reports?approvalStatusCode=A_APPR&modifiedDateAfter={seven_days_ago_str}',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None,
            'date_filter': {
                'start': seven_days_ago_str,
                'end': today_str
            }
        }
        
        try:
            params = {
                'approvalStatusCode': 'A_APPR',
                'modifiedDateAfter': seven_days_ago_str,
                'user': 'ALL',
                'limit': 100
            }
            
            result = self.sdk.get_expense_reports(params)
            
            if result['success']:
                reports = result['reports']
                count = len(reports)
                
                test_result['passed'] = True
                test_result['response'] = {
                    'count': count,
                    'params': params
                }
                
                print(f"  ✓ Request successful")
                print(f"  Approved reports modified in last 7 days: {count}")
                
                if count > 0:
                    # Group by modification date
                    by_date = {}
                    for report in reports:
                        modified_date = report.get('LastModifiedDate') or report.get('last_modified_date', 'Unknown')
                        if modified_date and modified_date != 'Unknown':
                            # Extract just the date part
                            date_part = modified_date.split('T')[0] if 'T' in modified_date else modified_date
                            by_date[date_part] = by_date.get(date_part, 0) + 1
                    
                    if by_date:
                        print(f"\n  Reports by last modified date:")
                        for date in sorted(by_date.keys(), reverse=True):
                            print(f"    {date}: {by_date[date]} report(s)")
                    
                    print(f"\n  Sample reports:")
                    for i, report in enumerate(reports[:3], 1):
                        print(f"    {i}. {report.get('ReportName', report.get('name', 'N/A'))}")
                        print(f"       - Total: {report.get('Total', report.get('total', 'N/A'))} {report.get('CurrencyCode', report.get('currency_code', ''))}")
                        print(f"       - Status: {report.get('ApprovalStatusName', 'N/A')}")
                        modified_date = report.get('LastModifiedDate') or report.get('last_modified_date')
                        if modified_date:
                            print(f"       - Last Modified: {modified_date}")
                else:
                    print(f"\n  ℹ️  No approved reports modified in the last 7 days")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_021_approved_reports_validation(self):
        """Test 3: Validate response structure and key fields"""
        test_name = "Approved reports field validation"
        print(f"Test 3: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'validations': [],
            'error': None
        }
        
        try:
            # Get any approved reports (last 30 days to increase chances of finding data)
            thirty_days_ago = (datetime.now().date() - timedelta(days=30)).strftime('%Y-%m-%d')
            today = datetime.now().date().strftime('%Y-%m-%d')
            
            params = {
                'approvalStatusCode': 'A_APPR',  # Only approved reports
                'modifiedDateAfter': thirty_days_ago,
                'user': 'ALL',
                'limit': 50
            }
            
            result = self.sdk.get_expense_reports(params)
            
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
            
            # If we have approved reports, check for required fields
            if result.get('count', 0) > 0:
                report = result['reports'][0]
                required_fields = [
                    ('ID', 'id'),
                    ('ReportName', 'name'),
                    ('ApprovalStatusCode', 'approval_status'),
                    ('LastModifiedDate', 'last_modified_date'),  # Key field - used as proxy for approval
                    ('Total', 'total'),
                    ('CurrencyCode', 'currency_code')
                ]
                
                for field_v3, field_v4 in required_fields:
                    if (field_v3 in report and report[field_v3] is not None) or \
                       (field_v4 in report and report[field_v4] is not None):
                        validations.append({'field': f'report.{field_v3}|{field_v4}', 'present': True})
                    else:
                        validations.append({'field': f'report.{field_v3}|{field_v4}', 'present': False})
                
                print(f"  Found {result['count']} approved reports in last 30 days")
                print(f"\n  Field validation:")
                print(f"  Note: API does NOT return ApprovedDate field (known limitation)")
                print(f"        Using LastModifiedDate as proxy for approval time")
            else:
                print(f"  ℹ️  No approved reports found in last 30 days")
                print(f"  Field validation (structure only):")
            
            test_result['validations'] = validations
            
            # Test passes if structure is valid and either:
            # - We have reports with all required fields (including LastModifiedDate), OR
            # - We have no reports (which is still a valid response)
            structure_valid = all(v['present'] for v in validations if 'report.' not in v['field'])
            
            if result.get('count', 0) > 0:
                # If we have reports, check that all required fields are present
                report_fields_valid = all(v['present'] for v in validations if 'report.' in v['field'])
                test_result['passed'] = structure_valid and report_fields_valid
            else:
                # No reports is acceptable
                test_result['passed'] = structure_valid
            
            for v in validations:
                status = "✓" if v['present'] else "✗"
                print(f"    {status} {v['field']}")
            
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
        results_file = Path(__file__).parent / "results" / "test_021_results.json"
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
        self.test_021_reports_approved_yesterday()
        self.test_021_reports_approved_last_7_days()
        self.test_021_approved_reports_validation()
        
        # Generate report
        return self.generate_report()


def main():
    """Main test execution"""
    test_suite = TestReportsApprovedYesterday()
    success = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

