#!/usr/bin/env python3
"""
Test Case #041: Reports Submitted On Behalf of Manager
User Query: What's the status of reports I submitted on behalf of my manager?
Service: Expense Reports & Status
API: GET /api/v3.0/expense/reports

This test verifies retrieving expense reports that were submitted by a delegate
(acting on behalf of another user). The query filters for reports where the
submitter is the current user (delegate) but the report owner is their manager.

Use Case: Delegates who submit reports on behalf of executives or other users
need to track the status of those submissions.
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


class TestDelegateSubmittedReports:
    """Test suite for reports submitted by delegate on behalf of manager"""
    
    def __init__(self):
        self.sdk = None
        self.delegate_login_id = None
        self.manager_login_id = None
        self.results = {
            'test_case': '041',
            'user_query': "What's the status of reports I submitted on behalf of my manager?",
            'api_endpoint': 'GET /api/v3.0/expense/reports?user={managerID}&submitterLoginID=me',
            'service': 'Expense Reports & Status',
            'tests': [],
            'summary': {}
        }
    
    def setup(self):
        """Initialize SDK and authenticate"""
        print("=" * 80)
        print("Test Case #041: Reports Submitted On Behalf of Manager")
        print("=" * 80)
        print()
        
        print("Setup: Initializing SDK...")
        
        # Try delegate_user first, then fallback to expense_user (they delegate each other)
        accounts_to_try = [
            ('delegate_user', 'integration'),
            ('expense_user', 'integration')
        ]
        
        for account_role, environment in accounts_to_try:
            try:
                print(f"  Trying {account_role}...")
                creds = get_test_credentials(account_role, environment)
                config = ConcurConfig(
                    client_id=creds['client_id'],
                    client_secret=creds['client_secret'],
                    username=creds['username'],
                    password=creds['password'],
                    base_url=creds['base_url'],
                    token_url=creds['token_url']
                )
                
                self.sdk = ConcurExpenseSDK(config)
                self.delegate_login_id = creds['username']
                
                # Test connection
                result = self.sdk.test_connection()
                if result['success']:
                    print(f"  ✓ SDK initialized with {account_role}")
                    print(f"  Environment: {creds['environment']}")
                    print(f"  Base URL: {self.sdk.config.base_url}")
                    print(f"  Username: {self.sdk.config.username}")
                    print(f"  Role: {creds['role']}")
                    print(f"  Delegate Login ID: {self.delegate_login_id}")
                    print(f"  ✓ Authentication successful")
                    print()
                    return True
                else:
                    print(f"  ✗ Authentication failed for {account_role}: {result['message']}")
                    continue
                    
            except Exception as e:
                print(f"  ✗ Failed with {account_role}: {str(e)}")
                continue
        
        # If we get here, all accounts failed
        print()
        print("NOTE: This test requires delegate_user or expense_user credentials")
        print("      The user must have permission to submit reports on behalf of others.")
        return False
    
    def test_041_basic_retrieval(self):
        """Test 1: Basic retrieval of reports submitted by delegate"""
        test_name = "Basic retrieval of reports submitted by delegate on behalf of manager"
        print(f"Test 1: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports?submitterLoginID=me',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            # Query for reports where submitter is the current delegate
            # Note: We'll search all reports first, then filter by submitter
            result = self.sdk.get_expense_reports(params={
                'limit': 100,
                'user': 'ALL'
            })
            
            if result['success']:
                all_reports = result.get('reports', [])
                
                # Filter for reports submitted by this delegate (not the owner)
                delegate_submitted = [
                    r for r in all_reports
                    if r.get('submitter_login_id') and 
                       r.get('submitter_login_id').lower() == self.delegate_login_id.lower() and
                       r.get('owner_login_id') and
                       r.get('owner_login_id').lower() != self.delegate_login_id.lower()
                ]
                
                test_result['passed'] = True
                test_result['response'] = {
                    'total_reports': len(all_reports),
                    'delegate_submitted_count': len(delegate_submitted),
                    'delegate_login_id': self.delegate_login_id,
                    'reports': delegate_submitted[:10]  # Sample first 10
                }
                
                print(f"  ✓ Successfully retrieved reports")
                print(f"  Total reports found: {len(all_reports)}")
                print(f"  Reports submitted by delegate: {len(delegate_submitted)}")
                print(f"  Delegate Login ID: {self.delegate_login_id}")
                
                if len(delegate_submitted) > 0:
                    print(f"\n  Sample Reports Submitted by Delegate (first 10):")
                    for i, report in enumerate(delegate_submitted[:10], 1):
                        print(f"\n  Report #{i}:")
                        print(f"    ID: {report.get('id')}")
                        print(f"    Name: {report.get('name')}")
                        print(f"    Owner: {report.get('owner_name')} ({report.get('owner_login_id')})")
                        print(f"    Submitter: {report.get('submitter_name')} ({report.get('submitter_login_id')})")
                        print(f"    Total: {report.get('currency_code', '')} {report.get('total', 0):.2f}")
                        print(f"    Status: {report.get('approval_status')} ({report.get('approval_status_code')})")
                        print(f"    Submission Date: {report.get('submission_date')}")
                else:
                    print(f"\n  ⚠️  No reports found submitted by this delegate on behalf of others")
                    print(f"\n  To create test data:")
                    print(f"    1. Log into Concur UI as delegate ({self.delegate_login_id})")
                    print(f"    2. Navigate to 'Expense' > 'Act On Behalf Of'")
                    print(f"    3. Select a manager/user to act on behalf of")
                    print(f"    4. Create and submit an expense report")
                    print(f"    5. The report owner will be the manager, submitter will be the delegate")
            else:
                test_result['passed'] = False
                test_result['error'] = result.get('error')
                print(f"  ✗ Failed to retrieve reports: {result.get('error')}")
            
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Test failed with exception: {str(e)}")
        
        self.results['tests'].append(test_result)
        print()
    
    def test_041_group_by_owner(self):
        """Test 2: Group delegate-submitted reports by owner (manager)"""
        test_name = "Group delegate-submitted reports by owner"
        print(f"Test 2: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports?submitterLoginID=me',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            # Get all reports
            result = self.sdk.get_expense_reports(params={
                'limit': 100,
                'user': 'ALL'
            })
            
            if result['success']:
                all_reports = result.get('reports', [])
                
                # Filter for delegate-submitted reports
                delegate_submitted = [
                    r for r in all_reports
                    if r.get('submitter_login_id') and 
                       r.get('submitter_login_id').lower() == self.delegate_login_id.lower() and
                       r.get('owner_login_id') and
                       r.get('owner_login_id').lower() != self.delegate_login_id.lower()
                ]
                
                # Group by owner
                by_owner = {}
                for report in delegate_submitted:
                    owner = report.get('owner_login_id', 'Unknown')
                    if owner not in by_owner:
                        by_owner[owner] = {
                            'owner_name': report.get('owner_name', 'Unknown'),
                            'reports': [],
                            'total_count': 0,
                            'total_amount': 0.0
                        }
                    by_owner[owner]['reports'].append(report)
                    by_owner[owner]['total_count'] += 1
                    by_owner[owner]['total_amount'] += report.get('total', 0)
                
                test_result['passed'] = True
                test_result['response'] = {
                    'delegate_submitted_count': len(delegate_submitted),
                    'unique_owners': len(by_owner),
                    'by_owner': {
                        owner: {
                            'owner_name': data['owner_name'],
                            'total_count': data['total_count'],
                            'total_amount': round(data['total_amount'], 2)
                        }
                        for owner, data in by_owner.items()
                    }
                }
                
                print(f"  ✓ Grouping analysis completed")
                print(f"  Reports submitted by delegate: {len(delegate_submitted)}")
                print(f"  Unique owners (managers): {len(by_owner)}")
                
                if by_owner:
                    print(f"\n  Reports by Owner:")
                    for owner, data in by_owner.items():
                        print(f"\n    Owner: {data['owner_name']} ({owner})")
                        print(f"      Reports: {data['total_count']}")
                        print(f"      Total Amount: ${data['total_amount']:.2f}")
                else:
                    print(f"\n  ⚠️  No reports to group")
            else:
                test_result['passed'] = False
                test_result['error'] = result.get('error')
                print(f"  ✗ Failed to retrieve reports: {result.get('error')}")
            
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Test failed with exception: {str(e)}")
        
        self.results['tests'].append(test_result)
        print()
    
    def test_041_status_breakdown(self):
        """Test 3: Analyze status breakdown of delegate-submitted reports"""
        test_name = "Analyze status breakdown of delegate-submitted reports"
        print(f"Test 3: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports?submitterLoginID=me',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.get_expense_reports(params={
                'limit': 100,
                'user': 'ALL'
            })
            
            if result['success']:
                all_reports = result.get('reports', [])
                
                # Filter for delegate-submitted reports
                delegate_submitted = [
                    r for r in all_reports
                    if r.get('submitter_login_id') and 
                       r.get('submitter_login_id').lower() == self.delegate_login_id.lower() and
                       r.get('owner_login_id') and
                       r.get('owner_login_id').lower() != self.delegate_login_id.lower()
                ]
                
                # Group by status
                by_status = {}
                for report in delegate_submitted:
                    status_code = report.get('approval_status_code', 'UNKNOWN')
                    status_name = report.get('approval_status', 'Unknown')
                    
                    if status_code not in by_status:
                        by_status[status_code] = {
                            'status_name': status_name,
                            'count': 0,
                            'reports': []
                        }
                    by_status[status_code]['count'] += 1
                    by_status[status_code]['reports'].append(report)
                
                test_result['passed'] = True
                test_result['response'] = {
                    'total_delegate_submitted': len(delegate_submitted),
                    'status_breakdown': {
                        code: {
                            'status_name': data['status_name'],
                            'count': data['count']
                        }
                        for code, data in by_status.items()
                    }
                }
                
                print(f"  ✓ Status analysis completed")
                print(f"  Total reports: {len(delegate_submitted)}")
                print(f"  Status breakdown:")
                
                if by_status:
                    for status_code, data in sorted(by_status.items(), key=lambda x: x[1]['count'], reverse=True):
                        print(f"    {status_code} ({data['status_name']}): {data['count']} reports")
                else:
                    print(f"    (No reports to analyze)")
            else:
                test_result['passed'] = False
                test_result['error'] = result.get('error')
                print(f"  ✗ Failed to retrieve reports: {result.get('error')}")
            
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Test failed with exception: {str(e)}")
        
        self.results['tests'].append(test_result)
        print()
    
    def test_041_filter_by_specific_manager(self):
        """Test 4: Filter reports for a specific manager/owner"""
        test_name = "Filter reports for a specific manager"
        print(f"Test 4: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports?user={managerID}&submitterLoginID=me',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            # First, get all delegate-submitted reports to find a manager
            result = self.sdk.get_expense_reports(params={
                'limit': 100,
                'user': 'ALL'
            })
            
            if result['success']:
                all_reports = result.get('reports', [])
                
                # Filter for delegate-submitted reports
                delegate_submitted = [
                    r for r in all_reports
                    if r.get('submitter_login_id') and 
                       r.get('submitter_login_id').lower() == self.delegate_login_id.lower() and
                       r.get('owner_login_id') and
                       r.get('owner_login_id').lower() != self.delegate_login_id.lower()
                ]
                
                if len(delegate_submitted) > 0:
                    # Pick the first manager found
                    target_manager = delegate_submitted[0].get('owner_login_id')
                    target_manager_name = delegate_submitted[0].get('owner_name')
                    
                    # Now query specifically for that manager
                    result_filtered = self.sdk.get_expense_reports(params={
                        'user': target_manager,
                        'limit': 100
                    })
                    
                    if result_filtered['success']:
                        manager_reports = result_filtered.get('reports', [])
                        
                        # Filter for those submitted by delegate
                        manager_delegate_reports = [
                            r for r in manager_reports
                            if r.get('submitter_login_id') and
                               r.get('submitter_login_id').lower() == self.delegate_login_id.lower()
                        ]
                        
                        test_result['passed'] = True
                        test_result['response'] = {
                            'target_manager': target_manager,
                            'target_manager_name': target_manager_name,
                            'total_manager_reports': len(manager_reports),
                            'delegate_submitted_for_manager': len(manager_delegate_reports),
                            'reports': manager_delegate_reports[:5]  # Sample first 5
                        }
                        
                        print(f"  ✓ Successfully filtered by manager")
                        print(f"  Target Manager: {target_manager_name} ({target_manager})")
                        print(f"  Total reports for manager: {len(manager_reports)}")
                        print(f"  Reports submitted by delegate for this manager: {len(manager_delegate_reports)}")
                        
                        if manager_delegate_reports:
                            print(f"\n  Sample Reports:")
                            for i, report in enumerate(manager_delegate_reports[:5], 1):
                                print(f"\n    Report #{i}:")
                                print(f"      ID: {report.get('id')}")
                                print(f"      Name: {report.get('name')}")
                                print(f"      Total: {report.get('currency_code', '')} {report.get('total', 0):.2f}")
                                print(f"      Status: {report.get('approval_status')} ({report.get('approval_status_code')})")
                    else:
                        test_result['passed'] = False
                        test_result['error'] = result_filtered.get('error')
                        print(f"  ✗ Failed to query by manager: {result_filtered.get('error')}")
                else:
                    # No delegate-submitted reports found
                    test_result['passed'] = True
                    test_result['response'] = {
                        'message': 'No delegate-submitted reports found to filter by manager'
                    }
                    print(f"  ⚠️  No delegate-submitted reports found to filter by manager")
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
        
        results_file = results_dir / 'test_041_results.json'
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"Results saved to: {results_file}")
        print()
        
        return self.results
    
    def run_all_tests(self):
        """Execute all tests"""
        if not self.setup():
            print("Setup failed. Cannot proceed with tests.")
            print()
            print("TROUBLESHOOTING:")
            print("  This test requires 'delegate_user' credentials in config/test_accounts.json")
            print("  Example configuration:")
            print('  {')
            print('    "environments": {')
            print('      "integration": {')
            print('        "accounts": {')
            print('          "delegate_user": {')
            print('            "username": "delegate@example.com",')
            print('            "password": "password",')
            print('            "role": "Delegate User"')
            print('          }')
            print('        }')
            print('      }')
            print('    }')
            print('  }')
            return False
        
        self.test_041_basic_retrieval()
        self.test_041_group_by_owner()
        self.test_041_status_breakdown()
        self.test_041_filter_by_specific_manager()
        
        self.generate_report()
        
        # Return True if all tests passed
        return self.results['summary']['failed'] == 0


if __name__ == "__main__":
    test_suite = TestDelegateSubmittedReports()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)

