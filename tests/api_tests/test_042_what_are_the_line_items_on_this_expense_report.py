#!/usr/bin/env python3
"""
Test Case #042: Line Items on Expense Report
User Query: What are the line items on this expense report?
Service: Expense Entries & Details
API: GET /expensereports/v4/reports/{reportId}/expenses

This test verifies retrieval of expense line items (entries) for a specific report.
Uses the V4 API to fetch detailed expense information including amounts, vendors,
transaction dates, and other entry-level details.
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


class TestReportLineItems:
    """Test suite for retrieving expense line items from a report"""
    
    def __init__(self):
        self.sdk = None
        self.user_id = None
        self.test_report_id = None
        self.results = {
            'test_case': '042',
            'user_query': 'What are the line items on this expense report?',
            'api_endpoint': 'GET /expensereports/v4/reports/{reportId}/expenses',
            'service': 'Expense Entries & Details',
            'tests': [],
            'summary': {}
        }
    
    def setup(self):
        """Initialize SDK and authenticate"""
        print("=" * 80)
        print("Test Case #042: Line Items on Expense Report")
        print("=" * 80)
        print()
        
        print("Setup: Initializing SDK...")
        try:
            # Load credentials from config - using expense_user to access own reports
            # Note: We use expense_user instead of manager because we need to access
            # the user's own reports to retrieve line items (permission requirement)
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
            
            # Find a report with expenses to test - use own reports to avoid permission issues
            print(f"\n  Finding own reports with expenses to test...")
            # First try to get user's own reports
            reports_result = self.sdk.get_expense_reports(params={'user': 'me', 'limit': 50})
            
            if reports_result['success'] and reports_result['count'] > 0:
                # Try to find a report that likely has expenses (any status with positive total)
                for report in reports_result['reports']:
                    total = float(report.get('Total', 0))
                    
                    # Look for reports that have a positive total (likely have expenses)
                    if total > 0:
                        self.test_report_id = report['ID']
                        print(f"  ✓ Selected test report: {report['ReportName']}")
                        print(f"    - Report ID: {self.test_report_id}")
                        print(f"    - Owner: {report['OwnerName']}")
                        print(f"    - Total: ${total:.2f} {report['CurrencyCode']}")
                        print(f"    - Status: {report['ApprovalStatusName']}")
                        break
                
                # If no suitable report found, use the first one
                if not self.test_report_id:
                    first_report = reports_result['reports'][0]
                    self.test_report_id = first_report['ID']
                    print(f"  ✓ Using first available report: {first_report['ReportName']}")
                    print(f"    - Report ID: {self.test_report_id}")
                    print(f"    - Status: {first_report['ApprovalStatusName']}")
            else:
                # No own reports found, create a test report with expenses
                print(f"  ℹ No existing reports found for this user")
                print(f"  ℹ Creating a test report with sample expenses...")
                
                from datetime import datetime
                report_name = f"Test Report - Line Items {datetime.now().strftime('%Y%m%d_%H%M%S')}"
                create_result = self.sdk.create_report(
                    name=report_name,
                    purpose="Test report for line items test - created by automated test 042"
                )
                
                if create_result['success']:
                    self.test_report_id = create_result['report_id']
                    print(f"  ✓ Created test report: {report_name}")
                    print(f"    - Report ID: {self.test_report_id}")
                    
                    # Add a couple of sample expenses
                    print(f"  ℹ Adding sample expenses to report...")
                    
                    # Sample expense 1: Parking
                    expense1 = self.sdk.create_expense(
                        report_id=self.test_report_id,
                        expense_type="PARKN",
                        amount=25.00,
                        currency_code="USD",
                        transaction_date=datetime.now().strftime("%Y-%m-%d"),
                        business_purpose="Client meeting parking",
                        vendor_description="Downtown Parking Garage",
                        city_name="Chicago",
                        country_code="US"
                    )
                    
                    if expense1.get('success'):
                        print(f"    ✓ Added parking expense: $25.00")
                    
                    # Sample expense 2: Meal
                    expense2 = self.sdk.create_expense(
                        report_id=self.test_report_id,
                        expense_type="MEALS",
                        amount=45.00,
                        currency_code="USD",
                        transaction_date=datetime.now().strftime("%Y-%m-%d"),
                        business_purpose="Client lunch",
                        vendor_description="Restaurant ABC",
                        city_name="Chicago",
                        country_code="US"
                    )
                    
                    if expense2.get('success'):
                        print(f"    ✓ Added meal expense: $45.00")
                    
                    print(f"  ✓ Test report ready with sample expenses")
                else:
                    raise Exception(f"Could not create test report: {create_result.get('message', 'Unknown error')}")
            
            print()
            return True
            
        except Exception as e:
            print(f"  ✗ Setup failed: {str(e)}")
            return False
    
    def test_042_basic_retrieval_line_items(self):
        """Test 1: Retrieve line items from a report"""
        test_name = "Basic retrieval of expense line items"
        print(f"Test 1: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': f'/expensereports/v4/reports/{self.test_report_id}/expenses',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            # Get expenses for the test report
            result = self.sdk.list_expenses(self.test_report_id)
            
            if result['success']:
                expenses = result['expenses']
                
                test_result['passed'] = True
                test_result['response'] = {
                    'report_id': self.test_report_id,
                    'expense_count': result['count'],
                    'api_version': result['api_version']
                }
                
                print(f"  ✓ Request successful")
                print(f"  Report ID: {self.test_report_id}")
                print(f"  Number of line items: {result['count']}")
                print(f"  API Version: {result['api_version']}")
                
                if result['count'] > 0:
                    print(f"\n  Expense line items:")
                    total_amount = 0
                    
                    for i, expense in enumerate(expenses, 1):
                        print(f"    {i}. {expense.get('expense_type', 'Unknown Type')}")
                        print(f"       - Expense ID: {expense.get('id', 'N/A')}")
                        
                        amount = expense.get('transaction_amount', 0)
                        currency = expense.get('transaction_currency_code', 'USD')
                        if amount:
                            print(f"       - Amount: ${float(amount):.2f} {currency}")
                            total_amount += float(amount)
                        
                        if expense.get('transaction_date'):
                            print(f"       - Date: {expense.get('transaction_date')}")
                        
                        if expense.get('vendor_description'):
                            print(f"       - Vendor: {expense.get('vendor_description')}")
                        
                        if expense.get('business_purpose'):
                            print(f"       - Purpose: {expense.get('business_purpose')}")
                        
                        if expense.get('city_name') or expense.get('country_code'):
                            location = f"{expense.get('city_name', '')} {expense.get('country_code', '')}".strip()
                            if location:
                                print(f"       - Location: {location}")
                        
                        if expense.get('payment_type'):
                            print(f"       - Payment Type: {expense.get('payment_type')}")
                        
                        has_receipt = expense.get('has_receipt')
                        if has_receipt is not None:
                            receipt_status = "Yes" if has_receipt else "No"
                            print(f"       - Has Receipt: {receipt_status}")
                    
                    if total_amount > 0:
                        print(f"\n  Total expense amount: ${total_amount:.2f}")
                else:
                    print(f"  ℹ No line items found in this report")
                    print(f"  Note: This may be a draft report with no expenses yet")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_042_expense_details_validation(self):
        """Test 2: Validate expense entry structure and data"""
        test_name = "Expense entry data validation"
        print(f"Test 2: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'validations': [],
            'error': None
        }
        
        try:
            result = self.sdk.list_expenses(self.test_report_id)
            
            if result['success']:
                validations = []
                
                # Check response structure
                required_response_fields = ['success', 'expenses', 'count', 'api_version', 'report_id']
                for field in required_response_fields:
                    if field in result:
                        validations.append({'field': f'response.{field}', 'present': True})
                    else:
                        validations.append({'field': f'response.{field}', 'present': False})
                
                # Validate data types
                if 'expenses' in result and isinstance(result['expenses'], list):
                    validations.append({'field': 'expenses (array)', 'present': True})
                else:
                    validations.append({'field': 'expenses (array)', 'present': False})
                
                if 'count' in result and isinstance(result['count'], int):
                    validations.append({'field': 'count (integer)', 'present': True})
                else:
                    validations.append({'field': 'count (integer)', 'present': False})
                
                # If we have expenses, validate expense structure
                if result.get('count', 0) > 0:
                    expense = result['expenses'][0]
                    
                    # Key expense fields
                    expense_fields = [
                        'id', 'report_id', 'expense_type', 'transaction_amount',
                        'transaction_currency_code', 'transaction_date'
                    ]
                    
                    for field in expense_fields:
                        if field in expense and expense[field] is not None:
                            validations.append({'field': f'expense.{field}', 'present': True})
                        else:
                            validations.append({'field': f'expense.{field}', 'present': False})
                    
                    # Optional but commonly present fields
                    optional_fields = [
                        'vendor_description', 'business_purpose', 'city_name',
                        'payment_type', 'has_receipt'
                    ]
                    
                    present_optional = [f for f in optional_fields if expense.get(f) is not None]
                    if present_optional:
                        validations.append({
                            'field': f'optional fields present ({len(present_optional)}/{len(optional_fields)})',
                            'present': True
                        })
                
                test_result['validations'] = validations
                test_result['passed'] = all(v['present'] for v in validations if 'optional' not in v['field'])
                
                for v in validations:
                    status = "✓" if v['present'] else "✗"
                    print(f"  {status} {v['field']}")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_042_expense_type_analysis(self):
        """Test 3: Analyze expense types in the report"""
        test_name = "Expense type breakdown"
        print(f"Test 3: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.list_expenses(self.test_report_id)
            
            if result['success']:
                expenses = result['expenses']
                
                # Group by expense type
                type_groups = {}
                total_by_type = {}
                
                for expense in expenses:
                    exp_type = expense.get('expense_type', 'Unknown')
                    amount = float(expense.get('transaction_amount', 0))
                    
                    if exp_type not in type_groups:
                        type_groups[exp_type] = []
                        total_by_type[exp_type] = 0
                    
                    type_groups[exp_type].append(expense)
                    total_by_type[exp_type] += amount
                
                test_result['passed'] = True
                test_result['response'] = {
                    'total_expenses': len(expenses),
                    'unique_expense_types': len(type_groups),
                    'expense_type_distribution': {
                        exp_type: len(exps) for exp_type, exps in type_groups.items()
                    }
                }
                
                print(f"  ✓ Expense type analysis complete")
                print(f"  Total expenses: {len(expenses)}")
                print(f"  Unique expense types: {len(type_groups)}")
                
                if type_groups:
                    print(f"\n  Expense breakdown by type:")
                    for exp_type, exps in sorted(type_groups.items(), key=lambda x: len(x[1]), reverse=True):
                        count = len(exps)
                        total = total_by_type[exp_type]
                        avg = total / count if count > 0 else 0
                        print(f"    - {exp_type}: {count} expense(s)")
                        print(f"      Total: ${total:.2f}, Average: ${avg:.2f}")
                else:
                    print(f"  ℹ No expenses to analyze")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_042_receipt_compliance(self):
        """Test 4: Check receipt compliance for expenses"""
        test_name = "Receipt compliance analysis"
        print(f"Test 4: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.list_expenses(self.test_report_id)
            
            if result['success']:
                expenses = result['expenses']
                
                with_receipt = 0
                without_receipt = 0
                receipt_required = 0
                missing_required_receipt = 0
                
                for expense in expenses:
                    has_receipt = expense.get('has_receipt')
                    required = expense.get('receipt_required')
                    
                    if has_receipt is True:
                        with_receipt += 1
                    elif has_receipt is False:
                        without_receipt += 1
                    
                    if required:
                        receipt_required += 1
                        if not has_receipt:
                            missing_required_receipt += 1
                
                test_result['passed'] = True
                test_result['response'] = {
                    'total_expenses': len(expenses),
                    'with_receipt': with_receipt,
                    'without_receipt': without_receipt,
                    'receipt_required': receipt_required,
                    'missing_required_receipt': missing_required_receipt
                }
                
                print(f"  ✓ Receipt compliance analysis complete")
                print(f"  Total expenses: {len(expenses)}")
                
                if len(expenses) > 0:
                    print(f"\n  Receipt status:")
                    print(f"    - With receipt: {with_receipt}")
                    print(f"    - Without receipt: {without_receipt}")
                    print(f"    - Receipt required: {receipt_required}")
                    
                    if missing_required_receipt > 0:
                        print(f"    ⚠ Missing required receipts: {missing_required_receipt}")
                    else:
                        print(f"    ✓ All required receipts present")
                    
                    # Calculate compliance rate
                    if receipt_required > 0:
                        compliance_rate = ((receipt_required - missing_required_receipt) / receipt_required) * 100
                        print(f"\n  Receipt compliance rate: {compliance_rate:.1f}%")
                else:
                    print(f"  ℹ No expenses to analyze")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_042_multiple_reports_comparison(self):
        """Test 5: Compare line items across multiple reports"""
        test_name = "Multi-report line item comparison"
        print(f"Test 5: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            # Get a few of user's own reports to compare (avoid permission issues)
            reports_result = self.sdk.get_expense_reports(params={'user': 'me', 'limit': 5})
            
            if not reports_result['success'] or reports_result['count'] == 0:
                test_result['error'] = "No reports found"
                print(f"  ✗ No reports available to compare")
                self.results['tests'].append(test_result)
                print()
                return False
            
            report_summaries = []
            total_expenses_all = 0
            
            for report in reports_result['reports'][:3]:  # Test up to 3 reports
                report_id = report['ID']
                report_name = report['ReportName']
                
                try:
                    expenses_result = self.sdk.list_expenses(report_id)
                    
                    if expenses_result['success']:
                        expense_count = expenses_result['count']
                        total_expenses_all += expense_count
                        
                        # Calculate total for this report
                        total_amount = sum(
                            float(exp.get('transaction_amount', 0)) 
                            for exp in expenses_result['expenses']
                        )
                        
                        report_summaries.append({
                            'report_id': report_id,
                            'report_name': report_name,
                            'expense_count': expense_count,
                            'total_amount': total_amount
                        })
                except Exception as e:
                    # Skip reports that can't be accessed
                    continue
            
            test_result['passed'] = len(report_summaries) > 0
            test_result['response'] = {
                'reports_analyzed': len(report_summaries),
                'total_expenses_across_reports': total_expenses_all,
                'report_summaries': report_summaries
            }
            
            print(f"  ✓ Analyzed {len(report_summaries)} report(s)")
            print(f"  Total expenses across all reports: {total_expenses_all}")
            
            if report_summaries:
                print(f"\n  Report comparison:")
                for summary in report_summaries:
                    print(f"    - {summary['report_name']}")
                    print(f"      Report ID: {summary['report_id']}")
                    print(f"      Line items: {summary['expense_count']}")
                    print(f"      Total: ${summary['total_amount']:.2f}")
            else:
                print(f"  ℹ No reports with accessible expenses")
                
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
        results_file = Path(__file__).parent / "results" / "test_042_results.json"
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
        self.test_042_basic_retrieval_line_items()
        self.test_042_expense_details_validation()
        self.test_042_expense_type_analysis()
        self.test_042_receipt_compliance()
        self.test_042_multiple_reports_comparison()
        
        # Generate report
        return self.generate_report()


def main():
    """Main test execution"""
    test_suite = TestReportLineItems()
    success = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

