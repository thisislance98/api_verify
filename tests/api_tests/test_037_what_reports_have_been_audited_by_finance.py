#!/usr/bin/env python3
"""
Test Case #037: Reports Audited by Finance
User Query: What reports have been audited by finance?
Service: Expense Reports & Status
API: GET /api/v3.0/expense/reports

This test verifies retrieving expense reports that have been audited by finance.
The audit status may be indicated by:
- Standard AuditStatus field
- AuditDate field (presence indicates report was audited)
- Custom audit fields (company-specific configuration)
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


class TestAuditedReports:
    """Test suite for reports audited by finance"""
    
    def __init__(self):
        self.sdk = None
        self.results = {
            'test_case': '037',
            'user_query': 'What reports have been audited by finance?',
            'api_endpoint': 'GET /api/v3.0/expense/reports (filter by audit status)',
            'service': 'Expense Reports & Status',
            'tests': [],
            'summary': {}
        }
    
    def setup(self):
        """Initialize SDK and authenticate"""
        print("=" * 80)
        print("Test Case #037: Reports Audited by Finance")
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
    
    def test_037_basic_retrieval(self):
        """Test 1: Basic retrieval of audited reports"""
        test_name = "Basic retrieval of audited reports"
        print(f"Test 1: {test_name}")
        print("-" * 80)
        
        test_result = {
            'test_name': test_name,
            'endpoint': '/api/v3.0/expense/reports (filter by audit status)',
            'method': 'GET',
            'passed': False,
            'response': None,
            'error': None
        }
        
        try:
            result = self.sdk.get_audited_reports(limit=100, user='ALL')
            
            if result['success']:
                test_result['passed'] = True
                test_result['response'] = {
                    'count': result['count'],
                    'total_retrieved': result['total_retrieved'],
                    'message': result['message'],
                    'reports': result['reports'][:5] if result['reports'] else []  # Sample first 5
                }
                
                print(f"  ✓ Successfully retrieved audited reports")
                print(f"  Total reports retrieved: {result['total_retrieved']}")
                print(f"  Audited reports found: {result['count']}")
                print(f"  Audit rate: {(result['count'] / result['total_retrieved'] * 100) if result['total_retrieved'] > 0 else 0:.1f}%")
                
                if result['count'] > 0:
                    print(f"\n  Sample Audited Reports (first 5):")
                    for i, report in enumerate(result['reports'][:5], 1):
                        print(f"\n  Report #{i}:")
                        print(f"    ID: {report.get('id')}")
                        print(f"    Name: {report.get('name')}")
                        print(f"    Owner: {report.get('owner_name')} ({report.get('owner_login_id')})")
                        print(f"    Total: {report.get('currency_code', '')} {report.get('total', 0):.2f}")
                        print(f"    Approval Status: {report.get('approval_status')} ({report.get('approval_status_code')})")
                        print(f"    Payment Status: {report.get('payment_status_name')} ({report.get('payment_status_code')})")
                        print(f"    Audit Indicator: {report.get('audit_indicator')}")
                        print(f"    Audit Status: {report.get('audit_status')}")
                        print(f"    Audit Date: {report.get('audit_date')}")
                        print(f"    Audited By: {report.get('audited_by')}")
                        if report.get('days_since_audit') is not None:
                            print(f"    Days Since Audit: {report.get('days_since_audit')}")
                else:
                    print(f"\n  ⚠️  No audited reports found")
                    print(f"  This could mean:")
                    print(f"    - No reports have been audited yet")
                    print(f"    - Audit fields are not populated in this environment")
                    print(f"    - Audit status is tracked using custom fields")
                    print(f"    - This environment doesn't use the audit feature")
            else:
                test_result['passed'] = False
                test_result['error'] = result.get('error')
                print(f"  ✗ Failed to retrieve reports: {result.get('error')}")
            
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Test failed with exception: {str(e)}")
        
        self.results['tests'].append(test_result)
        print()
    
    def test_037_check_audit_fields(self):
        """Test 2: Check which audit fields are available in the API response"""
        test_name = "Check available audit fields"
        print(f"Test 2: {test_name}")
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
            # Get a sample of all reports to inspect fields
            result = self.sdk.get_expense_reports(params={
                'limit': 10,
                'user': 'ALL'
            })
            
            if result['success']:
                items = result.get('Items', [])
                
                # Collect all unique field names that could relate to audit
                audit_related_fields = set()
                sample_values = {}
                
                for item in items:
                    for key in item.keys():
                        if 'audit' in key.lower():
                            audit_related_fields.add(key)
                            # Store a sample value if it exists
                            if key not in sample_values and item.get(key):
                                sample_values[key] = item.get(key)
                
                test_result['passed'] = True
                test_result['response'] = {
                    'total_reports_checked': len(items),
                    'audit_related_fields': list(audit_related_fields),
                    'sample_values': sample_values
                }
                
                print(f"  ✓ Field inspection completed")
                print(f"  Reports checked: {len(items)}")
                print(f"  Audit-related fields found: {len(audit_related_fields)}")
                
                if audit_related_fields:
                    print(f"\n  Available Audit Fields:")
                    for field in sorted(audit_related_fields):
                        sample = sample_values.get(field, 'N/A')
                        print(f"    - {field}: {sample}")
                else:
                    print(f"\n  ⚠️  No audit-related fields found in API response")
                    print(f"  This suggests:")
                    print(f"    - Audit feature may not be enabled")
                    print(f"    - Audit tracking uses custom fields")
                    print(f"    - Audit data not available in V3 API")
            else:
                test_result['passed'] = False
                test_result['error'] = result.get('error')
                print(f"  ✗ Failed to retrieve reports: {result.get('error')}")
            
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Test failed with exception: {str(e)}")
        
        self.results['tests'].append(test_result)
        print()
    
    def test_037_audit_status_distribution(self):
        """Test 3: Analyze distribution of audit statuses"""
        test_name = "Analyze audit status distribution"
        print(f"Test 3: {test_name}")
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
            result = self.sdk.get_audited_reports(limit=100, user='ALL')
            
            if result['success']:
                reports = result['reports']
                
                # Analyze audit indicators
                audit_indicator_counts = {}
                for report in reports:
                    indicator = report.get('audit_indicator', 'Unknown')
                    audit_indicator_counts[indicator] = audit_indicator_counts.get(indicator, 0) + 1
                
                # Analyze approval status of audited reports
                approval_status_counts = {}
                for report in reports:
                    status = report.get('approval_status_code', 'Unknown')
                    approval_status_counts[status] = approval_status_counts.get(status, 0) + 1
                
                # Analyze payment status of audited reports
                payment_status_counts = {}
                for report in reports:
                    status = report.get('payment_status_code', 'Unknown')
                    payment_status_counts[status] = payment_status_counts.get(status, 0) + 1
                
                test_result['passed'] = True
                test_result['response'] = {
                    'total_audited_reports': len(reports),
                    'audit_indicator_distribution': audit_indicator_counts,
                    'approval_status_distribution': approval_status_counts,
                    'payment_status_distribution': payment_status_counts
                }
                
                print(f"  ✓ Distribution analysis completed")
                print(f"  Total audited reports: {len(reports)}")
                
                if audit_indicator_counts:
                    print(f"\n  Audit Indicators:")
                    for indicator, count in sorted(audit_indicator_counts.items()):
                        print(f"    {indicator}: {count}")
                
                if approval_status_counts:
                    print(f"\n  Approval Status Distribution:")
                    for status, count in sorted(approval_status_counts.items()):
                        print(f"    {status}: {count}")
                
                if payment_status_counts:
                    print(f"\n  Payment Status Distribution:")
                    for status, count in sorted(payment_status_counts.items()):
                        print(f"    {status}: {count}")
                
                if len(reports) == 0:
                    print(f"  ⚠️  No audited reports to analyze")
            else:
                test_result['passed'] = False
                test_result['error'] = result.get('error')
                print(f"  ✗ Failed to retrieve reports: {result.get('error')}")
            
        except Exception as e:
            test_result['error'] = str(e)
            print(f"  ✗ Test failed with exception: {str(e)}")
        
        self.results['tests'].append(test_result)
        print()
    
    def test_037_audit_timeline(self):
        """Test 4: Analyze audit timeline and patterns"""
        test_name = "Analyze audit timeline"
        print(f"Test 4: {test_name}")
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
            result = self.sdk.get_audited_reports(limit=100, user='ALL')
            
            if result['success']:
                reports = result['reports']
                
                if len(reports) > 0:
                    # Filter reports with audit dates
                    reports_with_dates = [r for r in reports if r.get('days_since_audit') is not None]
                    
                    if reports_with_dates:
                        days_list = [r['days_since_audit'] for r in reports_with_dates]
                        avg_days = sum(days_list) / len(days_list)
                        max_days = max(days_list)
                        min_days = min(days_list)
                        
                        # Categorize by time periods
                        last_week = sum(1 for d in days_list if d <= 7)
                        last_month = sum(1 for d in days_list if d <= 30)
                        last_quarter = sum(1 for d in days_list if d <= 90)
                        
                        test_result['passed'] = True
                        test_result['response'] = {
                            'total_audited_reports': len(reports),
                            'reports_with_audit_dates': len(reports_with_dates),
                            'average_days_since_audit': round(avg_days, 1),
                            'max_days_since_audit': max_days,
                            'min_days_since_audit': min_days,
                            'audited_last_week': last_week,
                            'audited_last_month': last_month,
                            'audited_last_quarter': last_quarter
                        }
                        
                        print(f"  ✓ Timeline analysis completed")
                        print(f"  Total audited reports: {len(reports)}")
                        print(f"  Reports with audit dates: {len(reports_with_dates)}")
                        print(f"  Average days since audit: {avg_days:.1f}")
                        print(f"  Max days since audit: {max_days}")
                        print(f"  Min days since audit: {min_days}")
                        print(f"\n  Audit Timeline:")
                        print(f"    Last 7 days: {last_week} reports")
                        print(f"    Last 30 days: {last_month} reports")
                        print(f"    Last 90 days: {last_quarter} reports")
                    else:
                        test_result['passed'] = True
                        test_result['response'] = {
                            'message': 'No audit date information available',
                            'total_audited_reports': len(reports)
                        }
                        print(f"  ⚠️  No audit date information available")
                        print(f"  Found {len(reports)} audited reports but no date information")
                else:
                    test_result['passed'] = True
                    test_result['response'] = {'message': 'No audited reports found'}
                    print(f"  ⚠️  No audited reports to analyze")
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
        
        results_file = results_dir / 'test_037_results.json'
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
        
        self.test_037_basic_retrieval()
        self.test_037_check_audit_fields()
        self.test_037_audit_status_distribution()
        self.test_037_audit_timeline()
        
        self.generate_report()
        
        # Return True if all tests passed
        return self.results['summary']['failed'] == 0


if __name__ == "__main__":
    test_suite = TestAuditedReports()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)

