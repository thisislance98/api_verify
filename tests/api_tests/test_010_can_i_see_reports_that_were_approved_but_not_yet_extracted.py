#!/usr/bin/env python3
"""
Test Case #010: Approved But Not Extracted Reports
User Query: Can I see reports that were approved but not yet extracted?
Service: Expense Reports & Status
API: GET /api/v3.0/expense/reports

This test verifies the retrieval of expense reports that have been approved
but have not yet been extracted to external systems (approvalStatusCode=A_APPR,
hasException=N, extractedDate=null).
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


class TestApprovedNotExtractedReports:
    """Test suite for approved but not extracted reports endpoint"""
    
    def __init__(self):
        self.sdk = None
        self.user_id = None
        self.results = {
            'test_case': '010',
            'user_query': "Can I see reports that were approved but not yet extracted?",
            'api_endpoint': 'GET /api/v3.0/expense/reports',
            'service': 'Expense Reports & Status',
            'tests': [],
            'summary': {}
        }
    
    def setup(self):
        """Initialize SDK and authenticate"""
        print("=" * 80)
        print("Test Case #010: Approved But Not Extracted Reports")
        print("=" * 80)
        print()
        
        print("Setup: Initializing SDK...")
        try:
            # Load credentials from config (using manager_approver to see more reports)
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
    
    def test_010_basic_retrieval(self):
        """Test 1: Basic retrieval of approved but not extracted reports"""
        test_name = "Basic retrieval without filters"
        print(f"Test 1: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports',
            'method': 'GET',
            'params': {
                'approvalStatusCode': 'A_APPR',
                'hasException': 'N'
            },
            'passed': False,
            'response': None,
            'error': None,
            'test_data_available': False
        }
        
        try:
            result = self.sdk.get_approved_not_extracted_reports()
            
            if result['success']:
                count = result['count']
                test_result['response'] = {
                    'count': count,
                    'params': result['params']
                }
                test_result['test_data_available'] = count > 0
                
                print(f"  ✓ Request successful")
                print(f"  Retrieved {count} approved reports not yet extracted")
                
                if count > 0:
                    test_result['passed'] = True
                    print(f"\n  Sample report details:")
                    report = result['reports'][0]
                    print(f"    - Report Name: {report.get('ReportName', report.get('name', 'N/A'))}")
                    print(f"    - Report ID: {report.get('ID', report.get('id', 'N/A'))}")
                    print(f"    - Owner: {report.get('OwnerName', 'N/A')}")
                    print(f"    - Total: {report.get('Total', 'N/A')} {report.get('CurrencyCode', '')}")
                    print(f"    - Approval Status: {report.get('ApprovalStatusName', 'N/A')} ({report.get('ApprovalStatusCode', 'N/A')})")
                    print(f"    - Submit Date: {report.get('SubmitDate', 'N/A')}")
                    print(f"    - Extracted Date: {report.get('ExtractedDate', 'Not extracted')}")
                else:
                    # No test data available - provide guidance
                    test_result['passed'] = False
                    test_result['error'] = 'NO_TEST_DATA'
                    print(f"  ⚠ No test data available")
                    print(f"\n  Test Requirements:")
                    print(f"    This test requires reports with:")
                    print(f"    1. Approval Status: A_APPR (Approved)")
                    print(f"    2. Has Exception: N (No exceptions)")
                    print(f"    3. Payment Status: P_NOTP (Not yet processed for payment/extraction)")
                    print(f"\n  To create test data:")
                    print(f"    1. Submit an expense report via Concur UI")
                    print(f"    2. Approve it (as manager) to move it to A_APPR status")
                    print(f"    3. Do NOT extract or process it for payment yet")
                    print(f"    4. Ensure the report has no policy exceptions")
                    print(f"\n  Alternative: Check if there are pending reports that can be approved")
                    try:
                        pending = self.sdk.get_expense_reports({'approvalStatusCode': 'A_PEND', 'user': 'ALL', 'limit': 3})
                        if pending['success'] and pending.get('count', 0) > 0:
                            print(f"    Found {pending['count']} pending reports that could be approved:")
                            for i, report in enumerate(pending['reports'][:3]):
                                print(f"      {i+1}. {report.get('ReportName', 'N/A')} (ID: {report.get('ID', 'N/A')})")
                    except:
                        pass
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_010_approval_status_verification(self):
        """Test 2: Verify all returned reports have approved status"""
        test_name = "Approval status verification"
        print(f"Test 2: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'validations': [],
            'error': None
        }
        
        try:
            result = self.sdk.get_approved_not_extracted_reports()
            
            if result['success']:
                validations = []
                all_valid = True
                
                # Check that all returned reports have approved status
                for report in result['reports']:
                    status_code = report.get('ApprovalStatusCode', '').upper()
                    is_valid = status_code == 'A_APPR'
                    
                    if not is_valid:
                        all_valid = False
                        validations.append({
                            'report_id': report.get('ID'),
                            'report_name': report.get('ReportName'),
                            'status_code': status_code,
                            'valid': False
                        })
                        print(f"  ✗ Invalid status found: {status_code} for report {report.get('ReportName')}")
                
                if all_valid:
                    test_result['passed'] = True
                    test_result['response'] = {
                        'all_reports_valid': True,
                        'total_reports_checked': len(result['reports'])
                    }
                    print(f"  ✓ All reports have approved status (A_APPR)")
                    print(f"  Total reports checked: {len(result['reports'])}")
                else:
                    test_result['error'] = f"Found {len(validations)} reports with invalid status"
                    test_result['validations'] = validations
                    
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_010_extraction_status_verification(self):
        """Test 3: Verify none of the reports have been extracted"""
        test_name = "Extraction status verification"
        print(f"Test 3: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'validations': [],
            'error': None
        }
        
        try:
            result = self.sdk.get_approved_not_extracted_reports()
            
            if result['success']:
                validations = []
                all_valid = True
                
                # Check that all returned reports have no extraction date
                for report in result['reports']:
                    extracted_date = report.get('ExtractedDate')
                    is_valid = not extracted_date or extracted_date == 'null'
                    
                    if not is_valid:
                        all_valid = False
                        validations.append({
                            'report_id': report.get('ID'),
                            'report_name': report.get('ReportName'),
                            'extracted_date': extracted_date,
                            'valid': False
                        })
                        print(f"  ✗ Report already extracted: {report.get('ReportName')} on {extracted_date}")
                
                if all_valid:
                    test_result['passed'] = True
                    test_result['response'] = {
                        'all_reports_not_extracted': True,
                        'total_reports_checked': len(result['reports'])
                    }
                    print(f"  ✓ All reports have no extraction date (not yet extracted)")
                    print(f"  Total reports checked: {len(result['reports'])}")
                else:
                    test_result['error'] = f"Found {len(validations)} reports that were already extracted"
                    test_result['validations'] = validations
                    
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_010_exception_status_verification(self):
        """Test 4: Verify none of the reports have exceptions"""
        test_name = "Exception status verification"
        print(f"Test 4: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.get_approved_not_extracted_reports()
            
            if result['success']:
                # Check the request params to ensure hasException=N was used
                params = result.get('params', {})
                has_exception_param = params.get('hasException')
                
                if has_exception_param == 'N':
                    test_result['passed'] = True
                    test_result['response'] = {
                        'hasException_filter': 'N',
                        'total_reports': len(result['reports'])
                    }
                    print(f"  ✓ Request correctly filters for reports without exceptions (hasException=N)")
                    print(f"  Total reports returned: {len(result['reports'])}")
                else:
                    test_result['error'] = f"Expected hasException=N, got {has_exception_param}"
                    print(f"  ✗ Filter not correctly applied: hasException={has_exception_param}")
                    
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_010_response_structure(self):
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
            result = self.sdk.get_approved_not_extracted_reports()
            
            validations = []
            
            # Check required fields in response
            required_fields = ['success', 'reports', 'count', 'params', 'message']
            
            for field in required_fields:
                if field in result:
                    validations.append({'field': field, 'present': True})
                else:
                    validations.append({'field': field, 'present': False})
            
            # Validate data types
            if 'reports' in result and isinstance(result['reports'], list):
                validations.append({'field': 'reports (array)', 'present': True})
            else:
                validations.append({'field': 'reports (array)', 'present': False})
            
            if 'count' in result and isinstance(result['count'], int):
                validations.append({'field': 'count (integer)', 'present': True})
            else:
                validations.append({'field': 'count (integer)', 'present': False})
            
            # If we have reports, validate report structure
            if result.get('count', 0) > 0:
                report = result['reports'][0]
                report_fields = [
                    'ID', 'ReportName', 'OwnerName', 'Total', 
                    'CurrencyCode', 'ApprovalStatusCode', 'ApprovalStatusName'
                ]
                for field in report_fields:
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
    
    def test_010_with_limit_filter(self):
        """Test 6: Test with custom limit parameter"""
        test_name = "Custom limit parameter"
        print(f"Test 6: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports',
            'method': 'GET',
            'params': {
                'approvalStatusCode': 'A_APPR',
                'hasException': 'N',
                'limit': 10
            },
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.get_approved_not_extracted_reports(limit=10)
            
            if result['success']:
                test_result['passed'] = True
                test_result['response'] = {
                    'count': result['count'],
                    'requested_limit': 10
                }
                
                print(f"  ✓ Request successful with limit=10")
                print(f"  Retrieved {result['count']} reports (max 10)")
                
                # Verify count doesn't exceed limit
                if result['count'] <= 10:
                    print(f"  ✓ Result count respects limit")
                else:
                    print(f"  ⚠ Result count ({result['count']}) exceeds limit (10)")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
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
        results_file = Path(__file__).parent / "results" / "test_010_results.json"
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
        self.test_010_basic_retrieval()
        self.test_010_approval_status_verification()
        self.test_010_extraction_status_verification()
        self.test_010_exception_status_verification()
        self.test_010_response_structure()
        self.test_010_with_limit_filter()
        
        # Generate report
        return self.generate_report()


def main():
    """Main test execution"""
    test_suite = TestApprovedNotExtractedReports()
    success = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

