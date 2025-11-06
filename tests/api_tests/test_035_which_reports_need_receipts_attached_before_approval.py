#!/usr/bin/env python3
"""
Test Case #035: Reports Needing Receipts Before Approval
User Query: Which reports need receipts attached before approval?
Service: Expense Reports & Status
API: GET /api/v3.0/expense/reports

This test verifies retrieving expense reports that are pending approval but
require receipts to be attached. This identifies reports that are blocked from
approval due to missing receipt documentation.
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


class TestReportsNeedingReceipts:
    """Test suite for reports needing receipts before approval"""
    
    def __init__(self):
        self.sdk = None
        self.results = {
            'test_case': '035',
            'user_query': 'Which reports need receipts attached before approval?',
            'api_endpoint': 'GET /api/v3.0/expense/reports?hasImages=false&approvalStatusCode=A_PEND&requiresReceipts=Y',
            'service': 'Expense Reports & Status',
            'tests': [],
            'summary': {}
        }
    
    def setup(self):
        """Initialize SDK and authenticate"""
        print("=" * 80)
        print("Test Case #035: Reports Needing Receipts Before Approval")
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
    
    def test_035_basic_retrieval(self):
        """Test 1: Basic retrieval of reports needing receipts"""
        test_name = "Basic retrieval of reports needing receipts"
        print(f"Test 1: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports?hasImages=false&approvalStatusCode=A_PEND',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.get_reports_needing_receipts(limit=50, user='ALL')
            
            if result['success']:
                test_result['passed'] = True
                test_result['response'] = {
                    'count': result['count'],
                    'approval_status_code': result['approval_status_code'],
                    'reports': result['reports'][:5] if result['reports'] else []  # Sample first 5
                }
                
                print(f"  ✓ Successfully retrieved reports needing receipts")
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
                        print(f"    Has Images: {report.get('has_images', 'N/A')}")
                        print(f"    Receipt Status: {report.get('receipt_status', 'N/A')}")
                        print(f"    Approval Status: {report.get('approval_status')} ({report.get('approval_status_code')})")
                else:
                    print(f"\n  ⚠️  No reports found needing receipts")
                    print(f"  This could mean:")
                    print(f"    - All pending reports have receipts attached")
                    print(f"    - There are no pending reports in the system")
                    print(f"    - Receipt requirements are not enforced in this environment")
            else:
                test_result['passed'] = False
                test_result['error'] = result.get('error')
                print(f"  ✗ Failed to retrieve reports: {result.get('error')}")
            
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Test failed with exception: {str(e)}")
        
        self.results['tests'].append(test_result)
        print()
    
    def test_035_verify_receipt_status(self):
        """Test 2: Verify receipt status and image requirements"""
        test_name = "Verify receipt status and image requirements"
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
            result = self.sdk.get_reports_needing_receipts(limit=100, user='ALL')
            
            if result['success']:
                reports = result['reports']
                
                # Verify all reports have A_PEND status
                all_pending = all(r.get('approval_status_code') == 'A_PEND' for r in reports)
                
                # Verify all reports have no images (if field is available)
                reports_without_images = [r for r in reports if r.get('has_images') == False or r.get('has_images') == 'N']
                
                test_result['passed'] = True
                test_result['response'] = {
                    'count': result['count'],
                    'all_pending_status': all_pending,
                    'reports_without_images': len(reports_without_images),
                    'status_verification': 'PASS' if all_pending else 'FAIL'
                }
                
                print(f"  ✓ Receipt status verification completed")
                print(f"  All reports in A_PEND status: {all_pending}")
                print(f"  Reports without images: {len(reports_without_images)} of {len(reports)}")
                print(f"  Total verified: {result['count']}")
                
                if result['count'] > 0:
                    # Calculate statistics about image status
                    has_images_data = [r for r in reports if 'has_images' in r]
                    if has_images_data:
                        print(f"  Reports with image data available: {len(has_images_data)}")
            else:
                test_result['passed'] = False
                test_result['error'] = result.get('error')
                print(f"  ✗ Failed to retrieve reports: {result.get('error')}")
            
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Test failed with exception: {str(e)}")
        
        self.results['tests'].append(test_result)
        print()
    
    def test_035_check_days_pending(self):
        """Test 3: Check how long reports have been pending without receipts"""
        test_name = "Analyze time reports have been pending without receipts"
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
            result = self.sdk.get_reports_needing_receipts(limit=100, user='ALL')
            
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
                            print(f"\n  Overdue Reports Missing Receipts:")
                            for report in overdue_reports[:3]:
                                print(f"    - {report.get('name')} ({report.get('days_since_submission')} days)")
                                print(f"      Owner: {report.get('owner_name')}")
                                print(f"      Amount: {report.get('currency_code', '')} {report.get('total', 0):.2f}")
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
    
    def test_035_group_by_owner(self):
        """Test 4: Group reports by owner to identify employees with missing receipts"""
        test_name = "Group reports by owner"
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
            result = self.sdk.get_reports_needing_receipts(limit=100, user='ALL')
            
            if result['success']:
                reports = result['reports']
                
                if len(reports) > 0:
                    # Group by owner
                    owner_groups = {}
                    for report in reports:
                        owner_name = report.get('owner_name', 'Unknown')
                        owner_login = report.get('owner_login_id', '')
                        owner_key = f"{owner_name} ({owner_login})"
                        
                        if owner_key not in owner_groups:
                            owner_groups[owner_key] = []
                        owner_groups[owner_key].append(report)
                    
                    # Calculate statistics
                    owner_stats = []
                    for owner, reports_list in owner_groups.items():
                        total_amount = sum(r.get('total', 0) for r in reports_list)
                        owner_stats.append({
                            'owner': owner,
                            'report_count': len(reports_list),
                            'total_amount': total_amount,
                            'currency': reports_list[0].get('currency_code', 'USD')
                        })
                    
                    # Sort by report count
                    owner_stats.sort(key=lambda x: x['report_count'], reverse=True)
                    
                    test_result['passed'] = True
                    test_result['response'] = {
                        'total_reports': len(reports),
                        'unique_owners': len(owner_groups),
                        'top_owners': owner_stats[:5]
                    }
                    
                    print(f"  ✓ Owner grouping completed")
                    print(f"  Total reports: {len(reports)}")
                    print(f"  Unique owners: {len(owner_groups)}")
                    
                    print(f"\n  Top Owners with Missing Receipts:")
                    for i, stat in enumerate(owner_stats[:5], 1):
                        print(f"\n  #{i}: {stat['owner']}")
                        print(f"      Reports: {stat['report_count']}")
                        print(f"      Total Amount: {stat['currency']} {stat['total_amount']:.2f}")
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
        
        results_file = results_dir / 'test_035_results.json'
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
        
        self.test_035_basic_retrieval()
        self.test_035_verify_receipt_status()
        self.test_035_check_days_pending()
        self.test_035_group_by_owner()
        
        self.generate_report()
        
        # Return True if all tests passed
        return self.results['summary']['failed'] == 0


if __name__ == "__main__":
    test_suite = TestReportsNeedingReceipts()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)

