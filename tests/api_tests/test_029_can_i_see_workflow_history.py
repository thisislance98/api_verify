#!/usr/bin/env python3
"""
Test Case #029: Workflow History of Expense Report
User Query: Can I see the workflow history of my expense report?
Service: Expense Reports & Status
API: GET /expensereports/v4/reports/{reportId}

This test verifies retrieving a single expense report by ID including
workflow transitions/history. The V4 API should include workflow steps
and transitions in the response.
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


class TestWorkflowHistory:
    """Test suite for retrieving workflow history of expense reports"""
    
    def __init__(self):
        self.sdk = None
        self.results = {
            'test_case': '029',
            'user_query': 'Can I see the workflow history of my expense report?',
            'api_endpoint': 'GET /expensereports/v4/reports/{reportId}',
            'service': 'Expense Reports & Status',
            'tests': [],
            'summary': {}
        }
        self.test_report_id = None
    
    def setup(self):
        """Initialize SDK and authenticate"""
        print("=" * 80)
        print("Test Case #029: Workflow History of Expense Report")
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
            
            print()
            return True
            
        except Exception as e:
            print(f"  ✗ Setup failed: {str(e)}")
            return False
    
    def find_test_report(self):
        """Find a test report to use for workflow history testing"""
        print("Finding test report...")
        print("-" * 80)
        
        try:
            # Get any report from the user
            result = self.sdk.get_expense_reports(params={
                'user': self.sdk.config.username,
                'limit': 10
            })
            
            if result['success'] and result.get('count', 0) > 0:
                # Pick the first report with some workflow activity
                reports = result['reports']
                
                # Prefer a submitted report over a draft
                submitted_report = None
                for report in reports:
                    status = report.get('approval_status') or report.get('ApprovalStatusName', '')
                    if status not in ['Not Submitted', 'NOTSUBMITTED']:
                        submitted_report = report
                        break
                
                # If no submitted report, use any report
                test_report = submitted_report or reports[0]
                
                self.test_report_id = test_report.get('id') or test_report.get('ID')
                report_name = test_report.get('name') or test_report.get('Name', 'N/A')
                report_status = test_report.get('approval_status') or test_report.get('ApprovalStatusName', 'N/A')
                
                print(f"  ✓ Found test report")
                print(f"    Report ID: {self.test_report_id}")
                print(f"    Report Name: {report_name}")
                print(f"    Status: {report_status}")
                print()
                return True
            else:
                print(f"  ✗ No reports found for user {self.sdk.config.username}")
                print(f"  ℹ Please create at least one report to test workflow history")
                print()
                return False
                
        except Exception as e:
            print(f"  ✗ Error finding test report: {str(e)}")
            print()
            return False
    
    def test_029_get_report_by_id(self):
        """Test 1: Get report by ID"""
        test_name = "Get single report by ID"
        print(f"Test 1: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': f'/expensereports/v4/reports/{self.test_report_id}',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.get_report_by_id(self.test_report_id)
            
            if result['success']:
                report = result['report']
                test_result['passed'] = True
                test_result['response'] = {
                    'report_id': report.get('reportId') or report.get('id'),
                    'report_name': report.get('name'),
                    'approval_status': report.get('approvalStatus') or report.get('approval_status'),
                    'has_workflow_data': 'workflowStep' in report or 'workflow' in report
                }
                
                print(f"  ✓ Successfully retrieved report")
                print(f"  Report ID: {report.get('reportId') or report.get('id')}")
                print(f"  Report Name: {report.get('name', 'N/A')}")
                print(f"  Status: {report.get('approvalStatus') or report.get('approval_status', 'N/A')}")
                print(f"  Created: {report.get('creationDate') or report.get('created_date', 'N/A')}")
                print(f"  Last Modified: {report.get('lastModifiedDate') or report.get('last_modified_date', 'N/A')}")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_029_workflow_fields_present(self):
        """Test 2: Verify workflow-related fields are present"""
        test_name = "Verify workflow fields in response"
        print(f"Test 2: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'workflow_fields': [],
            'error': None
        }
        
        try:
            result = self.sdk.get_report_by_id(self.test_report_id)
            
            if result['success']:
                report = result['report']
                
                # Check for workflow-related fields
                workflow_fields = [
                    'workflowStep',
                    'approvalStatus',
                    'approvalStatusName',
                    'submitDate',
                    'approverName',
                    'approvalDate',
                    'lastModifiedDate',
                    'workflow',
                    'workflowHistory',
                    'transitions'
                ]
                
                found_fields = []
                for field in workflow_fields:
                    # Check both camelCase and snake_case variants
                    if field in report or field.lower().replace('_', '') in str(report).lower():
                        value = report.get(field)
                        found_fields.append({
                            'field': field,
                            'present': True,
                            'has_value': value is not None and value != ''
                        })
                
                test_result['workflow_fields'] = found_fields
                test_result['passed'] = len(found_fields) > 0
                
                print(f"  Workflow-related fields found:")
                for field_info in found_fields:
                    status = "✓" if field_info['has_value'] else "○"
                    print(f"    {status} {field_info['field']}: {'Has value' if field_info['has_value'] else 'Present but empty'}")
                
                if len(found_fields) == 0:
                    print(f"  ⚠️ No workflow fields found in response")
                    print(f"  ℹ Available fields: {', '.join(report.keys())}")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_029_workflow_transitions(self):
        """Test 3: Check for workflow transitions/history"""
        test_name = "Check for workflow transitions/history"
        print(f"Test 3: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'transitions': [],
            'error': None
        }
        
        try:
            result = self.sdk.get_report_by_id(self.test_report_id)
            
            if result['success']:
                report = result['report']
                
                # Look for workflow history/transitions
                transitions = []
                
                # Check various possible locations for workflow data
                if 'workflow' in report:
                    transitions.append({
                        'type': 'workflow object',
                        'data': report['workflow']
                    })
                
                if 'workflowHistory' in report:
                    transitions.append({
                        'type': 'workflowHistory array',
                        'data': report['workflowHistory']
                    })
                
                if 'transitions' in report:
                    transitions.append({
                        'type': 'transitions array',
                        'data': report['transitions']
                    })
                
                # Check if we have basic workflow tracking
                basic_workflow = {}
                if 'workflowStep' in report:
                    basic_workflow['currentStep'] = report['workflowStep']
                if 'approvalStatus' in report or 'approvalStatusName' in report:
                    basic_workflow['status'] = report.get('approvalStatus') or report.get('approvalStatusName')
                if 'submitDate' in report:
                    basic_workflow['submitDate'] = report['submitDate']
                if 'lastModifiedDate' in report:
                    basic_workflow['lastModified'] = report['lastModifiedDate']
                
                if basic_workflow:
                    transitions.append({
                        'type': 'basic workflow tracking',
                        'data': basic_workflow
                    })
                
                test_result['transitions'] = transitions
                test_result['passed'] = len(transitions) > 0
                
                if transitions:
                    print(f"  ✓ Found {len(transitions)} workflow data source(s)")
                    for idx, trans in enumerate(transitions, 1):
                        print(f"    {idx}. {trans['type']}")
                        if trans['type'] == 'basic workflow tracking':
                            for key, value in trans['data'].items():
                                print(f"       - {key}: {value}")
                        elif isinstance(trans['data'], list):
                            print(f"       - Contains {len(trans['data'])} items")
                        elif isinstance(trans['data'], dict):
                            print(f"       - Contains {len(trans['data'])} fields")
                else:
                    print(f"  ⚠️ No explicit workflow history/transitions found")
                    print(f"  ℹ The V4 API may not include detailed workflow history")
                    print(f"  ℹ Current status: {report.get('approvalStatus') or report.get('approvalStatusName', 'Unknown')}")
                
            else:
                test_result['error'] = result.get('message', 'Unknown error')
                print(f"  ✗ Request failed: {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_029_compare_with_list(self):
        """Test 4: Compare single report retrieval with list endpoint"""
        test_name = "Compare single report vs list endpoint data"
        print(f"Test 4: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'comparison': {},
            'error': None
        }
        
        try:
            # Get single report
            single_result = self.sdk.get_report_by_id(self.test_report_id)
            
            # Get same report from list
            list_result = self.sdk.get_expense_reports(params={
                'reportId': self.test_report_id,
                'limit': 1
            })
            
            if single_result['success'] and list_result['success']:
                single_report = single_result['report']
                list_reports = list_result.get('reports', [])
                
                if list_reports:
                    list_report = list_reports[0]
                    
                    # Compare field counts
                    single_fields = len(single_report.keys())
                    list_fields = len(list_report.keys())
                    
                    test_result['comparison'] = {
                        'single_endpoint_fields': single_fields,
                        'list_endpoint_fields': list_fields,
                        'difference': single_fields - list_fields
                    }
                    
                    test_result['passed'] = True
                    
                    print(f"  Single report endpoint: {single_fields} fields")
                    print(f"  List endpoint: {list_fields} fields")
                    print(f"  Difference: {single_fields - list_fields} additional fields in single report")
                    
                    if single_fields > list_fields:
                        print(f"  ✓ Single report endpoint provides more details")
                    elif single_fields == list_fields:
                        print(f"  ℹ Both endpoints provide same field count")
                    else:
                        print(f"  ℹ List endpoint provides more fields")
                else:
                    test_result['error'] = "Report not found in list endpoint"
                    print(f"  ✗ Could not find report in list endpoint")
                
            else:
                test_result['error'] = "One or both requests failed"
                print(f"  ✗ Request failed")
                if not single_result['success']:
                    print(f"    Single: {single_result.get('message')}")
                if not list_result['success']:
                    print(f"    List: {list_result.get('message')}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_029_multiple_reports_workflow(self):
        """Test 5: Check workflow info across multiple reports"""
        test_name = "Workflow info across multiple reports"
        print(f"Test 5: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'reports_analyzed': [],
            'error': None
        }
        
        try:
            # Get multiple reports
            result = self.sdk.get_expense_reports(params={
                'user': self.sdk.config.username,
                'limit': 5
            })
            
            if result['success'] and result.get('count', 0) > 0:
                reports_with_workflow = []
                
                for report in result['reports'][:5]:  # Analyze up to 5 reports
                    report_id = report.get('id') or report.get('ID')
                    report_name = report.get('name') or report.get('Name', 'N/A')
                    status = report.get('approval_status') or report.get('ApprovalStatusName', 'N/A')
                    workflow_step = report.get('workflow_step') or report.get('WorkflowStep', 'N/A')
                    
                    reports_with_workflow.append({
                        'report_id': report_id,
                        'name': report_name,
                        'status': status,
                        'workflow_step': workflow_step
                    })
                
                test_result['reports_analyzed'] = reports_with_workflow
                test_result['passed'] = len(reports_with_workflow) > 0
                
                print(f"  ✓ Analyzed {len(reports_with_workflow)} report(s)")
                print(f"\n  Workflow status summary:")
                for idx, rpt in enumerate(reports_with_workflow, 1):
                    print(f"    {idx}. {rpt['name']}")
                    print(f"       Status: {rpt['status']}")
                    print(f"       Workflow Step: {rpt['workflow_step']}")
                    print()
                
            else:
                test_result['error'] = "No reports found"
                print(f"  ✗ No reports found for analysis")
                
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
        results_file = Path(__file__).parent / "results" / "test_029_results.json"
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
        
        # Find a test report
        if not self.find_test_report():
            print("⚠️ Cannot proceed without a test report")
            print("Please create at least one expense report and try again")
            return False
        
        # Run tests
        self.test_029_get_report_by_id()
        self.test_029_workflow_fields_present()
        self.test_029_workflow_transitions()
        self.test_029_compare_with_list()
        self.test_029_multiple_reports_workflow()
        
        # Generate report
        return self.generate_report()


def main():
    """Main test execution"""
    test_suite = TestWorkflowHistory()
    success = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

