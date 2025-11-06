#!/usr/bin/env python3
"""
Test Case #034: Reports Where I'm Listed as a Delegate
User Query: Can I see reports where I'm listed as a delegate?
Service: Expense Reports & Status
API: GET /api/v3.0/expense/reports?delegateLoginID=me

This test verifies retrieving expense reports where the current authenticated
user is listed as a delegate, allowing them to act on behalf of the report owner.
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


class TestReportsWhereImDelegate:
    """Test suite for reports where current user is a delegate"""
    
    def __init__(self):
        self.sdk = None
        self.results = {
            'test_case': '034',
            'user_query': 'Can I see reports where I\'m listed as a delegate?',
            'api_endpoint': 'GET /api/v3.0/expense/reports?delegateLoginID=me',
            'service': 'Expense Reports & Status',
            'tests': [],
            'summary': {}
        }
    
    def setup(self):
        """Initialize SDK and authenticate"""
        print("=" * 80)
        print("Test Case #034: Reports Where I'm Listed as a Delegate")
        print("=" * 80)
        print()
        
        print("Setup: Initializing SDK...")
        try:
            # Load credentials - using expense_user account which has delegate relationships
            # According to test_accounts.json: "expense_user and delegate_user delegate each other"
            creds = get_test_credentials('expense_user', 'integration')
            print(f"  Using expense_user account (has delegate relationships)")
            
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
    
    def test_034_basic_retrieval(self):
        """Test 1: Basic retrieval of reports where I'm a delegate"""
        test_name = "Basic retrieval of reports where I'm a delegate"
        print(f"Test 1: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports?delegateLoginID=me',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.get_reports_where_im_delegate(limit=50)
            
            if result['success']:
                test_result['passed'] = True
                test_result['response'] = {
                    'count': result['count'],
                    'reports': result['reports'][:5] if result['reports'] else []  # Sample first 5
                }
                
                print(f"  ✓ Successfully retrieved reports where I'm a delegate")
                print(f"  Reports found: {result['count']}")
                
                if result['count'] > 0:
                    print(f"\n  Sample Reports (first 5):")
                    for i, report in enumerate(result['reports'][:5], 1):
                        print(f"\n  Report #{i}:")
                        print(f"    ID: {report.get('id')}")
                        print(f"    Name: {report.get('name')}")
                        print(f"    Owner: {report.get('owner_name')} ({report.get('owner_login_id')})")
                        print(f"    Delegate: {report.get('delegate_name')} ({report.get('delegate_login_id')})")
                        print(f"    Total: {report.get('currency_code', '')} {report.get('total', 0):.2f}")
                        print(f"    Status: {report.get('approval_status')} ({report.get('approval_status_code')})")
                        print(f"    Payment: {report.get('payment_status_name')} ({report.get('payment_status_code')})")
                        print(f"    Created: {report.get('created_date')}")
                        print(f"    Submitted: {report.get('submission_date') or 'Not submitted'}")
                else:
                    print(f"\n  ⚠️  No reports found where you are listed as delegate")
                    print(f"  This could mean:")
                    print(f"    - No one has assigned you as a delegate")
                    print(f"    - All delegated reports have been processed")
                    print(f"    - The account doesn't have delegate permissions configured")
            else:
                test_result['passed'] = False
                test_result['error'] = result.get('error')
                print(f"  ✗ Failed to retrieve reports: {result.get('error')}")
            
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Test failed with exception: {str(e)}")
        
        self.results['tests'].append(test_result)
        print()
    
    def test_034_group_by_owner(self):
        """Test 2: Group reports by owner"""
        test_name = "Group reports by owner"
        print(f"Test 2: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports?delegateLoginID=me',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.get_reports_where_im_delegate(limit=100)
            
            if result['success']:
                reports = result['reports']
                
                # Group reports by owner
                owner_groups = {}
                for report in reports:
                    owner_id = report.get('owner_login_id', 'Unknown')
                    owner_name = report.get('owner_name', 'Unknown')
                    
                    if owner_id not in owner_groups:
                        owner_groups[owner_id] = {
                            'name': owner_name,
                            'reports': [],
                            'total_amount': 0,
                            'count': 0
                        }
                    
                    owner_groups[owner_id]['reports'].append(report)
                    owner_groups[owner_id]['count'] += 1
                    owner_groups[owner_id]['total_amount'] += report.get('total', 0)
                
                test_result['passed'] = True
                test_result['response'] = {
                    'total_reports': len(reports),
                    'unique_owners': len(owner_groups),
                    'owner_summary': {
                        owner_id: {
                            'name': data['name'],
                            'count': data['count'],
                            'total_amount': round(data['total_amount'], 2)
                        }
                        for owner_id, data in owner_groups.items()
                    }
                }
                
                print(f"  ✓ Successfully grouped reports by owner")
                print(f"  Total reports: {len(reports)}")
                print(f"  Unique owners: {len(owner_groups)}")
                
                if owner_groups:
                    print(f"\n  Reports by Owner:")
                    for owner_id, data in sorted(owner_groups.items(), 
                                                 key=lambda x: x[1]['count'], 
                                                 reverse=True):
                        print(f"    {data['name']} ({owner_id})")
                        print(f"      Reports: {data['count']}")
                        print(f"      Total Amount: ${data['total_amount']:.2f}")
                else:
                    print(f"  No reports to group")
            else:
                test_result['passed'] = False
                test_result['error'] = result.get('error')
                print(f"  ✗ Failed to retrieve reports: {result.get('error')}")
            
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Test failed with exception: {str(e)}")
        
        self.results['tests'].append(test_result)
        print()
    
    def test_034_group_by_status(self):
        """Test 3: Group reports by approval status"""
        test_name = "Group reports by approval status"
        print(f"Test 3: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports?delegateLoginID=me',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.get_reports_where_im_delegate(limit=100)
            
            if result['success']:
                reports = result['reports']
                
                # Group reports by approval status
                status_groups = {}
                for report in reports:
                    status_code = report.get('approval_status_code', 'Unknown')
                    status_name = report.get('approval_status', 'Unknown')
                    
                    if status_code not in status_groups:
                        status_groups[status_code] = {
                            'name': status_name,
                            'reports': [],
                            'count': 0,
                            'total_amount': 0
                        }
                    
                    status_groups[status_code]['reports'].append(report)
                    status_groups[status_code]['count'] += 1
                    status_groups[status_code]['total_amount'] += report.get('total', 0)
                
                test_result['passed'] = True
                test_result['response'] = {
                    'total_reports': len(reports),
                    'unique_statuses': len(status_groups),
                    'status_summary': {
                        code: {
                            'name': data['name'],
                            'count': data['count'],
                            'total_amount': round(data['total_amount'], 2)
                        }
                        for code, data in status_groups.items()
                    }
                }
                
                print(f"  ✓ Successfully grouped reports by status")
                print(f"  Total reports: {len(reports)}")
                print(f"  Unique statuses: {len(status_groups)}")
                
                if status_groups:
                    print(f"\n  Reports by Approval Status:")
                    for status_code, data in sorted(status_groups.items(), 
                                                    key=lambda x: x[1]['count'], 
                                                    reverse=True):
                        print(f"    {status_code} - {data['name']}")
                        print(f"      Reports: {data['count']}")
                        print(f"      Total Amount: ${data['total_amount']:.2f}")
                else:
                    print(f"  No reports to group")
            else:
                test_result['passed'] = False
                test_result['error'] = result.get('error')
                print(f"  ✗ Failed to retrieve reports: {result.get('error')}")
            
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Test failed with exception: {str(e)}")
        
        self.results['tests'].append(test_result)
        print()
    
    def test_034_actionable_reports(self):
        """Test 4: Identify reports requiring delegate action"""
        test_name = "Identify reports requiring delegate action"
        print(f"Test 4: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports?delegateLoginID=me',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.get_reports_where_im_delegate(limit=100)
            
            if result['success']:
                reports = result['reports']
                
                # Identify actionable reports
                # Draft reports that could be submitted
                draft_reports = [r for r in reports if not r.get('submission_date')]
                
                # Pending reports that might need attention
                pending_reports = [r for r in reports if r.get('approval_status_code') == 'A_PEND']
                
                # Reports sent back to employee
                sent_back_reports = [r for r in reports if r.get('approval_status_code') == 'A_RESU']
                
                test_result['passed'] = True
                test_result['response'] = {
                    'total_reports': len(reports),
                    'draft_reports': len(draft_reports),
                    'pending_approval': len(pending_reports),
                    'sent_back': len(sent_back_reports),
                    'actionable_count': len(draft_reports) + len(sent_back_reports)
                }
                
                print(f"  ✓ Successfully identified actionable reports")
                print(f"  Total delegated reports: {len(reports)}")
                print(f"  Draft reports (can submit): {len(draft_reports)}")
                print(f"  Pending approval: {len(pending_reports)}")
                print(f"  Sent back (needs revision): {len(sent_back_reports)}")
                print(f"  Total actionable: {len(draft_reports) + len(sent_back_reports)}")
                
                if draft_reports:
                    print(f"\n  Draft Reports:")
                    for report in draft_reports[:3]:
                        print(f"    - {report.get('name')} (Owner: {report.get('owner_name')})")
                        print(f"      Amount: {report.get('currency_code', '')} {report.get('total', 0):.2f}")
                
                if sent_back_reports:
                    print(f"\n  Reports Sent Back:")
                    for report in sent_back_reports[:3]:
                        print(f"    - {report.get('name')} (Owner: {report.get('owner_name')})")
                        print(f"      Amount: {report.get('currency_code', '')} {report.get('total', 0):.2f}")
            else:
                test_result['passed'] = False
                test_result['error'] = result.get('error')
                print(f"  ✗ Failed to retrieve reports: {result.get('error')}")
            
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
        
        results_file = results_dir / 'test_034_results.json'
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
        
        self.test_034_basic_retrieval()
        self.test_034_group_by_owner()
        self.test_034_group_by_status()
        self.test_034_actionable_reports()
        
        self.generate_report()
        
        # Return True if all tests passed
        return self.results['summary']['failed'] == 0


if __name__ == "__main__":
    test_suite = TestReportsWhereImDelegate()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)

