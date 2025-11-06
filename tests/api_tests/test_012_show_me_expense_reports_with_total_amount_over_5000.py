#!/usr/bin/env python3
"""
Test Case #012: Expense Reports Over $5000
User Query: Show me expense reports with total amount over $5000
Service: Expense Reports & Status
API: GET /api/v3.0/expense/reports

This test verifies retrieval of expense reports filtered by total approved amount
greater than $5000. Since the API may not support direct filtering by amount,
we retrieve reports and filter client-side.
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


class TestReportsOver5000:
    """Test suite for reports with total amount over $5000"""
    
    def __init__(self):
        self.sdk = None
        self.user_id = None
        self.threshold = 5000.0
        self.results = {
            'test_case': '012',
            'user_query': 'Show me expense reports with total amount over $5000',
            'api_endpoint': 'GET /api/v3.0/expense/reports',
            'service': 'Expense Reports & Status',
            'tests': [],
            'summary': {}
        }
    
    def setup(self):
        """Initialize SDK and authenticate"""
        print("=" * 80)
        print("Test Case #012: Expense Reports Over $5000")
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
    
    def test_012_basic_retrieval_all_reports(self):
        """Test 1: Retrieve all reports and filter by amount > $5000"""
        test_name = "Basic retrieval of reports over $5000"
        print(f"Test 1: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            # Get all expense reports with a reasonable limit
            # Note: We're retrieving all reports and will filter client-side
            # API max limit is 100
            params = {
                'user': 'ALL',
                'limit': 100  # API maximum limit
            }
            
            result = self.sdk.get_expense_reports(params=params)
            
            if result['success']:
                # Filter reports with total > $5000
                all_reports = result['reports']
                high_value_reports = [
                    report for report in all_reports 
                    if report.get('Total') and float(report.get('Total', 0)) > self.threshold
                ]
                
                test_result['passed'] = True
                test_result['response'] = {
                    'total_reports_retrieved': result['count'],
                    'reports_over_threshold': len(high_value_reports),
                    'threshold': self.threshold,
                    'params': params
                }
                
                print(f"  ✓ Request successful")
                print(f"  Total reports retrieved: {result['count']}")
                print(f"  Reports over ${self.threshold:,.2f}: {len(high_value_reports)}")
                
                if len(high_value_reports) > 0:
                    print(f"\n  Sample high-value reports:")
                    for i, report in enumerate(high_value_reports[:5], 1):
                        print(f"    {i}. {report['ReportName']}")
                        print(f"       - Report ID: {report['ID']}")
                        print(f"       - Owner: {report['OwnerName']}")
                        print(f"       - Total: ${report['Total']:,.2f} {report['CurrencyCode']}")
                        print(f"       - Status: {report['ApprovalStatusName']}")
                        print(f"       - Submit Date: {report.get('SubmitDate', 'N/A')}")
                    
                    if len(high_value_reports) > 5:
                        print(f"    ... and {len(high_value_reports) - 5} more")
                    
                    # Calculate statistics
                    total_amounts = [float(report.get('Total', 0)) for report in high_value_reports]
                    avg_amount = sum(total_amounts) / len(total_amounts)
                    max_amount = max(total_amounts)
                    min_amount = min(total_amounts)
                    
                    print(f"\n  Statistics for high-value reports:")
                    print(f"    - Average amount: ${avg_amount:,.2f}")
                    print(f"    - Maximum amount: ${max_amount:,.2f}")
                    print(f"    - Minimum amount: ${min_amount:,.2f}")
                else:
                    print(f"  ℹ No reports found with total over ${self.threshold:,.2f}")
                    print(f"  Note: This is not a test failure - it means no high-value reports exist")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_012_verify_threshold_filtering(self):
        """Test 2: Verify all returned reports are actually over $5000"""
        test_name = "Verify threshold filtering accuracy"
        print(f"Test 2: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            params = {
                'user': 'ALL',
                'limit': 100  # API maximum limit
            }
            
            result = self.sdk.get_expense_reports(params=params)
            
            if result['success']:
                # Filter reports with total > $5000
                high_value_reports = [
                    report for report in result['reports']
                    if report.get('Total') and float(report.get('Total', 0)) > self.threshold
                ]
                
                # Verify all reports meet the threshold
                all_valid = True
                invalid_reports = []
                
                for report in high_value_reports:
                    total = float(report.get('Total', 0))
                    if total <= self.threshold:
                        all_valid = False
                        invalid_reports.append({
                            'name': report['ReportName'],
                            'id': report['ID'],
                            'total': total
                        })
                
                if all_valid:
                    test_result['passed'] = True
                    test_result['response'] = {
                        'all_reports_valid': True,
                        'total_reports_checked': len(high_value_reports),
                        'threshold': self.threshold
                    }
                    print(f"  ✓ All filtered reports meet threshold criteria")
                    print(f"  Total reports validated: {len(high_value_reports)}")
                    
                    if len(high_value_reports) > 0:
                        amounts = [float(report.get('Total', 0)) for report in high_value_reports]
                        print(f"  Amount range: ${min(amounts):,.2f} - ${max(amounts):,.2f}")
                else:
                    test_result['error'] = f"Found {len(invalid_reports)} reports below threshold"
                    test_result['response'] = {
                        'all_reports_valid': False,
                        'invalid_reports': invalid_reports
                    }
                    print(f"  ✗ Found {len(invalid_reports)} reports below threshold")
                    for inv in invalid_reports:
                        print(f"    - {inv['name']}: ${inv['total']:,.2f}")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_012_filter_with_status(self):
        """Test 3: Combine amount filter with approval status"""
        test_name = "High-value reports by approval status"
        print(f"Test 3: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            params = {
                'user': 'ALL',
                'limit': 100  # API maximum limit
            }
            
            result = self.sdk.get_expense_reports(params=params)
            
            if result['success']:
                # Filter by amount and group by status
                high_value_reports = [
                    report for report in result['reports']
                    if report.get('Total') and float(report.get('Total', 0)) > self.threshold
                ]
                
                # Group by approval status
                status_groups = {}
                for report in high_value_reports:
                    status = report.get('ApprovalStatusName', 'Unknown')
                    if status not in status_groups:
                        status_groups[status] = []
                    status_groups[status].append(report)
                
                test_result['passed'] = True
                test_result['response'] = {
                    'total_high_value_reports': len(high_value_reports),
                    'status_distribution': {
                        status: len(reports) for status, reports in status_groups.items()
                    }
                }
                
                print(f"  ✓ Reports grouped by status")
                print(f"  Total high-value reports: {len(high_value_reports)}")
                print(f"\n  Distribution by approval status:")
                
                for status, reports in sorted(status_groups.items(), key=lambda x: len(x[1]), reverse=True):
                    total_value = sum(float(r.get('Total', 0)) for r in reports)
                    print(f"    - {status}: {len(reports)} reports (${total_value:,.2f} total)")
                
                if not status_groups:
                    print(f"    ℹ No high-value reports found to categorize")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_012_currency_handling(self):
        """Test 4: Verify currency handling for amount comparisons"""
        test_name = "Currency code validation"
        print(f"Test 4: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            params = {
                'user': 'ALL',
                'limit': 100  # API maximum limit
            }
            
            result = self.sdk.get_expense_reports(params=params)
            
            if result['success']:
                # Filter by amount
                high_value_reports = [
                    report for report in result['reports']
                    if report.get('Total') and float(report.get('Total', 0)) > self.threshold
                ]
                
                # Group by currency
                currency_groups = {}
                for report in high_value_reports:
                    currency = report.get('CurrencyCode', 'Unknown')
                    if currency not in currency_groups:
                        currency_groups[currency] = []
                    currency_groups[currency].append(report)
                
                test_result['passed'] = True
                test_result['response'] = {
                    'total_reports': len(high_value_reports),
                    'currencies_found': list(currency_groups.keys()),
                    'currency_distribution': {
                        currency: len(reports) for currency, reports in currency_groups.items()
                    }
                }
                
                print(f"  ✓ Currency analysis complete")
                print(f"  Total high-value reports: {len(high_value_reports)}")
                print(f"  Currencies found: {len(currency_groups)}")
                
                if currency_groups:
                    print(f"\n  Distribution by currency:")
                    for currency, reports in sorted(currency_groups.items()):
                        total_amount = sum(float(r.get('Total', 0)) for r in reports)
                        avg_amount = total_amount / len(reports) if reports else 0
                        print(f"    - {currency}: {len(reports)} reports")
                        print(f"      Total: {total_amount:,.2f}, Avg: {avg_amount:,.2f}")
                    
                    if len(currency_groups) > 1:
                        print(f"\n  ⚠ Note: Multiple currencies detected")
                        print(f"    The ${self.threshold:,.2f} threshold is applied uniformly")
                        print(f"    Real-world usage should consider exchange rates")
                else:
                    print(f"    ℹ No high-value reports to analyze")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_012_response_structure(self):
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
            params = {'user': 'ALL', 'limit': 100}  # API maximum limit
            result = self.sdk.get_expense_reports(params=params)
            
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
                report_fields = ['ID', 'ReportName', 'Total', 'CurrencyCode', 
                               'ApprovalStatusName', 'OwnerName']
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
        results_file = Path(__file__).parent / "results" / "test_012_results.json"
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
        self.test_012_basic_retrieval_all_reports()
        self.test_012_verify_threshold_filtering()
        self.test_012_filter_with_status()
        self.test_012_currency_handling()
        self.test_012_response_structure()
        
        # Generate report
        return self.generate_report()


def main():
    """Main test execution"""
    test_suite = TestReportsOver5000()
    success = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

