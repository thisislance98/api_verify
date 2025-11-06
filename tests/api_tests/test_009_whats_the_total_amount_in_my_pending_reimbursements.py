#!/usr/bin/env python3
"""
Test Case #009: Pending Reimbursements Total
User Query: What's the total amount in my pending reimbursements?
Service: Expense Reports & Status
API: GET /expensereports/v4/reports

This test verifies the calculation of total pending reimbursements
by summing AmountDueEmployee for reports with approvalStatusId=A_PEND or A_APPR.
A_PEND = Submitted and awaiting approval
A_APPR = Approved and awaiting payment/extraction
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


class TestPendingReimbursementsTotal:
    """Test suite for pending reimbursements total endpoint"""
    
    def __init__(self):
        self.sdk = None
        self.user_id = None
        self.results = {
            'test_case': '009',
            'user_query': "What's the total amount in my pending reimbursements?",
            'api_endpoint': 'GET /expensereports/v4/reports',
            'service': 'Expense Reports & Status',
            'tests': [],
            'summary': {}
        }
    
    def setup(self):
        """Initialize SDK and authenticate"""
        print("=" * 80)
        print("Test Case #009: Pending Reimbursements Total")
        print("=" * 80)
        print()
        
        print("Setup: Initializing SDK...")
        try:
            # Load credentials from config
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
    
    def test_009_basic_pending_total(self):
        """Test 1: Basic retrieval of pending reimbursements total"""
        test_name = "Basic pending reimbursements total"
        print(f"Test 1: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': f'/expensereports/v4/users/{self.user_id}/context/TRAVELER/reports',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.get_pending_reimbursements_total()
            
            if result['success']:
                test_result['passed'] = True
                test_result['response'] = {
                    'total_pending': result['total_pending'],
                    'currency_code': result['currency_code'],
                    'report_count': result['count'],
                    'currency_codes': result.get('currency_codes', [])
                }
                
                print(f"  ✓ Request successful")
                print(f"  Total pending reimbursements: {result['total_pending']} {result['currency_code']}")
                print(f"  Number of pending reports: {result['count']}")
                
                if len(result.get('currency_codes', [])) > 1:
                    print(f"  ⚠ Multiple currencies detected: {', '.join(result['currency_codes'])}")
                
                if result['count'] > 0:
                    print(f"\n  Sample pending report:")
                    report = result['reports'][0]
                    print(f"    - Name: {report['name']}")
                    print(f"    - Report ID: {report['id']}")
                    print(f"    - Status: {report.get('approval_status', 'N/A')}")
                    print(f"    - Amount Due: {report.get('amount_due_employee', 'N/A')} {report.get('currency_code', '')}")
                else:
                    print(f"  ℹ No pending reimbursements found")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_009_verify_calculation(self):
        """Test 2: Verify the sum calculation is correct"""
        test_name = "Verify sum calculation"
        print(f"Test 2: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.get_pending_reimbursements_total()
            
            if result['success']:
                # Manually calculate the sum to verify
                manual_sum = sum(
                    report.get('amount_due_employee', 0) 
                    for report in result['reports']
                )
                
                # Allow for small floating point differences
                difference = abs(result['total_pending'] - manual_sum)
                tolerance = 0.01
                
                if difference < tolerance:
                    test_result['passed'] = True
                    test_result['response'] = {
                        'api_total': result['total_pending'],
                        'manual_total': manual_sum,
                        'difference': difference,
                        'match': True
                    }
                    print(f"  ✓ Calculation verified")
                    print(f"  API Total: {result['total_pending']}")
                    print(f"  Manual Sum: {manual_sum}")
                    print(f"  Difference: {difference}")
                else:
                    test_result['error'] = f"Calculation mismatch: API={result['total_pending']}, Manual={manual_sum}"
                    test_result['response'] = {
                        'api_total': result['total_pending'],
                        'manual_total': manual_sum,
                        'difference': difference,
                        'match': False
                    }
                    print(f"  ✗ Calculation mismatch")
                    print(f"  API Total: {result['total_pending']}")
                    print(f"  Manual Sum: {manual_sum}")
                    print(f"  Difference: {difference}")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_009_filter_status_verification(self):
        """Test 3: Verify only A_PEND and A_APPR reports are included"""
        test_name = "Status filter verification"
        print(f"Test 3: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'validations': [],
            'error': None
        }
        
        try:
            result = self.sdk.get_pending_reimbursements_total()
            
            if result['success']:
                validations = []
                all_valid = True
                
                # Check that all returned reports have A_PEND or A_APPR status
                for report in result['reports']:
                    status = report.get('approval_status', '').upper()
                    is_valid = status in ['A_PEND', 'A_APPR']
                    
                    if not is_valid:
                        all_valid = False
                        validations.append({
                            'report_id': report.get('id'),
                            'report_name': report.get('name'),
                            'status': status,
                            'valid': False
                        })
                        print(f"  ✗ Invalid status found: {status} for report {report.get('name')}")
                
                if all_valid:
                    test_result['passed'] = True
                    test_result['response'] = {
                        'all_reports_valid': True,
                        'total_reports_checked': len(result['reports'])
                    }
                    print(f"  ✓ All reports have valid status (A_PEND or A_APPR)")
                    print(f"  Total reports checked: {len(result['reports'])}")
                    
                    # Show status distribution
                    status_counts = {}
                    for report in result['reports']:
                        status = report.get('approval_status', 'UNKNOWN').upper()
                        status_counts[status] = status_counts.get(status, 0) + 1
                    
                    print(f"  Status distribution:")
                    for status, count in status_counts.items():
                        print(f"    - {status}: {count} reports")
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
    
    def test_009_response_structure(self):
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
            result = self.sdk.get_pending_reimbursements_total()
            
            validations = []
            
            # Check required fields in response
            required_fields = [
                'success', 'total_pending', 'currency_code', 
                'currency_codes', 'reports', 'count', 'message'
            ]
            
            for field in required_fields:
                if field in result:
                    validations.append({'field': field, 'present': True})
                else:
                    validations.append({'field': field, 'present': False})
            
            # Validate data types
            if 'total_pending' in result:
                if isinstance(result['total_pending'], (int, float)):
                    validations.append({'field': 'total_pending (numeric)', 'present': True})
                else:
                    validations.append({'field': 'total_pending (numeric)', 'present': False})
            
            if 'reports' in result and isinstance(result['reports'], list):
                validations.append({'field': 'reports (array)', 'present': True})
            else:
                validations.append({'field': 'reports (array)', 'present': False})
            
            # If we have reports, validate report structure
            if result.get('count', 0) > 0:
                report = result['reports'][0]
                report_fields = ['id', 'name', 'approval_status', 'amount_due_employee']
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
        results_file = Path(__file__).parent / "results" / "test_009_results.json"
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
        self.test_009_basic_pending_total()
        self.test_009_verify_calculation()
        self.test_009_filter_status_verification()
        self.test_009_response_structure()
        
        # Generate report
        return self.generate_report()


def main():
    """Main test execution"""
    test_suite = TestPendingReimbursementsTotal()
    success = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

