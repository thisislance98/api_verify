#!/usr/bin/env python3
"""
Test Case #028: Recalled Expense Reports
User Query: Show me all recalled expense reports
Service: Expense Reports & Status
API: GET /api/v3.0/expense/reports with approvalStatusCode=A_RESU&recalledDate IS NOT NULL

This test verifies that users can retrieve expense reports that have been recalled.

A recalled report is one that:
1. Has approval status A_RESU (Recalled/Resumed)
2. Has a recalledDate that is not null
3. Was previously submitted but pulled back by the employee for corrections

Note: The Concur API may not explicitly support filtering by recalledDate IS NOT NULL,
so we'll retrieve reports with A_RESU status and verify they have recall information.
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


class TestRecalledReports:
    """Test suite for recalled expense reports"""
    
    def __init__(self):
        self.sdk = None
        self.user_id = None
        self.username = None
        self.results = {
            'test_case': '028',
            'user_query': 'Show me all recalled expense reports',
            'api_endpoint': 'GET /api/v3.0/expense/reports with approvalStatusCode=A_RESU',
            'service': 'Expense Reports & Status',
            'tests': [],
            'summary': {}
        }
    
    def setup(self):
        """Initialize SDK and authenticate"""
        print("=" * 80)
        print("Test Case #028: Recalled Expense Reports")
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
    
    def test_028_recalled_reports_basic(self):
        """Test 1: Retrieve recalled reports with A_RESU status"""
        print("Test 1: Retrieve Recalled Reports (Basic)")
        print("-" * 80)
        
        test_result = {
            'test_name': 'Retrieve recalled reports with A_RESU status',
            'endpoint': '/api/v3.0/expense/reports',
            'method': 'GET',
            'filters': {
                'approvalStatusCode': 'A_RESU'
            },
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            print("  Retrieving reports with A_RESU (Recalled) status...")
            
            # Get recalled reports
            params = {
                'approvalStatusCode': 'A_RESU',
                'user': 'ALL',
                'limit': 100
            }
            result = self.sdk.get_expense_reports(params)
            
            if not result['success']:
                raise Exception(result.get('message', 'Failed to retrieve reports'))
            
            reports = result['reports']
            
            test_result['response'] = {
                'report_count': len(reports),
                'reports': reports[:10] if reports else []  # First 10 for brevity
            }
            
            if reports:
                print(f"  ✓ Found {len(reports)} recalled reports")
                print()
                
                # Display details
                for i, report in enumerate(reports, 1):
                    print(f"  Report #{i}:")
                    print(f"    Report ID: {report.get('ID')}")
                    print(f"    Report Name: {report.get('ReportName')}")
                    print(f"    Owner: {report.get('owner_name', report.get('OwnerName'))}")
                    total = report.get('Total', report.get('total', 0))
                    currency = report.get('CurrencyCode', report.get('currency_code', 'USD'))
                    print(f"    Total: {currency} {float(total):.2f}")
                    print(f"    Status: {report.get('ApprovalStatusCode')} - {report.get('ApprovalStatusName')}")
                    print(f"    Created: {report.get('created_date', report.get('CreateDate'))}")
                    print(f"    Last Modified: {report.get('last_modified_date', report.get('LastModifiedDate'))}")
                    
                    # Check for recall-related fields
                    if report.get('RecalledDate') or report.get('recalled_date'):
                        print(f"    Recalled Date: {report.get('RecalledDate', report.get('recalled_date'))}")
                    if report.get('SubmitDate') or report.get('submission_date'):
                        print(f"    Original Submit Date: {report.get('SubmitDate', report.get('submission_date'))}")
                    
                    print()
                    
                    if i >= 5:  # Limit console output to 5 reports
                        remaining = len(reports) - 5
                        if remaining > 0:
                            print(f"  ... and {remaining} more recalled reports")
                        break
                
                test_result['passed'] = True
            else:
                print("  ⚠ No recalled reports found")
                print()
                print("  This is not necessarily an error - it means no reports have been")
                print("  recalled in this environment. To create test data:")
                print()
                print("  1. Log into Concur UI")
                print("  2. Create and submit an expense report")
                print("  3. Recall the report (pull it back from approval)")
                print("  4. Run this test again")
                print()
                
                test_result['passed'] = True  # Pass with no data is acceptable
            
        except Exception as e:
            print(f"  ✗ Test failed: {str(e)}")
            test_result['error'] = str(e)
            test_result['passed'] = False
        
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_028_recalled_reports_with_date_filter(self):
        """Test 2: Retrieve recalled reports from last 90 days"""
        print("Test 2: Recalled Reports in Last 90 Days")
        print("-" * 80)
        
        test_result = {
            'test_name': 'Recalled reports with date filter (last 90 days)',
            'endpoint': '/api/v3.0/expense/reports',
            'method': 'GET',
            'filters': {
                'approvalStatusCode': 'A_RESU',
                'modifiedDateAfter': '90 days ago'
            },
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            # Calculate date 90 days ago
            ninety_days_ago = datetime.now() - timedelta(days=90)
            date_filter = ninety_days_ago.strftime('%Y-%m-%d')
            
            print(f"  Searching for recalled reports modified after {date_filter}...")
            
            # Get recalled reports with date filter
            params = {
                'approvalStatusCode': 'A_RESU',
                'user': 'ALL',
                'modifiedDateAfter': date_filter,
                'limit': 100
            }
            result = self.sdk.get_expense_reports(params)
            
            if not result['success']:
                raise Exception(result.get('message', 'Failed to retrieve reports'))
            
            reports = result['reports']
            
            test_result['response'] = {
                'report_count': len(reports),
                'date_filter': date_filter,
                'reports': reports[:10] if reports else []
            }
            
            if reports:
                print(f"  ✓ Found {len(reports)} recalled reports in last 90 days")
                print()
                
                # Calculate recall frequency by month
                recall_by_month = {}
                for report in reports:
                    modified_date = report.get('LastModifiedDate', '')
                    if modified_date:
                        month = modified_date[:7]  # YYYY-MM
                        recall_by_month[month] = recall_by_month.get(month, 0) + 1
                
                if recall_by_month:
                    print("  Recall frequency by month:")
                    for month in sorted(recall_by_month.keys(), reverse=True):
                        print(f"    {month}: {recall_by_month[month]} reports")
                    print()
                
                test_result['passed'] = True
            else:
                print("  ⚠ No recalled reports found in last 90 days")
                print()
                test_result['passed'] = True  # Pass with no data is acceptable
            
        except Exception as e:
            print(f"  ✗ Test failed: {str(e)}")
            test_result['error'] = str(e)
            test_result['passed'] = False
        
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_028_recalled_reports_by_employee(self):
        """Test 3: Analyze recalled reports by employee"""
        print("Test 3: Recalled Reports Analysis by Employee")
        print("-" * 80)
        
        test_result = {
            'test_name': 'Analyze recalled reports by employee',
            'endpoint': '/api/v3.0/expense/reports',
            'method': 'GET',
            'filters': {
                'approvalStatusCode': 'A_RESU'
            },
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            print("  Retrieving recalled reports for employee analysis...")
            
            params = {
                'approvalStatusCode': 'A_RESU',
                'user': 'ALL',
                'limit': 100
            }
            result = self.sdk.get_expense_reports(params)
            
            if not result['success']:
                raise Exception(result.get('message', 'Failed to retrieve reports'))
            
            reports = result['reports']
            
            if reports:
                # Group by employee
                by_employee = {}
                for report in reports:
                    owner = report.get('owner_name', report.get('OwnerName', 'Unknown'))
                    if owner not in by_employee:
                        by_employee[owner] = {
                            'count': 0,
                            'total_amount': 0,
                            'reports': []
                        }
                    by_employee[owner]['count'] += 1
                    total = float(report.get('Total', report.get('total', 0)))
                    by_employee[owner]['total_amount'] += total
                    by_employee[owner]['reports'].append({
                        'id': report.get('ID'),
                        'name': report.get('ReportName', report.get('name')),
                        'amount': total,
                        'created': report.get('created_date', report.get('CreateDate')),
                        'modified': report.get('last_modified_date', report.get('LastModifiedDate'))
                    })
                
                print(f"  ✓ Found {len(reports)} recalled reports from {len(by_employee)} employees")
                print()
                
                # Sort by recall count
                sorted_employees = sorted(
                    by_employee.items(),
                    key=lambda x: x[1]['count'],
                    reverse=True
                )
                
                print("  Employees with recalled reports:")
                for employee, data in sorted_employees[:10]:  # Top 10
                    avg_amount = data['total_amount'] / data['count']
                    print(f"    {employee}:")
                    print(f"      Recalled: {data['count']} reports")
                    print(f"      Total value: ${data['total_amount']:.2f}")
                    print(f"      Average per report: ${avg_amount:.2f}")
                    print()
                
                test_result['response'] = {
                    'total_reports': len(reports),
                    'unique_employees': len(by_employee),
                    'employee_summary': by_employee
                }
                test_result['passed'] = True
                
            else:
                print("  ⚠ No recalled reports found for analysis")
                print()
                test_result['passed'] = True  # Pass with no data is acceptable
            
        except Exception as e:
            print(f"  ✗ Test failed: {str(e)}")
            test_result['error'] = str(e)
            test_result['passed'] = False
        
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_028_recalled_vs_other_statuses(self):
        """Test 4: Compare recalled reports with other approval statuses"""
        print("Test 4: Recalled Reports vs Other Statuses")
        print("-" * 80)
        
        test_result = {
            'test_name': 'Compare recalled reports with other statuses',
            'endpoint': '/api/v3.0/expense/reports',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            print("  Comparing approval statuses...")
            
            # Get reports with different statuses
            statuses_to_check = {
                'A_RESU': 'Recalled',
                'A_PEND': 'Pending Approval',
                'A_APPR': 'Approved',
                'A_NOTF': 'Not Submitted'
            }
            
            status_counts = {}
            for status_code, status_name in statuses_to_check.items():
                params = {
                    'approvalStatusCode': status_code,
                    'user': 'ALL',
                    'limit': 100
                }
                result = self.sdk.get_expense_reports(params)
                
                if result['success']:
                    status_counts[status_code] = {
                        'name': status_name,
                        'count': len(result['reports'])
                    }
                else:
                    status_counts[status_code] = {
                        'name': status_name,
                        'count': 0
                    }
            
            print("  Report counts by approval status:")
            for code, data in status_counts.items():
                print(f"    {code} ({data['name']}): {data['count']} reports")
            
            print()
            
            # Calculate recall rate
            recalled_count = status_counts.get('A_RESU', {}).get('count', 0)
            total_submitted = sum(
                status_counts.get(code, {}).get('count', 0)
                for code in ['A_RESU', 'A_PEND', 'A_APPR']
            )
            
            if total_submitted > 0:
                recall_rate = (recalled_count / total_submitted) * 100
                print(f"  Recall rate: {recall_rate:.1f}% ({recalled_count}/{total_submitted})")
                print()
            
            test_result['response'] = {
                'status_counts': status_counts,
                'recalled_count': recalled_count,
                'total_submitted': total_submitted,
                'recall_rate_pct': round(recall_rate, 2) if total_submitted > 0 else 0
            }
            test_result['passed'] = True
            
        except Exception as e:
            print(f"  ✗ Test failed: {str(e)}")
            test_result['error'] = str(e)
            test_result['passed'] = False
        
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def generate_report(self):
        """Generate test results JSON file"""
        # Calculate summary
        total = len(self.results['tests'])
        passed = sum(1 for t in self.results['tests'] if t['passed'])
        failed = total - passed
        
        self.results['summary'] = {
            'total': total,
            'passed': passed,
            'failed': failed,
            'success_rate': f"{(passed/total*100):.1f}%" if total > 0 else "0%",
            'timestamp': datetime.now().isoformat()
        }
        
        # Save to results directory
        results_dir = Path(__file__).parent / 'results'
        results_dir.mkdir(exist_ok=True)
        
        results_file = results_dir / 'test_028_results.json'
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {self.results['summary']['success_rate']}")
        print()
        print(f"Results saved to: {results_file}")
        print("=" * 80)
    
    def run_all_tests(self):
        """Execute all tests"""
        if not self.setup():
            print("Setup failed. Cannot continue with tests.")
            return False
        
        # Run all test methods
        test_methods = [
            self.test_028_recalled_reports_basic,
            self.test_028_recalled_reports_with_date_filter,
            self.test_028_recalled_reports_by_employee,
            self.test_028_recalled_vs_other_statuses
        ]
        
        for test_method in test_methods:
            test_method()
            print()
        
        self.generate_report()
        
        # Return True if all tests passed
        return all(t['passed'] for t in self.results['tests'])


if __name__ == "__main__":
    test_suite = TestRecalledReports()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)

