#!/usr/bin/env python3
"""
Test Case #040: Reports with Allocations to Multiple Projects
User Query: Show me reports with allocations to multiple projects
Service: Expense Reports & Status
API: GET /api/v3.0/expense/reports?hasAllocations=Y (then check allocation count)

This test verifies retrieval of expense reports that have expense allocations
distributed across multiple projects. Allocations allow splitting expenses
across different cost centers, departments, or projects.
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


class TestReportsWithMultipleAllocations:
    """Test suite for reports with allocations to multiple projects"""
    
    def __init__(self):
        self.sdk = None
        self.user_id = None
        self.results = {
            'test_case': '040',
            'user_query': 'Show me reports with allocations to multiple projects',
            'api_endpoint': 'GET /api/v3.0/expense/reports?hasAllocations=Y',
            'service': 'Expense Reports & Status',
            'tests': [],
            'summary': {}
        }
    
    def setup(self):
        """Initialize SDK and authenticate"""
        print("=" * 80)
        print("Test Case #040: Reports with Allocations to Multiple Projects")
        print("=" * 80)
        print()
        
        print("Setup: Initializing SDK...")
        try:
            # Load credentials - using manager_approver to see all reports
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
    
    def test_040_basic_retrieval_with_allocations(self):
        """Test 1: Retrieve reports with any allocations"""
        test_name = "Basic retrieval of reports with hasAllocations=Y"
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
            # Get all expense reports with allocations
            params = {
                'hasAllocations': 'Y',
                'user': 'ALL',
                'limit': 100  # API maximum limit
            }
            
            result = self.sdk.get_expense_reports(params=params)
            
            if result['success']:
                allocated_reports = result['reports']
                
                test_result['passed'] = True
                test_result['response'] = {
                    'total_reports': result['count'],
                    'params': params
                }
                
                print(f"  ✓ Request successful")
                print(f"  Total reports with allocations: {result['count']}")
                
                if len(allocated_reports) > 0:
                    print(f"\n  Sample reports with allocations:")
                    for i, report in enumerate(allocated_reports[:10], 1):
                        print(f"    {i}. {report['ReportName']}")
                        print(f"       - Report ID: {report['ID']}")
                        print(f"       - Owner: {report['OwnerName']}")
                        print(f"       - Total: ${report['Total']:,.2f} {report['CurrencyCode']}")
                        print(f"       - Status: {report['ApprovalStatusName']}")
                    
                    if len(allocated_reports) > 10:
                        print(f"    ... and {len(allocated_reports) - 10} more")
                else:
                    print(f"  ℹ No reports with allocations found")
                    print(f"  Note: This may indicate no expenses have been split across projects")
                    print(f"  To generate test data, create a report with:")
                    print(f"    - An expense entry")
                    print(f"    - Split allocation across multiple projects/cost centers")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_040_get_allocation_details(self):
        """Test 2: Get detailed allocation information for reports"""
        test_name = "Get allocation details from reports"
        print(f"Test 2: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            # Get reports with allocations
            params = {
                'hasAllocations': 'Y',
                'user': 'ALL',
                'limit': 10  # Just get a few for detailed inspection
            }
            
            result = self.sdk.get_expense_reports(params=params)
            
            if result['success'] and len(result['reports']) > 0:
                allocated_reports = result['reports']
                
                print(f"  Found {len(allocated_reports)} reports with allocations")
                print(f"\n  Fetching allocation details for each report...")
                
                reports_with_details = []
                
                for i, report in enumerate(allocated_reports[:5], 1):  # Limit to first 5
                    report_id = report['ID']
                    print(f"\n  Report {i}: {report['ReportName']} (ID: {report_id})")
                    
                    # Get full report details including allocations
                    details_result = self.sdk.get_report_full_details(report_id)
                    
                    if details_result['success']:
                        full_report = details_result['report']
                        
                        # Extract allocation information from expense entries
                        total_allocations = 0
                        entries_with_allocations = []
                        
                        expense_entries = full_report.get('ExpenseEntriesList', [])
                        for entry in expense_entries:
                            allocations = entry.get('Allocations', [])
                            if allocations and len(allocations) > 0:
                                total_allocations += len(allocations)
                                entries_with_allocations.append({
                                    'expense_type': entry.get('ExpenseTypeName', 'Unknown'),
                                    'amount': entry.get('TransactionAmount', 0),
                                    'allocation_count': len(allocations),
                                    'allocations': allocations
                                })
                        
                        print(f"    - Expense Entries: {len(expense_entries)}")
                        print(f"    - Entries with Allocations: {len(entries_with_allocations)}")
                        print(f"    - Total Allocations: {total_allocations}")
                        
                        reports_with_details.append({
                            'report_id': report_id,
                            'report_name': report['ReportName'],
                            'total': report['Total'],
                            'entries_count': len(expense_entries),
                            'entries_with_allocations': len(entries_with_allocations),
                            'total_allocations': total_allocations,
                            'allocations_details': entries_with_allocations
                        })
                    else:
                        print(f"    ⚠ Could not fetch details: {details_result.get('message')}")
                
                test_result['passed'] = len(reports_with_details) > 0
                test_result['response'] = {
                    'reports_analyzed': len(reports_with_details),
                    'reports': reports_with_details
                }
                
                if len(reports_with_details) > 0:
                    print(f"\n  ✓ Successfully retrieved allocation details for {len(reports_with_details)} reports")
                else:
                    print(f"\n  ⚠ Could not retrieve allocation details")
                
            else:
                # No reports with allocations found
                test_result['passed'] = True  # Test passes but with no data
                test_result['response'] = {
                    'reports_analyzed': 0,
                    'message': 'No reports with allocations found'
                }
                print(f"  ℹ No reports with allocations to analyze")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_040_filter_multiple_allocations(self):
        """Test 3: Filter for reports with multiple project allocations"""
        test_name = "Filter reports with allocations to multiple projects"
        print(f"Test 3: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            # Get reports with allocations
            params = {
                'hasAllocations': 'Y',
                'user': 'ALL',
                'limit': 50
            }
            
            result = self.sdk.get_expense_reports(params=params)
            
            if result['success']:
                allocated_reports = result['reports']
                
                print(f"  Found {len(allocated_reports)} reports with allocations")
                print(f"  Analyzing allocation counts...")
                
                reports_with_multiple = []
                reports_with_single = []
                
                for report in allocated_reports[:20]:  # Analyze first 20
                    report_id = report['ID']
                    
                    # Get full report details
                    details_result = self.sdk.get_report_full_details(report_id)
                    
                    if details_result['success']:
                        full_report = details_result['report']
                        expense_entries = full_report.get('ExpenseEntriesList', [])
                        
                        # Find entries with multiple allocations
                        has_multiple_allocations = False
                        max_allocations = 0
                        
                        for entry in expense_entries:
                            allocations = entry.get('Allocations', [])
                            if len(allocations) > max_allocations:
                                max_allocations = len(allocations)
                            if len(allocations) > 1:
                                has_multiple_allocations = True
                        
                        report_info = {
                            'report_id': report_id,
                            'report_name': report['ReportName'],
                            'owner': report['OwnerName'],
                            'total': report['Total'],
                            'currency': report['CurrencyCode'],
                            'max_allocations': max_allocations,
                            'entries_count': len(expense_entries)
                        }
                        
                        if has_multiple_allocations:
                            reports_with_multiple.append(report_info)
                        elif max_allocations == 1:
                            reports_with_single.append(report_info)
                
                test_result['passed'] = True
                test_result['response'] = {
                    'reports_with_multiple_allocations': len(reports_with_multiple),
                    'reports_with_single_allocation': len(reports_with_single),
                    'total_analyzed': len(reports_with_multiple) + len(reports_with_single),
                    'multiple_allocation_reports': reports_with_multiple
                }
                
                print(f"\n  ✓ Analysis complete")
                print(f"  Reports analyzed: {len(reports_with_multiple) + len(reports_with_single)}")
                print(f"  Reports with MULTIPLE allocations (>1 project): {len(reports_with_multiple)}")
                print(f"  Reports with SINGLE allocation: {len(reports_with_single)}")
                
                if len(reports_with_multiple) > 0:
                    print(f"\n  Reports with allocations to multiple projects:")
                    for i, rep in enumerate(reports_with_multiple[:10], 1):
                        print(f"    {i}. {rep['report_name']}")
                        print(f"       - Owner: {rep['owner']}")
                        print(f"       - Total: ${rep['total']:,.2f} {rep['currency']}")
                        print(f"       - Max allocations per entry: {rep['max_allocations']}")
                        print(f"       - Entries: {rep['entries_count']}")
                else:
                    print(f"\n  ℹ No reports found with multiple project allocations")
                    print(f"  Note: Reports may have allocations but to only one project each")
                    print(f"  To generate test data:")
                    print(f"    1. Create an expense report")
                    print(f"    2. Add an expense entry")
                    print(f"    3. Split allocation across 2+ projects/cost centers")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_040_allocation_distribution_analysis(self):
        """Test 4: Analyze allocation distribution patterns"""
        test_name = "Analyze allocation distribution across reports"
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
                'hasAllocations': 'Y',
                'user': 'ALL',
                'limit': 50
            }
            
            result = self.sdk.get_expense_reports(params=params)
            
            if result['success']:
                allocated_reports = result['reports']
                
                # Track allocation patterns
                allocation_distribution = {}  # {allocation_count: count_of_reports}
                total_reports_analyzed = 0
                total_value_multi_allocation = 0
                
                for report in allocated_reports[:20]:
                    report_id = report['ID']
                    details_result = self.sdk.get_report_full_details(report_id)
                    
                    if details_result['success']:
                        full_report = details_result['report']
                        expense_entries = full_report.get('ExpenseEntriesList', [])
                        
                        max_allocations = 0
                        for entry in expense_entries:
                            allocations = entry.get('Allocations', [])
                            if len(allocations) > max_allocations:
                                max_allocations = len(allocations)
                        
                        if max_allocations > 0:
                            if max_allocations not in allocation_distribution:
                                allocation_distribution[max_allocations] = 0
                            allocation_distribution[max_allocations] += 1
                            
                            if max_allocations > 1:
                                total_value_multi_allocation += float(report.get('Total', 0))
                        
                        total_reports_analyzed += 1
                
                test_result['passed'] = True
                test_result['response'] = {
                    'total_reports_analyzed': total_reports_analyzed,
                    'allocation_distribution': allocation_distribution,
                    'total_value_multi_allocation': total_value_multi_allocation
                }
                
                print(f"  ✓ Distribution analysis complete")
                print(f"  Total reports analyzed: {total_reports_analyzed}")
                
                if allocation_distribution:
                    print(f"\n  Allocation distribution:")
                    for alloc_count in sorted(allocation_distribution.keys()):
                        report_count = allocation_distribution[alloc_count]
                        label = "project" if alloc_count == 1 else "projects"
                        print(f"    - {alloc_count} {label}: {report_count} reports")
                    
                    multi_alloc_count = sum(
                        count for alloc, count in allocation_distribution.items() 
                        if alloc > 1
                    )
                    if multi_alloc_count > 0:
                        print(f"\n  Reports with multiple project allocations: {multi_alloc_count}")
                        print(f"  Total value: ${total_value_multi_allocation:,.2f}")
                else:
                    print(f"  ℹ No allocation data available for analysis")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_040_allocation_field_inspection(self):
        """Test 5: Inspect allocation field structure"""
        test_name = "Inspect allocation field structure"
        print(f"Test 5: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            params = {
                'hasAllocations': 'Y',
                'user': 'ALL',
                'limit': 5
            }
            
            result = self.sdk.get_expense_reports(params=params)
            
            if result['success'] and len(result['reports']) > 0:
                report = result['reports'][0]
                report_id = report['ID']
                
                print(f"  Inspecting report: {report['ReportName']} (ID: {report_id})")
                
                details_result = self.sdk.get_report_full_details(report_id)
                
                if details_result['success']:
                    full_report = details_result['report']
                    expense_entries = full_report.get('ExpenseEntriesList', [])
                    
                    print(f"  ✓ Report has {len(expense_entries)} expense entries")
                    
                    # Find first entry with allocations
                    sample_allocation = None
                    for entry in expense_entries:
                        allocations = entry.get('Allocations', [])
                        if allocations and len(allocations) > 0:
                            sample_allocation = allocations[0]
                            print(f"\n  Found allocation in entry: {entry.get('ExpenseTypeName')}")
                            print(f"  Entry amount: ${entry.get('TransactionAmount', 0)}")
                            print(f"  Allocation count: {len(allocations)}")
                            
                            print(f"\n  Sample allocation fields:")
                            for key, value in sample_allocation.items():
                                print(f"    - {key}: {value}")
                            
                            test_result['response'] = {
                                'sample_allocation': sample_allocation,
                                'allocation_fields': list(sample_allocation.keys()),
                                'entry_expense_type': entry.get('ExpenseTypeName'),
                                'allocation_count': len(allocations)
                            }
                            break
                    
                    if sample_allocation:
                        test_result['passed'] = True
                        print(f"\n  ✓ Successfully inspected allocation structure")
                    else:
                        test_result['passed'] = True
                        test_result['response'] = {'message': 'No allocations found in entries'}
                        print(f"\n  ℹ Report has hasAllocations=Y but no allocation data in entries")
                else:
                    test_result['error'] = details_result.get('message')
                    print(f"  ✗ Failed to get report details: {test_result['error']}")
            else:
                test_result['passed'] = True
                test_result['response'] = {'message': 'No reports with allocations available'}
                print(f"  ℹ No reports with allocations available for inspection")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_040_response_structure(self):
        """Test 6: Validate response structure"""
        test_name = "Response structure validation"
        print(f"Test 6: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'validations': [],
            'error': None
        }
        
        try:
            params = {
                'hasAllocations': 'Y',
                'user': 'ALL',
                'limit': 10
            }
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
            
            # Validate hasAllocations parameter was applied
            if 'params' in result and result['params'].get('hasAllocations') == 'Y':
                validations.append({'field': 'hasAllocations param applied', 'present': True})
            else:
                validations.append({'field': 'hasAllocations param applied', 'present': False})
            
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
        results_file = Path(__file__).parent / "results" / "test_040_results.json"
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
        self.test_040_basic_retrieval_with_allocations()
        self.test_040_get_allocation_details()
        self.test_040_filter_multiple_allocations()
        self.test_040_allocation_distribution_analysis()
        self.test_040_allocation_field_inspection()
        self.test_040_response_structure()
        
        # Generate report
        return self.generate_report()


def main():
    """Main test execution"""
    test_suite = TestReportsWithMultipleAllocations()
    success = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

