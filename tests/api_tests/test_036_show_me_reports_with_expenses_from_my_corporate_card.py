#!/usr/bin/env python3
"""
Test Case #036: Reports with Corporate Card Expenses
User Query: Show me reports with expenses from my corporate card
Service: Expense Reports & Status
API: GET /api/v3.0/expense/reports

Tests the ability to find expense reports that contain expenses paid via corporate card.
This is useful for:
- Reconciling corporate card statements
- Identifying card-based vs reimbursable expenses
- Auditing corporate card usage
- Tracking company-paid vs employee-paid expenses

CBCP = Company Billed Corporate Pay (expenses charged directly to company card)
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tests.config import get_test_credentials
from concur_expense_sdk import ConcurExpenseSDK, ConcurConfig


class TestReportsWithCorporateCard:
    def __init__(self):
        self.sdk = None
        self.test_results = {
            "test_case": "036",
            "user_query": "Show me reports with expenses from my corporate card",
            "api_endpoint": "GET /api/v3.0/expense/reports",
            "service": "Expense Reports & Status",
            "tests": []
        }
        
    def setup(self):
        """Initialize SDK with test credentials"""
        print("=" * 80)
        print("TEST #036: Reports with Corporate Card Expenses")
        print("=" * 80)
        print("\nSetting up test environment...")
        
        # Get credentials for integration environment
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
        print(f"✓ Authenticated as: {creds['username']}")
        print(f"✓ Environment: {creds['base_url']}")
        
    def test_036_all_corporate_card_reports(self):
        """Test 1: Find all reports with corporate card expenses"""
        print("\n" + "-" * 80)
        print("Test 1: All Reports with Corporate Card Expenses")
        print("-" * 80)
        
        test_result = {
            "test_name": "All reports with corporate card expenses",
            "endpoint": "/api/v3.0/expense/reports",
            "method": "GET",
            "parameters": {
                "user": "ALL",
                "limit": 100
            }
        }
        
        try:
            # Use the SDK's specialized method for corporate card reports
            print(f"Fetching reports with corporate card expenses...")
            result = self.sdk.get_reports_with_corporate_card(limit=100, user='ALL')
            
            if not result.get('success', False):
                print(f"\n⚠ API call failed: {result.get('message', 'Unknown error')}")
                test_result["passed"] = False
                test_result["response"] = result
                test_result["error"] = result.get('message')
                self.test_results["tests"].append(test_result)
                return
            
            corporate_card_reports = result.get('reports', [])
            count = result.get('count', 0)
            total_checked = result.get('total_reports_checked', 0)
            payment_type_summary = result.get('payment_type_summary', {})
            all_payment_types = result.get('all_payment_types_seen', [])
            
            print(f"\n✓ Checked {total_checked} reports")
            print(f"✓ Found {count} reports with corporate card expenses")
            
            # Show payment type summary
            if payment_type_summary:
                print("\nPayment Type Distribution:")
                print(f"{'Payment Type':<40} {'Count':<10}")
                print("-" * 50)
                for payment_type, pcount in sorted(payment_type_summary.items(), key=lambda x: x[1], reverse=True):
                    marker = "🔶" if any(ind in payment_type.lower() for ind in ['corporate', 'corp', 'card', 'cbcp', 'company']) else "  "
                    print(f"{marker} {payment_type:<38} {pcount:<10}")
            
            if corporate_card_reports:
                print(f"\nCorporate Card Reports (showing first 10 of {count}):")
                print(f"{'Report ID':<25} {'Name':<30} {'Total':<15} {'Payment Type':<20}")
                print("-" * 90)
                
                total_amount = 0
                status_summary = {}
                
                for report in corporate_card_reports[:10]:
                    report_id = report.get('id', '')
                    name = report.get('name', 'Unnamed')
                    total = report.get('total', 0)
                    currency = report.get('currency_code', 'USD')
                    payment_type = report.get('payment_type_name', 'N/A')
                    approval_status = report.get('approval_status_code', '')
                    
                    print(f"{report_id:<25} "
                          f"{name[:28]:<30} "
                          f"{total:>10,.2f} {currency:<3} "
                          f"{payment_type[:18]:<20}")
                    
                    total_amount += total
                    
                    # Track status summary
                    if approval_status not in status_summary:
                        status_summary[approval_status] = 0
                    status_summary[approval_status] += 1
                
                print(f"\nTotal Amount: ${total_amount:,.2f}")
                
                if status_summary:
                    print("\nApproval Status Breakdown:")
                    print(f"{'Status':<15} {'Count':<10}")
                    print("-" * 25)
                    for status, scount in sorted(status_summary.items()):
                        print(f"{status:<15} {scount:<10}")
                        
            else:
                print("\n⚠ No reports with corporate card expenses found")
                print("\nThis may indicate:")
                print("  - Payment types are not configured with 'CBCP' code")
                print("  - No corporate card payment type exists in this environment")
                print("  - All reports are employee reimbursable (no corporate card)")
                
                if all_payment_types:
                    print(f"\nAll payment types seen in environment ({len(all_payment_types)}):")
                    for pt in all_payment_types[:10]:
                        print(f"  - {pt}")
                    if len(all_payment_types) > 10:
                        print(f"  ... and {len(all_payment_types) - 10} more")
                
                print("\n💡 To create test data:")
                print("  1. Configure a corporate card payment type in Concur")
                print("  2. Create an expense report with corporate card expenses")
                print("  3. Use payment type code 'CBCP' or name containing 'corporate card'")
            
            test_result["passed"] = True
            test_result["response"] = {
                "corporate_card_count": count,
                "total_reports_checked": total_checked,
                "reports": corporate_card_reports[:5],  # Limit to first 5 for results
                "payment_type_summary": payment_type_summary
            }
            test_result["error"] = None
            
        except Exception as e:
            print(f"\n✗ Test failed: {str(e)}")
            test_result["passed"] = False
            test_result["response"] = None
            test_result["error"] = str(e)
        
        self.test_results["tests"].append(test_result)
        
    def test_036_my_corporate_card_reports(self):
        """Test 2: Find MY corporate card reports only"""
        print("\n" + "-" * 80)
        print("Test 2: My Corporate Card Reports")
        print("-" * 80)
        
        test_result = {
            "test_name": "My corporate card reports only",
            "endpoint": "/api/v3.0/expense/reports",
            "method": "GET",
            "parameters": {
                "user": "me",
                "limit": 50
            }
        }
        
        try:
            print(f"Fetching MY reports with corporate card expenses...")
            result = self.sdk.get_reports_with_corporate_card(limit=50, user='me')
            
            if not result.get('success', False):
                print(f"\n⚠ API call failed: {result.get('message', 'Unknown error')}")
                test_result["passed"] = False
                test_result["response"] = result
                test_result["error"] = result.get('message')
                self.test_results["tests"].append(test_result)
                return
            
            corporate_card_reports = result.get('reports', [])
            count = result.get('count', 0)
            total_checked = result.get('total_reports_checked', 0)
            
            print(f"\n✓ Checked {total_checked} of my reports")
            print(f"✓ Found {count} of my reports with corporate card expenses")
            
            if corporate_card_reports:
                print(f"\nMy Corporate Card Reports:")
                print(f"{'Report ID':<25} {'Name':<30} {'Total':<15} {'Status':<20}")
                print("-" * 90)
                
                for report in corporate_card_reports:
                    report_id = report.get('id', '')
                    name = report.get('name', 'Unnamed')
                    total = report.get('total', 0)
                    currency = report.get('currency_code', 'USD')
                    status = report.get('approval_status', 'Unknown')
                    
                    print(f"{report_id:<25} "
                          f"{name[:28]:<30} "
                          f"{total:>10,.2f} {currency:<3} "
                          f"{status[:18]:<20}")
            else:
                print("\n⚠ No corporate card reports found for current user")
                print("The authenticated user has no reports with corporate card expenses")
            
            test_result["passed"] = True
            test_result["response"] = {
                "my_corporate_card_count": count,
                "my_total_reports_checked": total_checked,
                "reports": corporate_card_reports
            }
            test_result["error"] = None
            
        except Exception as e:
            print(f"\n✗ Test failed: {str(e)}")
            test_result["passed"] = False
            test_result["response"] = None
            test_result["error"] = str(e)
        
        self.test_results["tests"].append(test_result)
    
    def test_036_get_available_payment_types(self):
        """Test 3: Get available payment types in the environment"""
        print("\n" + "-" * 80)
        print("Test 3: Available Payment Types")
        print("-" * 80)
        
        test_result = {
            "test_name": "Get available payment types",
            "endpoint": "/api/v3.0/expense/paymenttypes",
            "method": "GET",
            "parameters": {}
        }
        
        try:
            print(f"Fetching available payment types...")
            result = self.sdk.get_payment_types()
            
            if not result.get('success', False):
                print(f"\n⚠ API call failed: {result.get('message', 'Unknown error')}")
                test_result["passed"] = False
                test_result["response"] = result
                test_result["error"] = result.get('message')
                self.test_results["tests"].append(test_result)
                return
            
            payment_types = result.get('payment_types', [])
            count = result.get('count', 0)
            
            print(f"\n✓ Found {count} payment types configured")
            
            if payment_types:
                print(f"\nConfigured Payment Types:")
                print(f"{'Code':<15} {'Name':<40} {'ID':<30}")
                print("-" * 85)
                
                corporate_card_found = False
                
                for pt in payment_types:
                    code = pt.get('code', 'N/A')
                    name = pt.get('name', 'N/A')
                    pt_id = pt.get('id', 'N/A')
                    is_default = pt.get('is_default', False)
                    
                    # Check if this is a corporate card type
                    is_corp_card = False
                    if code and code.upper() in ['CBCP', 'CORP', 'CARD']:
                        is_corp_card = True
                    elif name:
                        corp_indicators = ['corporate card', 'company card', 'corp card', 'cbcp', 'business card']
                        if any(ind in name.lower() for ind in corp_indicators):
                            is_corp_card = True
                    
                    marker = "🔶" if is_corp_card else "  "
                    default_marker = " [DEFAULT]" if is_default else ""
                    
                    print(f"{marker} {code:<13} {name[:38]:<40} {pt_id[:28]:<30}{default_marker}")
                    
                    if is_corp_card:
                        corporate_card_found = True
                
                if not corporate_card_found:
                    print("\n⚠ No corporate card payment type found")
                    print("Expected payment type codes: CBCP, CORP, CARD")
                    print("Or names containing: 'corporate card', 'company card', etc.")
                else:
                    print("\n✓ Corporate card payment type(s) configured (marked with 🔶)")
            else:
                print("\n⚠ No payment types found")
                print("This environment may not have payment types configured")
            
            test_result["passed"] = True
            test_result["response"] = {
                "payment_types_count": count,
                "payment_types": payment_types
            }
            test_result["error"] = None
            
        except Exception as e:
            print(f"\n✗ Test failed: {str(e)}")
            test_result["passed"] = False
            test_result["response"] = None
            test_result["error"] = str(e)
        
        self.test_results["tests"].append(test_result)
    
    def test_036_corporate_card_by_approval_status(self):
        """Test 4: Analyze corporate card reports by approval status"""
        print("\n" + "-" * 80)
        print("Test 4: Corporate Card Reports by Approval Status")
        print("-" * 80)
        
        test_result = {
            "test_name": "Corporate card reports grouped by approval status",
            "endpoint": "/api/v3.0/expense/reports",
            "method": "GET",
            "parameters": {
                "user": "ALL",
                "limit": 100
            }
        }
        
        try:
            print(f"Analyzing corporate card reports by approval status...")
            result = self.sdk.get_reports_with_corporate_card(limit=100, user='ALL')
            
            if not result.get('success', False):
                print(f"\n⚠ API call failed: {result.get('message', 'Unknown error')}")
                test_result["passed"] = False
                test_result["response"] = result
                test_result["error"] = result.get('message')
                self.test_results["tests"].append(test_result)
                return
            
            corporate_card_reports = result.get('reports', [])
            count = result.get('count', 0)
            
            print(f"\n✓ Analyzing {count} corporate card reports")
            
            if corporate_card_reports:
                # Group by approval status
                status_groups = {}
                status_totals = {}
                
                for report in corporate_card_reports:
                    status_code = report.get('approval_status_code', 'UNKNOWN')
                    status_name = report.get('approval_status', 'Unknown')
                    total = report.get('total', 0)
                    
                    if status_code not in status_groups:
                        status_groups[status_code] = []
                        status_totals[status_code] = {'count': 0, 'amount': 0, 'name': status_name}
                    
                    status_groups[status_code].append(report)
                    status_totals[status_code]['count'] += 1
                    status_totals[status_code]['amount'] += total
                
                print(f"\nCorporate Card Reports by Approval Status:")
                print(f"{'Status Code':<15} {'Status Name':<25} {'Count':<10} {'Total Amount':<20}")
                print("-" * 70)
                
                for status_code in sorted(status_totals.keys()):
                    info = status_totals[status_code]
                    print(f"{status_code:<15} "
                          f"{info['name'][:23]:<25} "
                          f"{info['count']:<10} "
                          f"${info['amount']:>15,.2f}")
                
                # Show details for each status
                for status_code, reports in sorted(status_groups.items()):
                    print(f"\n{status_code} - {status_totals[status_code]['name']} ({len(reports)} reports):")
                    for i, report in enumerate(reports[:3], 1):  # Show first 3 per status
                        name = report.get('name', 'Unnamed')
                        total = report.get('total', 0)
                        currency = report.get('currency_code', 'USD')
                        owner = report.get('owner_name', 'Unknown')
                        print(f"  {i}. {name[:40]} - {total:,.2f} {currency} ({owner})")
                    if len(reports) > 3:
                        print(f"  ... and {len(reports) - 3} more")
                
                test_result["passed"] = True
                test_result["response"] = {
                    "status_summary": status_totals,
                    "total_corporate_card_reports": count
                }
                test_result["error"] = None
            else:
                print("\n⚠ No corporate card reports found for analysis")
                test_result["passed"] = True
                test_result["response"] = {
                    "status_summary": {},
                    "total_corporate_card_reports": 0
                }
                test_result["error"] = None
            
        except Exception as e:
            print(f"\n✗ Test failed: {str(e)}")
            test_result["passed"] = False
            test_result["response"] = None
            test_result["error"] = str(e)
        
        self.test_results["tests"].append(test_result)
    
    def generate_report(self):
        """Generate JSON report with test results"""
        # Calculate summary
        total_tests = len(self.test_results["tests"])
        passed_tests = sum(1 for test in self.test_results["tests"] if test["passed"])
        failed_tests = total_tests - passed_tests
        
        self.test_results["summary"] = {
            "total": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": f"{(passed_tests/total_tests*100) if total_tests > 0 else 0:.1f}%",
            "timestamp": datetime.now().isoformat()
        }
        
        # Save to file
        results_dir = os.path.join(os.path.dirname(__file__), 'results')
        os.makedirs(results_dir, exist_ok=True)
        
        output_file = os.path.join(results_dir, 'test_036_results.json')
        with open(output_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {self.test_results['summary']['success_rate']}")
        print(f"\nResults saved to: {output_file}")
        print("=" * 80)
        
    def run_all_tests(self):
        """Execute all tests in sequence"""
        try:
            self.setup()
            self.test_036_all_corporate_card_reports()
            self.test_036_my_corporate_card_reports()
            self.test_036_get_available_payment_types()
            self.test_036_corporate_card_by_approval_status()
        except Exception as e:
            print(f"\n✗ Fatal error during test execution: {str(e)}")
        finally:
            self.generate_report()


if __name__ == "__main__":
    test_suite = TestReportsWithCorporateCard()
    test_suite.run_all_tests()

