#!/usr/bin/env python3
"""
Test Case #031: Reports with Comments from Approvers
User Query: Which reports have comments from approvers?
Service: Expense Reports & Status
API: GET /expensereports/v4/reports/{reportId}

This test verifies that we can identify expense reports that have comments from approvers
in their workflow history. This is useful for:
- Finding reports with feedback from approvers
- Identifying reports that may need attention based on comments
- Reviewing approval history and communication

The test:
1. Gets a list of expense reports
2. For each report, retrieves full details including workflow history
3. Checks for approver comments in the workflow steps
4. Returns reports that have approver comments
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


class TestReportsWithApproverComments:
    """Test suite for finding reports with approver comments"""
    
    def __init__(self):
        self.sdk = None
        self.user_id = None
        self.username = None
        self.results = {
            'test_case': '031',
            'user_query': 'Which reports have comments from approvers?',
            'api_endpoint': 'GET /expensereports/v4/reports/{reportId}',
            'service': 'Expense Reports & Status',
            'tests': [],
            'summary': {}
        }
    
    def setup(self):
        """Initialize SDK and authenticate"""
        print("=" * 80)
        print("Test Case #031: Reports with Comments from Approvers")
        print("=" * 80)
        print()
        
        print("Setup: Initializing SDK...")
        try:
            # Load credentials from config
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
            self.username = creds['username']
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
    
    def get_report_with_workflow(self, report_id: str) -> dict:
        """
        Get report details including workflow history from V4 API
        
        Args:
            report_id: The report ID to retrieve
            
        Returns:
            Dictionary with report data including workflow history
        """
        try:
            endpoint = f"expensereports/v4/reports/{report_id}"
            response = self.sdk._make_request("GET", endpoint)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'report': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'message': response.text[:200] if hasattr(response, 'text') else 'Unknown error'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def extract_approver_comments(self, report_data: dict) -> list:
        """
        Extract approver comments from report workflow history
        
        Args:
            report_data: The full report data including workflow
            
        Returns:
            List of comments from approvers with metadata
        """
        comments = []
        
        # Check for workflow steps/history
        workflow_steps = report_data.get('workflowSteps', [])
        
        for step in workflow_steps:
            # Look for comments in workflow step
            comment = step.get('comment', '') or step.get('comments', '')
            actor_name = step.get('actorName', '') or step.get('approverName', '')
            action = step.get('action', '') or step.get('actionType', '')
            action_date = step.get('actionDate', '') or step.get('completedDate', '')
            
            # Only include if there's an actual comment from an approver
            if comment and comment.strip():
                comments.append({
                    'comment': comment,
                    'actor': actor_name,
                    'action': action,
                    'date': action_date,
                    'step_name': step.get('stepName', '') or step.get('name', '')
                })
        
        # Also check top-level comment fields (some APIs put it here)
        if 'approverComments' in report_data and report_data['approverComments']:
            comments.append({
                'comment': report_data['approverComments'],
                'actor': 'Approver',
                'action': 'Comment',
                'date': report_data.get('lastModifiedDate', ''),
                'step_name': 'Top-level comment'
            })
        
        return comments
    
    def test_031_find_reports_with_approver_comments(self):
        """Test 1: Find all reports with approver comments"""
        test_name = "Find reports with approver comments"
        print(f"Test 1: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/expensereports/v4/reports/{reportId}',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            # First, get a list of reports to check
            print(f"  Step 1: Retrieving expense reports...")
            
            # Get all reports (any status) to maximize chances of finding comments
            params = {
                'user': 'ALL',
                'limit': 50
            }
            
            reports_result = self.sdk.get_expense_reports(params)
            
            if not reports_result['success']:
                test_result['error'] = f"Failed to get reports: {reports_result.get('message', 'Unknown error')}"
                print(f"  ✗ {test_result['error']}")
                self.results['tests'].append(test_result)
                return False
            
            all_reports = reports_result['reports']
            print(f"  ✓ Found {len(all_reports)} reports to check")
            print()
            
            # Check each report for approver comments
            print(f"  Step 2: Checking each report for approver comments...")
            reports_with_comments = []
            checked_count = 0
            
            for report in all_reports:
                report_id = report.get('ID') or report.get('id')
                report_name = report.get('ReportName') or report.get('name', 'N/A')
                
                if not report_id:
                    continue
                
                checked_count += 1
                
                # Get full report details with workflow
                details_result = self.get_report_with_workflow(report_id)
                
                if details_result['success']:
                    report_data = details_result['report']
                    comments = self.extract_approver_comments(report_data)
                    
                    if comments:
                        reports_with_comments.append({
                            'report_id': report_id,
                            'report_name': report_name,
                            'owner_name': report.get('OwnerName') or report.get('ownerName', 'N/A'),
                            'total': report.get('Total') or report.get('totalApprovedAmount', 0),
                            'currency': report.get('CurrencyCode') or report.get('currencyCode', ''),
                            'approval_status': report.get('ApprovalStatusName') or report.get('approvalStatus', 'N/A'),
                            'comments': comments,
                            'comment_count': len(comments)
                        })
                        print(f"    ✓ Report '{report_name}' has {len(comments)} comment(s)")
                
                # Show progress every 10 reports
                if checked_count % 10 == 0:
                    print(f"    ... checked {checked_count}/{len(all_reports)} reports ...")
            
            print()
            print(f"  ✓ Checked {checked_count} reports")
            print(f"  ✓ Found {len(reports_with_comments)} reports with approver comments")
            
            test_result['passed'] = True
            test_result['response'] = {
                'total_reports_checked': checked_count,
                'reports_with_comments': len(reports_with_comments),
                'reports': reports_with_comments
            }
            
            # Display results
            if len(reports_with_comments) > 0:
                print(f"\n  Reports with Approver Comments:")
                print(f"  " + "=" * 76)
                
                for i, report in enumerate(reports_with_comments, 1):
                    print(f"\n  {i}. {report['report_name']}")
                    print(f"     Report ID: {report['report_id']}")
                    print(f"     Owner: {report['owner_name']}")
                    print(f"     Total: {report['total']} {report['currency']}")
                    print(f"     Status: {report['approval_status']}")
                    print(f"     Comments ({report['comment_count']}):")
                    
                    for j, comment in enumerate(report['comments'], 1):
                        print(f"       {j}) By: {comment['actor']}")
                        print(f"          Action: {comment['action']}")
                        print(f"          Date: {comment['date']}")
                        print(f"          Comment: {comment['comment']}")
                        if comment['step_name']:
                            print(f"          Step: {comment['step_name']}")
                
                print(f"\n  Summary:")
                print(f"    • Total reports analyzed: {checked_count}")
                print(f"    • Reports with comments: {len(reports_with_comments)}")
                print(f"    • Percentage with comments: {(len(reports_with_comments)/checked_count*100):.1f}%")
            else:
                print(f"\n  ℹ️  No reports found with approver comments")
                print(f"  This could mean:")
                print(f"    - Approvers are approving without adding comments")
                print(f"    - The V4 API may not include workflow history")
                print(f"    - Comments may be stored in a different field")
                print(f"\n  💡 To create test data:")
                print(f"    1. Submit an expense report")
                print(f"    2. Have a manager/approver add a comment when approving/sending back")
                print(f"    3. Check if the comment appears in the report details")
            
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
            import traceback
            print(f"  Traceback: {traceback.format_exc()}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_031_check_specific_report_workflow(self):
        """Test 2: Check workflow structure of a single report"""
        test_name = "Examine workflow structure of a report"
        print(f"Test 2: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            # Get one report to examine its structure
            print(f"  Getting a sample report to examine workflow structure...")
            
            params = {'user': 'ALL', 'limit': 1}
            reports_result = self.sdk.get_expense_reports(params)
            
            if reports_result['success'] and len(reports_result['reports']) > 0:
                report = reports_result['reports'][0]
                report_id = report.get('ID') or report.get('id')
                report_name = report.get('ReportName') or report.get('name', 'N/A')
                
                print(f"  ✓ Sample report: {report_name} (ID: {report_id})")
                print()
                
                # Get full details
                details_result = self.get_report_with_workflow(report_id)
                
                if details_result['success']:
                    report_data = details_result['report']
                    
                    # Show the structure
                    print(f"  Report structure (top-level fields):")
                    for key in sorted(report_data.keys()):
                        value = report_data[key]
                        value_type = type(value).__name__
                        if isinstance(value, list):
                            print(f"    • {key}: [{value_type}, length={len(value)}]")
                        elif isinstance(value, dict):
                            print(f"    • {key}: [{value_type}, keys={len(value)}]")
                        else:
                            # Truncate long values
                            value_str = str(value)
                            if len(value_str) > 50:
                                value_str = value_str[:50] + "..."
                            print(f"    • {key}: {value_str}")
                    
                    # Check for workflow-related fields
                    print(f"\n  Workflow-related fields:")
                    workflow_keys = [k for k in report_data.keys() if 'workflow' in k.lower() or 
                                    'comment' in k.lower() or 'approv' in k.lower() or
                                    'history' in k.lower() or 'step' in k.lower()]
                    
                    if workflow_keys:
                        for key in workflow_keys:
                            value = report_data[key]
                            print(f"    • {key}:")
                            if isinstance(value, list) and len(value) > 0:
                                print(f"      Type: list with {len(value)} items")
                                print(f"      First item keys: {list(value[0].keys()) if isinstance(value[0], dict) else 'not a dict'}")
                            elif isinstance(value, dict):
                                print(f"      Type: dict")
                                print(f"      Keys: {list(value.keys())}")
                            else:
                                print(f"      Value: {value}")
                    else:
                        print(f"    ℹ️  No obvious workflow fields found")
                        print(f"    The V4 API may not return workflow history")
                    
                    test_result['passed'] = True
                    test_result['response'] = {
                        'report_id': report_id,
                        'report_name': report_name,
                        'available_fields': list(report_data.keys()),
                        'workflow_fields': workflow_keys
                    }
                else:
                    test_result['error'] = details_result.get('error', 'Unknown error')
                    print(f"  ✗ Failed to get report details: {test_result['error']}")
            else:
                test_result['error'] = 'No reports available to examine'
                print(f"  ✗ {test_result['error']}")
                
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Exception: {str(e)}")
        
        print()
        self.results['tests'].append(test_result)
        return test_result['passed']
    
    def test_031_check_v2_api_workflow(self):
        """Test 3: Check V2 API for workflow/comment information"""
        test_name = "Check V2 API for workflow information"
        print(f"Test 3: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/expense/expensereport/v2.0/report/{reportId}',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            # Get one report to examine via V2 API
            print(f"  Getting a sample report via V2 API (for comparison)...")
            
            params = {'user': 'ALL', 'limit': 1}
            reports_result = self.sdk.get_expense_reports(params)
            
            if reports_result['success'] and len(reports_result['reports']) > 0:
                report = reports_result['reports'][0]
                report_id = report.get('ID') or report.get('id')
                report_name = report.get('ReportName') or report.get('name', 'N/A')
                
                print(f"  ✓ Sample report: {report_name} (ID: {report_id})")
                print()
                
                # Get full details using V2 API
                v2_result = self.sdk.get_report_full_details(report_id)
                
                if v2_result['success']:
                    report_data = v2_result['report']
                    
                    # Look for workflow/comment fields
                    print(f"  V2 API workflow-related fields:")
                    workflow_keys = [k for k in report_data.keys() if 'workflow' in k.lower() or 
                                    'comment' in k.lower() or 'history' in k.lower() or
                                    'approval' in k.lower()]
                    
                    if workflow_keys:
                        for key in workflow_keys:
                            value = report_data[key]
                            print(f"    • {key}:")
                            if isinstance(value, list):
                                print(f"      Length: {len(value)}")
                                if len(value) > 0:
                                    print(f"      Sample: {str(value[0])[:200]}")
                            elif isinstance(value, dict):
                                print(f"      Keys: {list(value.keys())}")
                            else:
                                value_str = str(value)
                                if len(value_str) > 100:
                                    value_str = value_str[:100] + "..."
                                print(f"      Value: {value_str}")
                    else:
                        print(f"    ℹ️  No workflow/comment fields found in V2 API response")
                    
                    # Check for approval workflow URL
                    if 'WorkflowActionURL' in report_data:
                        print(f"\n  ✓ WorkflowActionURL found (for approval actions)")
                        print(f"    URL: {report_data['WorkflowActionURL'][:100]}...")
                    
                    test_result['passed'] = True
                    test_result['response'] = {
                        'report_id': report_id,
                        'report_name': report_name,
                        'workflow_fields': workflow_keys,
                        'has_workflow_url': 'WorkflowActionURL' in report_data
                    }
                else:
                    test_result['error'] = v2_result.get('error', 'Unknown error')
                    print(f"  ✗ Failed to get V2 report details: {test_result['error']}")
            else:
                test_result['error'] = 'No reports available to examine'
                print(f"  ✗ {test_result['error']}")
                
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
        results_file = Path(__file__).parent / "results" / "test_031_results.json"
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
        self.test_031_find_reports_with_approver_comments()
        self.test_031_check_specific_report_workflow()
        self.test_031_check_v2_api_workflow()
        
        # Generate report
        return self.generate_report()


def main():
    """Main test execution"""
    test_suite = TestReportsWithApproverComments()
    success = test_suite.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

