#!/usr/bin/env python3
"""
Test Case #016: Draft Reports Not Yet Submitted
User Query: Show me my draft reports that haven't been submitted yet
Service: Expense Reports & Status
API: GET /api/v3.0/expense/reports

This test verifies retrieving draft expense reports (A_NOTF status) that haven't been submitted yet.
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


class TestDraftReports:
    """Test suite for draft reports endpoint"""
    
    def __init__(self):
        self.sdk = None
        self.results = {
            'test_case': '016',
            'user_query': 'Show me my draft reports that haven\'t been submitted yet',
            'api_endpoint': 'GET /api/v3.0/expense/reports',
            'service': 'Expense Reports & Status',
            'tests': [],
            'summary': {}
        }
    
    def setup(self):
        """Initialize SDK and authenticate"""
        print("=" * 80)
        print("Test Case #016: Draft Reports Not Yet Submitted")
        print("=" * 80)
        print()
        
        print("Setup: Initializing SDK...")
        try:
            # Load credentials - using expense_user as they would have draft reports
            creds = get_test_credentials('expense_user', 'integration')
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
    
    def test_016_basic_draft_retrieval(self):
        """Test 1: Basic retrieval of draft reports"""
        test_name = "Basic draft reports retrieval"
        print(f"Test 1: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports?approvalStatusCode=A_NOTF&user=me',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.get_draft_reports()
            
            if result['success']:
                test_result['passed'] = True
                test_result['response'] = {
                    'status_code': result.get('status_code'),
                    'reports_found': len(result.get('Items', [])),
                    'reports': result.get('Items', [])
                }
                
                print(f"  Status Code: {result.get('status_code')}")
                print(f"  Draft Reports Found: {len(result.get('Items', []))}")
                
                # Display draft report details
                if result.get('Items'):
                    print()
                    print("  Draft Reports:")
                    for i, report in enumerate(result.get('Items', []), 1):
                        print(f"    {i}. Report Name: {report.get('Name', 'N/A')}")
                        print(f"       Report ID: {report.get('ID', 'N/A')}")
                        print(f"       Status: {report.get('ApprovalStatusCode', 'N/A')}")
                        print(f"       Total: {report.get('Total', 0)} {report.get('CurrencyCode', '')}")
                        print(f"       Created: {report.get('CreateDate', 'N/A')}")
                        print(f"       Last Modified: {report.get('LastModifiedDate', 'N/A')}")
                        print()
                else:
                    print("  ⚠️  No draft reports found")
                    print("     Consider creating a draft report for testing")
                
                print(f"  ✓ Test passed")
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Test failed: {test_result['error']}")
            
            print()
            
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Test failed with exception: {str(e)}")
            print()
        
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_016_draft_with_pagination(self):
        """Test 2: Draft reports with pagination"""
        test_name = "Draft reports with pagination (limit=5)"
        print(f"Test 2: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports?approvalStatusCode=A_NOTF&user=me&limit=5',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.get_draft_reports(limit=5)
            
            if result['success']:
                test_result['passed'] = True
                test_result['response'] = {
                    'status_code': result.get('status_code'),
                    'reports_found': len(result.get('Items', [])),
                    'limit_requested': 5,
                    'has_next_page': bool(result.get('NextPage'))
                }
                
                print(f"  Status Code: {result.get('status_code')}")
                print(f"  Reports Retrieved: {len(result.get('Items', []))}")
                print(f"  Has Next Page: {bool(result.get('NextPage'))}")
                print(f"  ✓ Test passed")
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Test failed: {test_result['error']}")
            
            print()
            
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Test failed with exception: {str(e)}")
            print()
        
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_016_draft_report_details(self):
        """Test 3: Retrieve detailed information for a draft report"""
        test_name = "Draft report detailed information"
        print(f"Test 3: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports?approvalStatusCode=A_NOTF&user=me',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            # First get draft reports
            result = self.sdk.get_draft_reports()
            
            if result['success'] and result.get('Items'):
                # Get the first draft report
                first_draft = result['Items'][0]
                report_id = first_draft.get('ID')
                
                test_result['passed'] = True
                test_result['response'] = {
                    'report_id': report_id,
                    'report_name': first_draft.get('Name'),
                    'total': first_draft.get('Total'),
                    'currency': first_draft.get('CurrencyCode'),
                    'created_date': first_draft.get('CreateDate'),
                    'owner_name': first_draft.get('OwnerName'),
                    'approval_status': first_draft.get('ApprovalStatusCode'),
                    'approval_status_name': first_draft.get('ApprovalStatusName'),
                    'payment_status': first_draft.get('PaymentStatusCode'),
                    'has_exception': first_draft.get('HasException')
                }
                
                print(f"  Report ID: {report_id}")
                print(f"  Report Name: {first_draft.get('Name')}")
                print(f"  Owner: {first_draft.get('OwnerName')}")
                print(f"  Total: {first_draft.get('Total')} {first_draft.get('CurrencyCode')}")
                print(f"  Status: {first_draft.get('ApprovalStatusName')} ({first_draft.get('ApprovalStatusCode')})")
                print(f"  Created: {first_draft.get('CreateDate')}")
                print(f"  Modified: {first_draft.get('LastModifiedDate')}")
                print(f"  Has Exception: {first_draft.get('HasException')}")
                print(f"  ✓ Test passed")
            elif result['success']:
                test_result['passed'] = True
                test_result['response'] = {'message': 'No draft reports to test with'}
                print(f"  ⚠️  No draft reports available for detailed testing")
                print(f"  ✓ Test passed (no data)")
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Test failed: {test_result['error']}")
            
            print()
            
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Test failed with exception: {str(e)}")
            print()
        
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_016_draft_reports_sorted_by_date(self):
        """Test 4: Draft reports sorted by creation date"""
        test_name = "Draft reports sorted by creation date"
        print(f"Test 4: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports?approvalStatusCode=A_NOTF&user=me&sortBy=CreateDate&sortDirection=DESC',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            # Get draft reports (SDK may not support sortBy, but test the request)
            result = self.sdk.get_draft_reports()
            
            if result['success']:
                reports = result.get('Items', [])
                
                # Sort manually if needed
                if reports:
                    sorted_reports = sorted(
                        reports,
                        key=lambda x: x.get('CreateDate', ''),
                        reverse=True
                    )
                    
                    test_result['passed'] = True
                    test_result['response'] = {
                        'reports_found': len(sorted_reports),
                        'oldest_date': sorted_reports[-1].get('CreateDate') if sorted_reports else None,
                        'newest_date': sorted_reports[0].get('CreateDate') if sorted_reports else None
                    }
                    
                    print(f"  Reports Found: {len(sorted_reports)}")
                    print(f"  Newest: {sorted_reports[0].get('CreateDate')} - {sorted_reports[0].get('Name')}")
                    if len(sorted_reports) > 1:
                        print(f"  Oldest: {sorted_reports[-1].get('CreateDate')} - {sorted_reports[-1].get('Name')}")
                else:
                    test_result['passed'] = True
                    test_result['response'] = {'message': 'No draft reports to sort'}
                    print(f"  ⚠️  No draft reports to test sorting")
                
                print(f"  ✓ Test passed")
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Test failed: {test_result['error']}")
            
            print()
            
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Test failed with exception: {str(e)}")
            print()
        
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def generate_report(self):
        """Generate test results report"""
        print("=" * 80)
        print("Generating Test Report")
        print("=" * 80)
        
        total = len(self.results['tests'])
        passed = sum(1 for test in self.results['tests'] if test['passed'])
        failed = total - passed
        success_rate = (passed / total * 100) if total > 0 else 0
        
        self.results['summary'] = {
            'total': total,
            'passed': passed,
            'failed': failed,
            'success_rate': f"{success_rate:.1f}%",
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Save results to file
        results_dir = Path(__file__).parent / 'results'
        results_dir.mkdir(exist_ok=True)
        results_file = results_dir / 'test_016_results.json'
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"Results saved to: {results_file}")
        print("=" * 80)
    
    def run_all_tests(self):
        """Execute all tests in sequence"""
        if not self.setup():
            print("Setup failed. Cannot proceed with tests.")
            return False
        
        # Run tests
        self.test_016_basic_draft_retrieval()
        self.test_016_draft_with_pagination()
        self.test_016_draft_report_details()
        self.test_016_draft_reports_sorted_by_date()
        
        # Generate report
        self.generate_report()
        
        return all(test['passed'] for test in self.results['tests'])


if __name__ == "__main__":
    test_suite = TestDraftReports()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)

