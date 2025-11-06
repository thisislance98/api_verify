#!/usr/bin/env python3
"""
Test Case #020: Expense Reports with Missing Manager Approval
User Query: Show me expense reports with missing manager approval
Service: Expense Reports & Status
API: GET /api/v3.0/expense/reports

This test verifies retrieving expense reports that are in pending approval status
but have no manager/approver assigned, which could indicate workflow configuration
issues or missing manager assignments.
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


class TestMissingManagerApproval:
    """Test suite for reports with missing manager approval"""
    
    def __init__(self):
        self.sdk = None
        self.results = {
            'test_case': '020',
            'user_query': 'Show me expense reports with missing manager approval',
            'api_endpoint': 'GET /api/v3.0/expense/reports?approvalStatusCode=A_PEND&approverName=null',
            'service': 'Expense Reports & Status',
            'tests': [],
            'summary': {}
        }
    
    def setup(self):
        """Initialize SDK and authenticate"""
        print("=" * 80)
        print("Test Case #020: Expense Reports with Missing Manager Approval")
        print("=" * 80)
        print()
        
        print("Setup: Initializing SDK...")
        try:
            # Load credentials from config - using manager_approver for context
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
    
    def test_020_basic_retrieval(self):
        """Test 1: Basic retrieval of reports with missing manager approval"""
        test_name = "Basic retrieval of reports with missing manager approval"
        print(f"Test 1: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports?approvalStatusCode=A_PEND&approverName=null',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.get_reports_with_missing_manager_approval(limit=50, user='ALL')
            
            if result['success']:
                test_result['passed'] = True
                test_result['response'] = {
                    'count': result['count'],
                    'approval_status_code': result['approval_status_code'],
                    'reports': result['reports'][:5] if result['reports'] else []  # Sample first 5
                }
                
                print(f"  ✓ Successfully retrieved reports with missing manager approval")
                print(f"  Reports found: {result['count']}")
                print(f"  Approval Status Code: {result['approval_status_code']}")
                
                if result['count'] > 0:
                    print(f"\n  Sample Reports (first 5):")
                    for i, report in enumerate(result['reports'][:5], 1):
                        print(f"\n  Report #{i}:")
                        print(f"    ID: {report.get('id')}")
                        print(f"    Name: {report.get('name')}")
                        print(f"    Owner: {report.get('owner_name')} ({report.get('owner_login_id')})")
                        print(f"    Total: {report.get('currency_code', '')} {report.get('total', 0):.2f}")
                        print(f"    Submission Date: {report.get('submission_date')}")
                        print(f"    Days Since Submission: {report.get('days_since_submission')}")
                        print(f"    Approval Status: {report.get('approval_status')} ({report.get('approval_status_code')})")
                        print(f"    Approver Name: '{report.get('approver_name')}'")
                        print(f"    Approver Login ID: '{report.get('approver_login_id')}'")
                        print(f"    Workflow Step: {report.get('workflow_step')}")
                else:
                    print(f"\n  ⚠️  No reports found with missing manager approval")
                    print(f"  This could mean:")
                    print(f"    - All pending reports have approvers assigned (good!)")
                    print(f"    - There are no pending reports in the system")
                    print(f"    - The workflow always assigns approvers automatically")
            else:
                test_result['passed'] = False
                test_result['error'] = result.get('error')
                print(f"  ✗ Failed to retrieve reports: {result.get('error')}")
            
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Test failed with exception: {str(e)}")
        
        self.results['tests'].append(test_result)
        print()
    
    def test_020_verify_status_codes(self):
        """Test 2: Verify approval status codes and missing approver fields"""
        test_name = "Verify approval status codes and missing approver fields"
        print(f"Test 2: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports?approvalStatusCode=A_PEND',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.get_reports_with_missing_manager_approval(limit=100, user='ALL')
            
            if result['success']:
                reports = result['reports']
                
                # Verify all reports have A_PEND status
                all_pending = all(r.get('approval_status_code') == 'A_PEND' for r in reports)
                
                # Verify all reports have missing approver
                all_missing_approver = all(
                    not r.get('approver_name') or r.get('approver_name').strip() == ''
                    for r in reports
                )
                
                if all_pending and all_missing_approver:
                    test_result['passed'] = True
                    test_result['response'] = {
                        'count': result['count'],
                        'all_pending_status': all_pending,
                        'all_missing_approver': all_missing_approver,
                        'status_verification': 'PASS'
                    }
                    print(f"  ✓ All reports verified to be in A_PEND status")
                    print(f"  ✓ All reports verified to have missing approver")
                    print(f"  Total verified: {result['count']}")
                else:
                    test_result['passed'] = False
                    test_result['response'] = {
                        'count': result['count'],
                        'all_pending_status': all_pending,
                        'all_missing_approver': all_missing_approver,
                        'status_verification': 'FAIL'
                    }
                    print(f"  ✗ Verification failed")
                    print(f"    All reports in A_PEND status: {all_pending}")
                    print(f"    All reports missing approver: {all_missing_approver}")
            else:
                test_result['passed'] = False
                test_result['error'] = result.get('error')
                print(f"  ✗ Failed to retrieve reports: {result.get('error')}")
            
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Test failed with exception: {str(e)}")
        
        self.results['tests'].append(test_result)
        print()
    
    def test_020_check_days_pending(self):
        """Test 3: Check how long reports have been pending without approver"""
        test_name = "Analyze time reports have been pending without approver"
        print(f"Test 3: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports?approvalStatusCode=A_PEND',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.get_reports_with_missing_manager_approval(limit=100, user='ALL')
            
            if result['success']:
                reports = result['reports']
                
                if len(reports) > 0:
                    # Calculate statistics
                    days_pending = [r.get('days_since_submission', 0) for r in reports if r.get('days_since_submission') is not None]
                    
                    if days_pending:
                        avg_days = sum(days_pending) / len(days_pending)
                        max_days = max(days_pending)
                        min_days = min(days_pending)
                        
                        # Find reports pending more than 7 days
                        overdue_reports = [r for r in reports if r.get('days_since_submission', 0) > 7]
                        
                        test_result['passed'] = True
                        test_result['response'] = {
                            'total_reports': len(reports),
                            'average_days_pending': round(avg_days, 1),
                            'max_days_pending': max_days,
                            'min_days_pending': min_days,
                            'overdue_count': len(overdue_reports),
                            'overdue_threshold_days': 7
                        }
                        
                        print(f"  ✓ Time analysis completed")
                        print(f"  Total reports: {len(reports)}")
                        print(f"  Average days pending: {avg_days:.1f}")
                        print(f"  Max days pending: {max_days}")
                        print(f"  Min days pending: {min_days}")
                        print(f"  Reports overdue (>7 days): {len(overdue_reports)}")
                        
                        if overdue_reports:
                            print(f"\n  Overdue Reports:")
                            for report in overdue_reports[:3]:
                                print(f"    - {report.get('name')} ({report.get('days_since_submission')} days)")
                    else:
                        test_result['passed'] = True
                        test_result['response'] = {'message': 'No time data available'}
                        print(f"  ⚠️  No time data available for analysis")
                else:
                    test_result['passed'] = True
                    test_result['response'] = {'message': 'No reports found'}
                    print(f"  ⚠️  No reports to analyze")
            else:
                test_result['passed'] = False
                test_result['error'] = result.get('error')
                print(f"  ✗ Failed to retrieve reports: {result.get('error')}")
            
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Test failed with exception: {str(e)}")
        
        self.results['tests'].append(test_result)
        print()
    
    def test_020_compare_with_all_pending(self):
        """Test 4: Compare with all pending reports to calculate percentage"""
        test_name = "Compare with all pending reports"
        print(f"Test 4: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports?approvalStatusCode=A_PEND',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            # Get reports with missing approver
            result_missing = self.sdk.get_reports_with_missing_manager_approval(limit=100, user='ALL')
            
            # Get all pending reports for comparison
            result_all_pending = self.sdk.get_expense_reports(params={
                'approvalStatusCode': 'A_PEND',
                'limit': 100,
                'user': 'ALL'
            })
            
            if result_missing['success'] and result_all_pending['success']:
                missing_count = result_missing['count']
                all_pending_count = result_all_pending.get('count', 0)
                
                percentage = (missing_count / all_pending_count * 100) if all_pending_count > 0 else 0
                
                test_result['passed'] = True
                test_result['response'] = {
                    'reports_missing_approver': missing_count,
                    'total_pending_reports': all_pending_count,
                    'percentage_missing_approver': round(percentage, 1)
                }
                
                print(f"  ✓ Comparison completed")
                print(f"  Reports missing approver: {missing_count}")
                print(f"  Total pending reports: {all_pending_count}")
                print(f"  Percentage missing approver: {percentage:.1f}%")
                
                if percentage > 10:
                    print(f"\n  ⚠️  WARNING: More than 10% of pending reports lack approver assignment!")
                    print(f"  This may indicate a workflow configuration issue.")
            else:
                test_result['passed'] = False
                test_result['error'] = result_missing.get('error') or result_all_pending.get('error')
                print(f"  ✗ Failed to retrieve reports")
            
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Test failed with exception: {str(e)}")
        
        self.results['tests'].append(test_result)
        print()
    
    def generate_report(self):
        """Generate test results report"""
        # Calculate summary
        total_tests = len(self.results['tests'])
        passed_tests = sum(1 for t in self.results['tests'] if t['passed'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        self.results['summary'] = {
            'total': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'success_rate': f"{success_rate:.1f}%",
            'timestamp': datetime.now().isoformat()
        }
        
        # Print summary
        print("=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Save to file
        results_dir = Path(__file__).parent / 'results'
        results_dir.mkdir(exist_ok=True)
        
        results_file = results_dir / 'test_020_results.json'
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"Results saved to: {results_file}")
        print()
        
        return self.results
    
    def run_all_tests(self):
        """Execute all tests"""
        if not self.setup():
            print("Setup failed. Cannot proceed with tests.")
            return False
        
        self.test_020_basic_retrieval()
        self.test_020_verify_status_codes()
        self.test_020_check_days_pending()
        self.test_020_compare_with_all_pending()
        
        self.generate_report()
        
        # Return True if all tests passed
        return self.results['summary']['failed'] == 0


if __name__ == "__main__":
    test_suite = TestMissingManagerApproval()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)

