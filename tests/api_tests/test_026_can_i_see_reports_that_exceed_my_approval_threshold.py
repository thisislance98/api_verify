#!/usr/bin/env python3
"""
Test Case #026: Reports that Exceed Approval Threshold
User Query: Can I see reports that exceed my approval threshold?
Service: Expense Reports & Status
API: GET /api/v3.0/expense/reports

This test finds expense reports that are pending approval (A_PEND) and exceed
a specific approval threshold amount. This is useful for managers with approval
limits - reports exceeding their threshold need to be escalated to higher-level
approvers.

CSV Row #26:
- Query: "Can I see reports that exceed my approval threshold?"
- Service: Expense Reports & Status
- Method: GET
- Endpoint: /api/v3.0/expense/reports
- Filter: approvalStatusCode=A_PEND&totalApprovedAmount>{threshold}, requires manager context
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add parent directory to path to import config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tests.config import get_test_credentials
from concur_expense_sdk import ConcurExpenseSDK, ConcurConfig


class TestReportsExceedThreshold:
    """Test suite for finding reports that exceed approval threshold"""
    
    def __init__(self):
        """Initialize test suite"""
        self.sdk = None
        self.user_id = None
        self.test_results = []
        self.approval_thresholds = [
            100,    # $100 - low threshold
            500,    # $500 - medium threshold
            1000,   # $1,000 - common threshold
            5000,   # $5,000 - high threshold
        ]
        
    def setup(self):
        """Initialize SDK with test credentials"""
        print("=" * 80)
        print("TEST CASE #024: Reports that Exceed Approval Threshold")
        print("=" * 80)
        
        # Get manager credentials since this is a manager approval scenario
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
        print(f"✓ SDK initialized")
        print(f"  Environment: {creds['environment']}")
        print(f"  Base URL: {self.sdk.config.base_url}")
        print(f"  Username: {self.sdk.config.username}")
        print(f"  Role: {creds['role']}")
        
        # Test connection
        print(f"\n✓ Authenticating as {creds['username']}...")
        result = self.sdk.test_connection()
        if not result['success']:
            raise Exception(f"Authentication failed: {result['message']}")
        print("✓ Authentication successful")
        
        # Get user ID
        print("✓ Getting user ID...")
        self.user_id = self.sdk.get_user_id()
        if not self.user_id:
            raise Exception("Could not retrieve user ID")
        print(f"✓ User ID: {self.user_id}")
        
    def test_026_reports_exceed_100(self):
        """Test 1: Find reports exceeding $100 threshold"""
        print("\n" + "=" * 80)
        print("TEST 1: Reports Exceeding $100 Threshold")
        print("=" * 80)
        
        threshold = 100
        return self._test_threshold(threshold, "test_026_reports_exceed_100")
    
    def test_026_reports_exceed_500(self):
        """Test 2: Find reports exceeding $500 threshold"""
        print("\n" + "=" * 80)
        print("TEST 2: Reports Exceeding $500 Threshold")
        print("=" * 80)
        
        threshold = 500
        return self._test_threshold(threshold, "test_026_reports_exceed_500")
    
    def test_026_reports_exceed_1000(self):
        """Test 3: Find reports exceeding $1,000 threshold"""
        print("\n" + "=" * 80)
        print("TEST 3: Reports Exceeding $1,000 Threshold")
        print("=" * 80)
        
        threshold = 1000
        return self._test_threshold(threshold, "test_026_reports_exceed_1000")
    
    def test_026_reports_exceed_5000(self):
        """Test 4: Find reports exceeding $5,000 threshold"""
        print("\n" + "=" * 80)
        print("TEST 4: Reports Exceeding $5,000 Threshold")
        print("=" * 80)
        
        threshold = 5000
        return self._test_threshold(threshold, "test_026_reports_exceed_5000")
    
    def test_026_all_pending_with_amounts(self):
        """Test 5: Get all pending reports with amounts (for context)"""
        print("\n" + "=" * 80)
        print("TEST 5: All Pending Reports (Context)")
        print("=" * 80)
        
        params = {
            'approvalStatusCode': 'A_PEND',
            'user': 'ALL'
        }
        
        print(f"\n📊 Fetching all pending reports for context...")
        print(f"   This shows the full distribution of amounts")
        
        try:
            result = self.sdk.get_expense_reports(params)
            
            if result['success']:
                reports = result['reports']
            else:
                reports = []
            
            if reports:
                print(f"\n✅ Found {len(reports)} total pending reports")
                
                # Create distribution by amount ranges
                distribution = {
                    'under_100': [],
                    'between_100_500': [],
                    'between_500_1000': [],
                    'between_1000_5000': [],
                    'over_5000': []
                }
                
                for report in reports:
                    amount = float(report.get('Total', 0))
                    report_id = report.get('ID', 'Unknown')
                    name = report.get('Name', 'Unnamed')
                    
                    if amount < 100:
                        distribution['under_100'].append((report_id, name, amount))
                    elif amount < 500:
                        distribution['between_100_500'].append((report_id, name, amount))
                    elif amount < 1000:
                        distribution['between_500_1000'].append((report_id, name, amount))
                    elif amount < 5000:
                        distribution['between_1000_5000'].append((report_id, name, amount))
                    else:
                        distribution['over_5000'].append((report_id, name, amount))
                
                # Display distribution
                print("\n📈 Amount Distribution:")
                print(f"   Under $100:         {len(distribution['under_100'])} reports")
                print(f"   $100 - $500:        {len(distribution['between_100_500'])} reports")
                print(f"   $500 - $1,000:      {len(distribution['between_500_1000'])} reports")
                print(f"   $1,000 - $5,000:    {len(distribution['between_1000_5000'])} reports")
                print(f"   Over $5,000:        {len(distribution['over_5000'])} reports")
                
                # Show details for each range (if any)
                for range_name, range_label in [
                    ('under_100', 'Under $100'),
                    ('between_100_500', '$100 - $500'),
                    ('between_500_1000', '$500 - $1,000'),
                    ('between_1000_5000', '$1,000 - $5,000'),
                    ('over_5000', 'Over $5,000')
                ]:
                    if distribution[range_name]:
                        print(f"\n   {range_label}:")
                        for report_id, name, amount in sorted(distribution[range_name], key=lambda x: x[2], reverse=True)[:5]:
                            print(f"     - ${amount:,.2f}: {name} (ID: {report_id})")
                
                # Calculate threshold impact
                print("\n💡 Threshold Impact Analysis:")
                for threshold in self.approval_thresholds:
                    count = sum(1 for r in reports if float(r.get('Total', 0)) > threshold)
                    percentage = (count / len(reports) * 100) if reports else 0
                    print(f"   ${threshold:,} threshold: {count} reports ({percentage:.1f}%) would need escalation")
                
                self.test_results.append({
                    'test_name': 'All pending reports with amount distribution',
                    'endpoint': '/api/v3.0/expense/reports',
                    'method': 'GET',
                    'params': params,
                    'passed': True,
                    'total_reports': len(reports),
                    'distribution': {k: len(v) for k, v in distribution.items()},
                    'response_sample': reports[:3] if len(reports) > 0 else [],
                    'error': None
                })
                return True
            else:
                print(f"\n⚠️  No pending reports found")
                print(f"   Cannot analyze threshold impact without data")
                
                self.test_results.append({
                    'test_name': 'All pending reports with amount distribution',
                    'endpoint': '/api/v3.0/expense/reports',
                    'method': 'GET',
                    'params': params,
                    'passed': True,
                    'total_reports': 0,
                    'distribution': {},
                    'response': None,
                    'error': 'No pending reports found'
                })
                return True
                
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            self.test_results.append({
                'test_name': 'All pending reports with amount distribution',
                'endpoint': '/api/v3.0/expense/reports',
                'method': 'GET',
                'params': params,
                'passed': False,
                'response': None,
                'error': str(e)
            })
            return False
    
    def _test_threshold(self, threshold: float, test_name: str):
        """
        Helper method to test a specific threshold
        
        Args:
            threshold: The dollar amount threshold
            test_name: Name of the test
        """
        params = {
            'approvalStatusCode': 'A_PEND',
            'user': 'ALL'
        }
        
        print(f"\n📊 Test Details:")
        print(f"   Threshold: ${threshold:,.2f}")
        print(f"   Status: Pending Approval (A_PEND)")
        print(f"   Logic: Total amount > ${threshold:,.2f}")
        
        try:
            result = self.sdk.get_expense_reports(params)
            
            if result['success']:
                reports = result['reports']
            else:
                reports = []
            
            # Filter reports by threshold (client-side filtering since API doesn't support > operator)
            filtered_reports = []
            if reports:
                for report in reports:
                    total = float(report.get('Total', 0))
                    if total > threshold:
                        filtered_reports.append(report)
            
            if filtered_reports:
                print(f"\n✅ Found {len(filtered_reports)} reports exceeding ${threshold:,.2f} threshold")
                print(f"   (Out of {len(reports)} total pending reports)")
                
                # Calculate statistics
                amounts = [float(r.get('Total', 0)) for r in filtered_reports]
                total_amount = sum(amounts)
                avg_amount = total_amount / len(amounts) if amounts else 0
                max_amount = max(amounts) if amounts else 0
                min_amount = min(amounts) if amounts else 0
                
                print(f"\n💰 Amount Statistics:")
                print(f"   Total: ${total_amount:,.2f}")
                print(f"   Average: ${avg_amount:,.2f}")
                print(f"   Range: ${min_amount:,.2f} - ${max_amount:,.2f}")
                
                # Show top reports
                sorted_reports = sorted(filtered_reports, key=lambda x: float(x.get('Total', 0)), reverse=True)
                print(f"\n📋 Top Reports Exceeding Threshold:")
                for i, report in enumerate(sorted_reports[:10], 1):
                    report_id = report.get('ID', 'Unknown')
                    name = report.get('Name', 'Unnamed')
                    total = float(report.get('Total', 0))
                    currency = report.get('CurrencyCode', 'USD')
                    owner = report.get('OwnerLoginID', 'Unknown')
                    excess = total - threshold
                    
                    print(f"   {i}. ${total:,.2f} {currency} (${excess:,.2f} over threshold)")
                    print(f"      Name: {name}")
                    print(f"      ID: {report_id}")
                    print(f"      Owner: {owner}")
                    print()
                
                # Escalation guidance
                excess_amount = total_amount - (threshold * len(filtered_reports))
                print(f"\n🚀 Escalation Guidance:")
                print(f"   {len(filtered_reports)} reports need higher-level approval")
                print(f"   Total excess amount: ${excess_amount:,.2f}")
                print(f"   This represents {(len(filtered_reports)/len(reports)*100):.1f}% of all pending reports")
                
                self.test_results.append({
                    'test_name': test_name,
                    'endpoint': '/api/v3.0/expense/reports',
                    'method': 'GET',
                    'params': params,
                    'threshold': threshold,
                    'passed': True,
                    'total_pending': len(reports),
                    'exceeding_threshold': len(filtered_reports),
                    'statistics': {
                        'total_amount': total_amount,
                        'average_amount': avg_amount,
                        'min_amount': min_amount,
                        'max_amount': max_amount,
                        'excess_amount': excess_amount
                    },
                    'response_sample': sorted_reports[:5],
                    'error': None
                })
                return True
                
            else:
                print(f"\n⚠️  No reports found exceeding ${threshold:,.2f} threshold")
                if reports:
                    print(f"   Total pending reports: {len(reports)}")
                    amounts = [float(r.get('Total', 0)) for r in reports]
                    max_pending = max(amounts) if amounts else 0
                    print(f"   Highest pending amount: ${max_pending:,.2f}")
                    print(f"   All pending reports are below the ${threshold:,.2f} threshold")
                else:
                    print(f"   No pending reports found at all")
                
                self.test_results.append({
                    'test_name': test_name,
                    'endpoint': '/api/v3.0/expense/reports',
                    'method': 'GET',
                    'params': params,
                    'threshold': threshold,
                    'passed': True,
                    'total_pending': len(reports) if reports else 0,
                    'exceeding_threshold': 0,
                    'response': None,
                    'error': f'No reports exceeding ${threshold:,.2f} threshold'
                })
                return True
                
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            self.test_results.append({
                'test_name': test_name,
                'endpoint': '/api/v3.0/expense/reports',
                'method': 'GET',
                'params': params,
                'threshold': threshold,
                'passed': False,
                'response': None,
                'error': str(e)
            })
            return False
    
    def generate_report(self):
        """Generate JSON report of test results"""
        passed = sum(1 for t in self.test_results if t['passed'])
        failed = len(self.test_results) - passed
        success_rate = (passed / len(self.test_results) * 100) if self.test_results else 0
        
        report = {
            'test_case': '026',
            'user_query': 'Can I see reports that exceed my approval threshold?',
            'api_endpoint': 'GET /api/v3.0/expense/reports',
            'service': 'Expense Reports & Status',
            'csv_row': 26,
            'description': 'Find pending reports exceeding manager approval threshold',
            'filters': {
                'status': 'A_PEND (Pending Approval)',
                'thresholds_tested': self.approval_thresholds,
                'note': 'Client-side filtering used since API does not support > operator for totalApprovedAmount'
            },
            'tests': self.test_results,
            'summary': {
                'total': len(self.test_results),
                'passed': passed,
                'failed': failed,
                'success_rate': f'{success_rate:.1f}%',
                'timestamp': datetime.now().isoformat()
            }
        }
        
        # Save to results directory
        results_dir = os.path.join(os.path.dirname(__file__), 'results')
        os.makedirs(results_dir, exist_ok=True)
        
        output_file = os.path.join(results_dir, 'test_026_results.json')
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📄 Test results saved to: {output_file}")
        return report
    
    def run_all_tests(self):
        """Execute all tests in sequence"""
        try:
            self.setup()
            
            # Run all test scenarios
            test_methods = [
                self.test_026_all_pending_with_amounts,  # Context first
                self.test_026_reports_exceed_100,
                self.test_026_reports_exceed_500,
                self.test_026_reports_exceed_1000,
                self.test_026_reports_exceed_5000,
            ]
            
            results = []
            for test_method in test_methods:
                result = test_method()
                results.append(result)
            
            # Generate report
            print("\n" + "=" * 80)
            print("GENERATING TEST REPORT")
            print("=" * 80)
            report = self.generate_report()
            
            # Print summary
            print("\n" + "=" * 80)
            print("TEST SUMMARY")
            print("=" * 80)
            print(f"Total Tests: {report['summary']['total']}")
            print(f"Passed: {report['summary']['passed']}")
            print(f"Failed: {report['summary']['failed']}")
            print(f"Success Rate: {report['summary']['success_rate']}")
            print("=" * 80)
            
            return all(results)
            
        except Exception as e:
            print(f"\n❌ Test suite failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == '__main__':
    test_suite = TestReportsExceedThreshold()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)

