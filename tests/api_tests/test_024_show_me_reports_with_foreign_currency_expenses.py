#!/usr/bin/env python3
"""
Test Case #024: Reports with Foreign Currency Expenses
User Query: Show me reports with foreign currency expenses
Service: Expense Reports & Status
API: GET /api/v3.0/expense/reports

Tests the ability to find expense reports that contain foreign currency expenses.
This is useful for:
- Identifying international travel expenses
- Currency conversion review
- Foreign exchange rate audit
- International expense reporting
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tests.config import get_test_credentials
from concur_expense_sdk import ConcurExpenseSDK, ConcurConfig


class TestReportsWithForeignCurrency:
    def __init__(self):
        self.sdk = None
        self.test_results = {
            "test_case": "024",
            "user_query": "Show me reports with foreign currency expenses",
            "api_endpoint": "GET /api/v3.0/expense/reports",
            "service": "Expense Reports & Status",
            "tests": []
        }
        
    def setup(self):
        """Initialize SDK with test credentials"""
        print("=" * 80)
        print("TEST #024: Reports with Foreign Currency Expenses")
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
        
    def test_024_all_foreign_currency_reports(self):
        """Test 1: Find all reports with foreign currency expenses"""
        print("\n" + "-" * 80)
        print("Test 1: All Reports with Foreign Currency")
        print("-" * 80)
        
        test_result = {
            "test_name": "All reports with foreign currency",
            "endpoint": "/api/v3.0/expense/reports",
            "method": "GET",
            "parameters": {
                "user": "ALL",
                "limit": 100
            }
        }
        
        try:
            # Use the SDK's specialized method for foreign currency reports
            print(f"Fetching reports with foreign currency...")
            result = self.sdk.get_reports_with_foreign_currency(limit=100)
            
            if not result.get('success', False):
                print(f"\n⚠ API call failed: {result.get('message', 'Unknown error')}")
                test_result["passed"] = False
                test_result["response"] = result
                test_result["error"] = result.get('message')
                self.test_results["tests"].append(test_result)
                return
            
            foreign_currency_reports = result.get('reports', [])
            count = result.get('count', 0)
            
            print(f"\n✓ Found {count} reports with foreign currency")
            
            if foreign_currency_reports:
                print("\nForeign Currency Reports:")
                print(f"{'Report ID':<25} {'Name':<30} {'Currency':<10} {'Foreign Curr':<15}")
                print("-" * 85)
                
                currency_summary = {}
                
                for report in foreign_currency_reports:
                    report_id = report.get('report_id', report.get('ID', ''))
                    name = report.get('name', report.get('ReportName', 'Unnamed'))
                    report_curr = report.get('report_currency', report.get('CurrencyCode', 'USD'))
                    foreign_currencies = report.get('foreign_currencies', [])
                    
                    print(f"{report_id:<25} "
                          f"{name[:28]:<30} "
                          f"{report_curr:<10} "
                          f"{', '.join(foreign_currencies):<15}")
                    
                    # Track currency summary
                    for curr in foreign_currencies:
                        if curr not in currency_summary:
                            currency_summary[curr] = 0
                        currency_summary[curr] += 1
                
                if currency_summary:
                    print("\nForeign Currency Summary:")
                    print(f"{'Currency':<10} {'Report Count':<15}")
                    print("-" * 30)
                    for currency, count in sorted(currency_summary.items()):
                        print(f"{currency:<10} {count:<15}")
            else:
                print("\n⚠ No reports with foreign currency found")
                print("Note: This may indicate:")
                print("  - All reports are in base currency (USD)")
                print("  - No international travel expenses")
                print("  - Need to create test data with foreign currency")
            
            test_result["passed"] = True
            test_result["response"] = {
                "foreign_currency_count": count,
                "reports": foreign_currency_reports[:10]  # Limit to first 10 for results
            }
            test_result["error"] = None
            
        except Exception as e:
            print(f"\n✗ Test failed: {str(e)}")
            test_result["passed"] = False
            test_result["response"] = None
            test_result["error"] = str(e)
        
        self.test_results["tests"].append(test_result)
        
    def test_024_specific_currency_reports(self):
        """Test 2: Find reports with specific currency (e.g., EUR, GBP, JPY)"""
        print("\n" + "-" * 80)
        print("Test 2: Reports with Specific Currencies")
        print("-" * 80)
        
        test_result = {
            "test_name": "Reports with specific currencies (EUR, GBP, JPY)",
            "endpoint": "/api/v3.0/expense/reports",
            "method": "GET",
            "parameters": {
                "user": "ALL",
                "limit": 100
            }
        }
        
        target_currencies = ['EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CNY']
        
        try:
            params = {
                "user": "ALL",
                "limit": 100
            }
            
            print(f"Looking for reports in currencies: {', '.join(target_currencies)}")
            response = self.sdk.get_expense_reports(params)
            
            currency_reports = {curr: [] for curr in target_currencies}
            
            for report in response.get('reports', []):
                # Check both CurrencyCode and currency_code for compatibility
                currency_code = report.get('currency_code', report.get('CurrencyCode', 'USD'))
                
                if currency_code in target_currencies:
                    report_info = {
                        'report_id': report.get('id', report.get('ID', '')),
                        'name': report.get('name', report.get('ReportName', 'Unnamed')),
                        'total': report.get('total', report.get('Total', 0)),
                        'country': report.get('country', report.get('Country', '')),
                        'submit_date': report.get('submission_date', report.get('SubmitDate', ''))
                    }
                    currency_reports[currency_code].append(report_info)
            
            total_found = sum(len(reports) for reports in currency_reports.values())
            print(f"\n✓ Found {total_found} reports in target currencies")
            
            if total_found > 0:
                print("\nBreakdown by Currency:")
                for currency, reports in currency_reports.items():
                    if reports:
                        print(f"\n{currency}: {len(reports)} report(s)")
                        for report in reports[:3]:  # Show first 3 per currency
                            print(f"  - {report['name'][:30]}: {report['total']:.2f} {currency}")
            else:
                print("\n⚠ No reports found in target currencies")
                print("Tip: Create test data with international expenses in EUR, GBP, etc.")
            
            test_result["passed"] = True
            test_result["response"] = {
                "target_currencies": target_currencies,
                "currency_breakdown": {curr: len(rpts) for curr, rpts in currency_reports.items()},
                "total_found": total_found
            }
            test_result["error"] = None
            
        except Exception as e:
            print(f"\n✗ Test failed: {str(e)}")
            test_result["passed"] = False
            test_result["response"] = None
            test_result["error"] = str(e)
        
        self.test_results["tests"].append(test_result)
    
    def test_024_foreign_currency_by_country(self):
        """Test 3: Correlate foreign currency with country"""
        print("\n" + "-" * 80)
        print("Test 3: Foreign Currency Correlation with Country")
        print("-" * 80)
        
        test_result = {
            "test_name": "Foreign currency by country",
            "endpoint": "/api/v3.0/expense/reports",
            "method": "GET",
            "parameters": {
                "user": "ALL",
                "limit": 100
            }
        }
        
        try:
            params = {
                "user": "ALL",
                "limit": 100
            }
            
            print(f"Analyzing currency usage by country...")
            response = self.sdk.get_expense_reports(params)
            
            country_currency_map = {}
            
            for report in response.get('reports', []):
                country = report.get('country', report.get('Country', 'Unknown'))
                currency = report.get('currency_code', report.get('CurrencyCode', 'USD'))
                
                # Skip USD as it's the base currency
                if currency != 'USD':
                    if country not in country_currency_map:
                        country_currency_map[country] = {}
                    if currency not in country_currency_map[country]:
                        country_currency_map[country][currency] = 0
                    country_currency_map[country][currency] += 1
            
            if country_currency_map:
                print(f"\n✓ Found foreign currency in {len(country_currency_map)} countries")
                print("\nCurrency Usage by Country:")
                print(f"{'Country':<20} {'Currency':<10} {'Report Count':<15}")
                print("-" * 50)
                
                for country in sorted(country_currency_map.keys()):
                    for currency, count in sorted(country_currency_map[country].items()):
                        print(f"{country:<20} {currency:<10} {count:<15}")
            else:
                print("\n⚠ No foreign currency reports found")
                print("All reports appear to be in base currency (USD)")
            
            test_result["passed"] = True
            test_result["response"] = {
                "country_currency_map": country_currency_map,
                "countries_with_foreign_currency": len(country_currency_map)
            }
            test_result["error"] = None
            
        except Exception as e:
            print(f"\n✗ Test failed: {str(e)}")
            test_result["passed"] = False
            test_result["response"] = None
            test_result["error"] = str(e)
        
        self.test_results["tests"].append(test_result)
    
    def test_024_verify_currency_conversion(self):
        """Test 4: Check for currency conversion details"""
        print("\n" + "-" * 80)
        print("Test 4: Currency Conversion Verification")
        print("-" * 80)
        
        test_result = {
            "test_name": "Currency conversion verification",
            "endpoint": "/api/v3.0/expense/reports",
            "method": "GET",
            "parameters": {
                "user": "ALL",
                "limit": 50
            }
        }
        
        try:
            params = {
                "user": "ALL",
                "limit": 50
            }
            
            print(f"Checking reports for currency conversion details...")
            response = self.sdk.get_expense_reports(params)
            
            reports_with_conversion = []
            
            for report in response.get('reports', []):
                currency = report.get('currency_code', report.get('CurrencyCode', 'USD'))
                
                # Check if there are conversion-related fields
                if currency != 'USD':
                    report_info = {
                        'report_id': report.get('id', report.get('ID', '')),
                        'name': report.get('name', report.get('ReportName', 'Unnamed')),
                        'currency': currency,
                        'total': report.get('total', report.get('Total', 0)),
                        'country': report.get('country', report.get('Country', '')),
                        # Some APIs include exchange rate info
                        'has_conversion_info': bool(report.get('ExchangeRate') or report.get('ConvertedTotal'))
                    }
                    reports_with_conversion.append(report_info)
            
            print(f"\n✓ Found {len(reports_with_conversion)} foreign currency reports")
            
            if reports_with_conversion:
                print("\nForeign Currency Reports (first 5):")
                for i, report in enumerate(reports_with_conversion[:5], 1):
                    print(f"\n{i}. {report['name']}")
                    print(f"   Currency: {report['currency']}")
                    print(f"   Total: {report['total']:.2f} {report['currency']}")
                    print(f"   Country: {report['country']}")
                    print(f"   Has Conversion Info: {'Yes' if report['has_conversion_info'] else 'No'}")
                
                print("\n💡 Note: To get detailed expense-level currency conversion:")
                print("   Use GET /api/v3.0/expense/entries for the report")
                print("   Each entry may have TransactionAmount vs ApprovedAmount in different currencies")
            else:
                print("\n⚠ No foreign currency reports found for conversion analysis")
            
            test_result["passed"] = True
            test_result["response"] = {
                "foreign_currency_reports": len(reports_with_conversion),
                "sample_reports": reports_with_conversion[:5]
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
        
        output_file = os.path.join(results_dir, 'test_024_results.json')
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
            self.test_024_all_foreign_currency_reports()
            self.test_024_specific_currency_reports()
            self.test_024_foreign_currency_by_country()
            self.test_024_verify_currency_conversion()
        except Exception as e:
            print(f"\n✗ Fatal error during test execution: {str(e)}")
        finally:
            self.generate_report()


if __name__ == "__main__":
    test_suite = TestReportsWithForeignCurrency()
    test_suite.run_all_tests()

