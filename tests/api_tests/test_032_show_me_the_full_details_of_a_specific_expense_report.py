#!/usr/bin/env python3
"""
Test Case #032: Full Details of Specific Expense Report
User Query: Show me the full details of a specific expense report
Service: Expense Reports & Status
API: GET /api/expense/expensereport/v2.0/report/{reportId}

This test verifies retrieval of complete expense report details using the V2.0 API.
The V2.0 API returns comprehensive information including:
- Report header fields (name, purpose, amounts, status)
- All expense entries with transaction details
- Expense allocations
- Workflow information and approver details
- Custom fields
- Receipts and attachments metadata
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


class TestReportFullDetails:
    """Test suite for retrieving full expense report details"""
    
    def __init__(self):
        self.sdk = None
        self.user_id = None
        self.test_report_id = None
        self.results = {
            'test_case': '032',
            'user_query': 'Show me the full details of a specific expense report',
            'api_endpoint': 'GET /api/expense/expensereport/v2.0/report/{reportId}',
            'service': 'Expense Reports & Status',
            'tests': [],
            'summary': {}
        }
    
    def setup(self):
        """Initialize SDK and authenticate"""
        print("=" * 80)
        print("Test Case #032: Full Details of Specific Expense Report")
        print("=" * 80)
        print()
        
        print("Setup: Initializing SDK...")
        try:
            # Load credentials from config - using manager_approver to see all reports
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
    
    def find_test_report(self):
        """Find a report to test with"""
        print("Finding a test report...")
        print("-" * 80)
        
        try:
            # Get any available report
            params = {
                'user': 'ALL',
                'limit': 5
            }
            
            result = self.sdk.get_expense_reports(params=params)
            
            if result['success'] and result['count'] > 0:
                # Use the first report we find
                report = result['reports'][0]
                self.test_report_id = report['ID']
                
                print(f"  ✓ Found test report")
                print(f"  Report ID: {self.test_report_id}")
                print(f"  Report Name: {report['ReportName']}")
                print(f"  Owner: {report['OwnerName']}")
                print(f"  Total: ${report['Total']:,.2f} {report['CurrencyCode']}")
                print(f"  Status: {report['ApprovalStatusName']}")
                print()
                return True
            else:
                print(f"  ✗ No reports found to test with")
                print(f"  Note: Please create some expense reports first")
                print()
                return False
                
        except Exception as e:
            print(f"  ✗ Error finding test report: {str(e)}")
            print()
            return False
    
    def test_032_get_full_report_details(self):
        """Test 1: Retrieve full details of a specific report"""
        test_name = "Get full report details using V2.0 API"
        print(f"Test 1: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': f'/api/expense/expensereport/v2.0/report/{self.test_report_id}',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            if not self.test_report_id:
                test_result['error'] = 'No test report ID available'
                print(f"  ✗ No test report ID available")
                print()
                self.results['tests'].append(test_result)
                return False
            
            result = self.sdk.get_report_full_details(self.test_report_id)
            
            if result['success']:
                summary = result['summary']
                report = result['report']
                
                test_result['passed'] = True
                test_result['response'] = {
                    'report_id': self.test_report_id,
                    'summary': summary
                }
                
                print(f"  ✓ Successfully retrieved full report details")
                print(f"\n  Report Summary:")
                print(f"    - Report Name: {summary['report_name']}")
                print(f"    - Owner: {summary['owner_name']} ({summary['owner_login_id']})")
                print(f"    - Total: ${summary['report_total']:,.2f} {summary['currency_code']}")
                print(f"    - Approval Status: {summary['approval_status_name']}")
                print(f"    - Payment Status: {summary['payment_status_name']}")
                print(f"    - Business Purpose: {summary['business_purpose'][:100] if summary['business_purpose'] else 'N/A'}")
                print(f"    - Country: {summary['country']}")
                print(f"    - Created: {summary['create_date']}")
                print(f"    - Submitted: {summary['submit_date']}")
                if summary['approved_date']:
                    print(f"    - Approved: {summary['approved_date']}")
                print(f"    - Has Exception: {summary['has_exception']}")
                print(f"    - Expense Entries: {summary['expense_entries_count']}")
                
                # Show expense entries if available
                expense_entries = report.get('ExpenseEntriesList', [])
                if expense_entries:
                    print(f"\n  Expense Entries ({len(expense_entries)}):")
                    for i, entry in enumerate(expense_entries[:5], 1):
                        expense_type = entry.get('ExpenseTypeName', 'Unknown')
                        # Handle both string and numeric amounts
                        transaction_amount = entry.get('TransactionAmount', 0)
                        if isinstance(transaction_amount, str):
                            try:
                                transaction_amount = float(transaction_amount)
                            except (ValueError, TypeError):
                                transaction_amount = 0.0
                        
                        posted_amount = entry.get('PostedAmount', 0)
                        if isinstance(posted_amount, str):
                            try:
                                posted_amount = float(posted_amount)
                            except (ValueError, TypeError):
                                posted_amount = 0.0
                        
                        transaction_currency = entry.get('TransactionCurrencyCode', '')
                        vendor = entry.get('VendorDescription', 'N/A')
                        # V2.0 API might use different field names for date
                        expense_date = entry.get('TransactionDate', entry.get('ExpenseDate', 'N/A'))
                        
                        print(f"    {i}. {expense_type}")
                        print(f"       Amount: {transaction_amount:,.2f} {transaction_currency} (Posted: {posted_amount:,.2f})")
                        print(f"       Vendor: {vendor}")
                        print(f"       Date: {expense_date}")
                        
                        # Show allocations if present
                        allocations = entry.get('Allocations', [])
                        if allocations:
                            print(f"       Allocations: {len(allocations)}")
                            for j, alloc in enumerate(allocations[:2], 1):
                                custom_data = alloc.get('Custom1', {})
                                if isinstance(custom_data, dict):
                                    custom_label = custom_data.get('Label', 'Custom1')
                                    custom_value = custom_data.get('Value', 'N/A')
                                else:
                                    custom_label = 'Custom1'
                                    custom_value = str(custom_data) if custom_data else 'N/A'
                                print(f"         {j}. {custom_label}: {custom_value}")
                    
                    if len(expense_entries) > 5:
                        print(f"    ... and {len(expense_entries) - 5} more entries")
                
                # Show custom fields if available
                custom_fields = summary['custom_fields']
                if custom_fields:
                    print(f"\n  Custom Fields ({len(custom_fields)}):")
                    for field in custom_fields[:5]:
                        if isinstance(field, dict):
                            label = field.get('Label', 'Unknown')
                            value = field.get('Value', 'N/A')
                            print(f"    - {label}: {value}")
                    if len(custom_fields) > 5:
                        print(f"    ... and {len(custom_fields) - 5} more fields")
                
            else:
                test_result['error'] = result.get('error', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                if 'message' in result:
                    print(f"  Message: {result['message']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_032_verify_response_structure(self):
        """Test 2: Verify complete response structure includes expected fields"""
        test_name = "Verify V2.0 API response structure"
        print(f"Test 2: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'validations': [],
            'error': None
        }
        
        try:
            if not self.test_report_id:
                test_result['error'] = 'No test report ID available'
                print(f"  ✗ No test report ID available")
                print()
                self.results['tests'].append(test_result)
                return False
            
            result = self.sdk.get_report_full_details(self.test_report_id)
            
            if not result['success']:
                test_result['error'] = result.get('error', 'Request failed')
                print(f"  ✗ Could not retrieve report: {test_result['error']}")
                print()
                self.results['tests'].append(test_result)
                return False
            
            report = result['report']
            validations = []
            
            # Check essential report header fields (V2.0 API names)
            header_fields = [
                'ReportName', 'ReportID', 'ReportTotal', 'CurrencyCode',
                'ApprovalStatusName', 'PaymentStatusName', 'EmployeeName', 
                'UserLoginID', 'ReportDate', 'ReportPurpose'
            ]
            
            print(f"  Checking report header fields:")
            for field in header_fields:
                present = field in report
                status = "✓" if present else "✗"
                validations.append({'field': field, 'present': present, 'category': 'header'})
                print(f"    {status} {field}: {present}")
            
            # Check for expense entries structure
            print(f"\n  Checking expense entries structure:")
            has_entries = 'ExpenseEntriesList' in report
            validations.append({'field': 'ExpenseEntriesList', 'present': has_entries, 'category': 'entries'})
            print(f"    {'✓' if has_entries else '✗'} ExpenseEntriesList: {has_entries}")
            
            if has_entries and len(report.get('ExpenseEntriesList', [])) > 0:
                entry = report['ExpenseEntriesList'][0]
                # V2.0 API field names for entries
                entry_fields = ['ExpenseTypeName', 'TransactionAmount', 'TransactionCurrencyCode', 
                               'PostedAmount', 'TransactionDate', 'VendorDescription']
                
                for field in entry_fields:
                    present = field in entry
                    status = "✓" if present else "✗"
                    validations.append({'field': f'entry.{field}', 'present': present, 'category': 'entry'})
                    print(f"    {status} entry.{field}: {present}")
            
            # Check for workflow information
            print(f"\n  Checking workflow fields:")
            workflow_fields = ['WorkflowActionURL', 'ApproverLoginID', 'ApproverName']
            for field in workflow_fields:
                present = field in report
                status = "✓" if present else "✗"
                validations.append({'field': field, 'present': present, 'category': 'workflow'})
                print(f"    {status} {field}: {present}")
            
            test_result['validations'] = validations
            
            # Consider test passed if we have core fields
            core_validations = [v for v in validations if v['category'] in ['header', 'entries']]
            passed_count = sum(1 for v in core_validations if v['present'])
            total_count = len(core_validations)
            
            test_result['passed'] = passed_count >= (total_count * 0.8)  # 80% threshold
            
            print(f"\n  Validation Score: {passed_count}/{total_count} core fields present")
            
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_032_invalid_report_id(self):
        """Test 3: Verify proper error handling for invalid report ID"""
        test_name = "Error handling for invalid report ID"
        print(f"Test 3: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            # Use an obviously invalid report ID
            invalid_id = "INVALID_REPORT_ID_12345"
            
            result = self.sdk.get_report_full_details(invalid_id)
            
            # Should return success=False for invalid ID
            if not result['success']:
                test_result['passed'] = True
                test_result['response'] = {
                    'handled_gracefully': True,
                    'error_message': result.get('error', ''),
                    'report_id': invalid_id
                }
                
                print(f"  ✓ Invalid report ID handled gracefully")
                print(f"  Error: {result.get('error', 'N/A')}")
                print(f"  Message: {result.get('message', 'N/A')}")
            else:
                test_result['error'] = 'API should have returned error for invalid report ID'
                print(f"  ✗ Invalid report ID was not rejected")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_032_compare_v2_vs_v3(self):
        """Test 4: Compare V2.0 detailed response with V3.0 summary response"""
        test_name = "Compare V2.0 vs V3.0 API responses"
        print(f"Test 4: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'comparison': None,
            'error': None
        }
        
        try:
            if not self.test_report_id:
                test_result['error'] = 'No test report ID available'
                print(f"  ✗ No test report ID available")
                print()
                self.results['tests'].append(test_result)
                return False
            
            # Get V2.0 details
            v2_result = self.sdk.get_report_full_details(self.test_report_id)
            
            # Get V3.0 summary (from list)
            v3_params = {'user': 'ALL', 'limit': 100}
            v3_result = self.sdk.get_expense_reports(params=v3_params)
            
            if v2_result['success'] and v3_result['success']:
                # Find matching report in V3 results
                v3_report = None
                for report in v3_result['reports']:
                    if report['ID'] == self.test_report_id:
                        v3_report = report
                        break
                
                if v3_report:
                    v2_summary = v2_result['summary']
                    
                    comparison = {
                        'v2_fields_count': len(v2_result['report'].keys()),
                        'v3_fields_count': len(v3_report.keys()),
                        'v2_has_entries': v2_summary['expense_entries_count'] > 0,
                        'v2_entries_count': v2_summary['expense_entries_count'],
                        'report_name_match': v2_summary['report_name'] == v3_report['ReportName'],
                        'total_match': abs(float(v2_summary['report_total']) - float(v3_report['Total'])) < 0.01
                    }
                    
                    test_result['passed'] = True
                    test_result['comparison'] = comparison
                    
                    print(f"  ✓ Comparison complete")
                    print(f"\n  V2.0 API (Detailed):")
                    print(f"    - Total fields: {comparison['v2_fields_count']}")
                    print(f"    - Includes entries: {comparison['v2_has_entries']}")
                    print(f"    - Entry count: {comparison['v2_entries_count']}")
                    print(f"\n  V3.0 API (Summary):")
                    print(f"    - Total fields: {comparison['v3_fields_count']}")
                    print(f"    - Includes entries: No")
                    print(f"\n  Data Consistency:")
                    print(f"    - Report Name Match: {'✓' if comparison['report_name_match'] else '✗'}")
                    print(f"    - Total Amount Match: {'✓' if comparison['total_match'] else '✗'}")
                    print(f"\n  Conclusion:")
                    print(f"    V2.0 API provides {comparison['v2_fields_count']} fields vs V3.0's {comparison['v3_fields_count']} fields")
                    print(f"    V2.0 includes detailed expense entries and allocations")
                    print(f"    V3.0 is suitable for listing/filtering, V2.0 for detailed inspection")
                else:
                    test_result['error'] = 'Could not find matching report in V3 results'
                    print(f"  ✗ Could not find matching report in V3 results")
            else:
                error_msg = v2_result.get('error') or v3_result.get('error')
                test_result['error'] = f'API request failed: {error_msg}'
                print(f"  ✗ API request failed: {error_msg}")
                
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
            'timestamp': datetime.now().isoformat(),
            'test_report_id': self.test_report_id
        }
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {self.results['summary']['success_rate']}")
        if self.test_report_id:
            print(f"Test Report ID: {self.test_report_id}")
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
        results_file = Path(__file__).parent / "results" / "test_032_results.json"
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
        
        # Find a test report to use
        if not self.find_test_report():
            print("⚠ Warning: No test reports available")
            print("Please create some expense reports in Concur before running this test")
            return False
        
        # Run tests
        self.test_032_get_full_report_details()
        self.test_032_verify_response_structure()
        self.test_032_invalid_report_id()
        self.test_032_compare_v2_vs_v3()
        
        # Generate report
        return self.generate_report()


def main():
    """Main test execution"""
    test_suite = TestReportFullDetails()
    success = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

