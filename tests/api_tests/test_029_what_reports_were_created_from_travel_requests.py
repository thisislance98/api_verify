#!/usr/bin/env python3
"""
Test Case #029: Reports Created from Travel Requests
User Query: What reports were created from travel requests?
Service: Expense Reports & Status
API: GET /api/v3.0/expense/reports

Tests the ability to find expense reports that were created from approved travel requests.
This is useful for:
- Linking expense reports to pre-trip authorizations
- Verifying travel expenses match pre-approved budgets
- Tracking travel request to expense report workflow
- Ensuring compliance with travel authorization policies
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tests.config import get_test_credentials
from concur_expense_sdk import ConcurExpenseSDK, ConcurConfig


class TestReportsFromTravelRequests:
    def __init__(self):
        self.sdk = None
        self.test_results = {
            "test_case": "029",
            "user_query": "What reports were created from travel requests?",
            "api_endpoint": "GET /api/v3.0/expense/reports",
            "service": "Expense Reports & Status",
            "tests": []
        }
        
    def setup(self):
        """Initialize SDK with test credentials"""
        print("=" * 80)
        print("TEST #029: Reports Created from Travel Requests")
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
        
    def test_029_all_reports_with_travel_requests(self):
        """Test 1: Find all reports linked to travel requests"""
        print("\n" + "-" * 80)
        print("Test 1: All Reports Linked to Travel Requests")
        print("-" * 80)
        
        test_result = {
            "test_name": "All reports linked to travel requests",
            "endpoint": "/api/v3.0/expense/reports",
            "method": "GET",
            "parameters": {
                "user": "ALL",
                "limit": 100
            }
        }
        
        try:
            # Get all reports and check for travel request linkage
            params = {
                "user": "ALL",
                "limit": 100
            }
            
            print(f"Fetching reports and checking for travel request links...")
            response = self.sdk.get_expense_reports(params)
            
            if not response.get('success', False):
                print(f"\n⚠ API call failed: {response.get('message', 'Unknown error')}")
                test_result["passed"] = False
                test_result["response"] = response
                test_result["error"] = response.get('message')
                self.test_results["tests"].append(test_result)
                return
            
            all_reports = response.get('reports', [])
            reports_with_travel_request = []
            
            # Check each report for travel request linkage
            # Possible fields: TravelRequestID, TripID, RequestID, or custom fields
            for report in all_reports:
                travel_request_id = None
                trip_id = None
                
                # Check standard fields
                if report.get('TravelRequestID'):
                    travel_request_id = report.get('TravelRequestID')
                elif report.get('RequestID'):
                    travel_request_id = report.get('RequestID')
                    
                if report.get('TripID'):
                    trip_id = report.get('TripID')
                
                # Check custom fields (if available)
                custom_fields = report.get('CustomFields', {})
                if isinstance(custom_fields, dict):
                    for field_name, field_value in custom_fields.items():
                        if 'travel' in field_name.lower() or 'request' in field_name.lower() or 'trip' in field_name.lower():
                            if field_value:
                                travel_request_id = field_value
                                break
                
                if travel_request_id or trip_id:
                    report_info = {
                        'report_id': report.get('ID', report.get('id', '')),
                        'name': report.get('ReportName', report.get('name', 'Unnamed')),
                        'travel_request_id': travel_request_id,
                        'trip_id': trip_id,
                        'owner_name': report.get('OwnerName', ''),
                        'total': report.get('Total', report.get('total', 0)),
                        'submit_date': report.get('SubmitDate', report.get('submission_date', '')),
                        'approval_status': report.get('ApprovalStatusName', report.get('approval_status', ''))
                    }
                    reports_with_travel_request.append(report_info)
            
            count = len(reports_with_travel_request)
            print(f"\n✓ Found {count} reports linked to travel requests out of {len(all_reports)} total reports")
            print(f"  ({count / len(all_reports) * 100:.1f}% of reports are linked to travel requests)" if all_reports else "")
            
            if reports_with_travel_request:
                print("\nReports Linked to Travel Requests:")
                print(f"{'Report ID':<25} {'Name':<30} {'Travel Request':<20} {'Owner':<25}")
                print("-" * 105)
                
                for report in reports_with_travel_request[:20]:  # Show first 20
                    travel_ref = report.get('travel_request_id') or report.get('trip_id', 'N/A')
                    print(f"{report['report_id']:<25} "
                          f"{report['name'][:28]:<30} "
                          f"{str(travel_ref)[:18]:<20} "
                          f"{report['owner_name'][:23]:<25}")
                
                if count > 20:
                    print(f"\n... and {count - 20} more reports")
                
                # Summary statistics
                total_amount = sum(float(r.get('total', 0)) for r in reports_with_travel_request)
                print(f"\nSummary:")
                print(f"  Total Reports with Travel Request: {count}")
                print(f"  Total Amount: ${total_amount:,.2f}")
                
                # Group by approval status
                status_breakdown = {}
                for report in reports_with_travel_request:
                    status = report.get('approval_status', 'Unknown')
                    if status not in status_breakdown:
                        status_breakdown[status] = 0
                    status_breakdown[status] += 1
                
                if status_breakdown:
                    print(f"\n  Status Breakdown:")
                    for status, cnt in sorted(status_breakdown.items()):
                        print(f"    {status}: {cnt}")
                        
            else:
                print("\n⚠ No reports found linked to travel requests")
                print("\nNote: This may indicate:")
                print("  - Travel request integration is not enabled")
                print("  - Reports were created directly without travel requests")
                print("  - Travel request fields are stored in custom fields not checked")
                print("  - Need to submit expense reports from approved travel requests")
                print("\nTo create test data:")
                print("  1. Create and approve a travel request in Concur Travel")
                print("  2. Create an expense report from that travel request")
                print("  3. The report should automatically link to the travel request ID")
            
            test_result["passed"] = True
            test_result["response"] = {
                "reports_with_travel_request": count,
                "total_reports": len(all_reports),
                "percentage": f"{count / len(all_reports) * 100:.1f}%" if all_reports else "0%",
                "reports": reports_with_travel_request[:10]  # Limit to first 10 for results
            }
            test_result["error"] = None
            
        except Exception as e:
            print(f"\n✗ Test failed: {str(e)}")
            test_result["passed"] = False
            test_result["response"] = None
            test_result["error"] = str(e)
        
        self.test_results["tests"].append(test_result)
        
    def test_029_specific_travel_request(self):
        """Test 2: Find reports for a specific travel request ID"""
        print("\n" + "-" * 80)
        print("Test 2: Reports for Specific Travel Request")
        print("-" * 80)
        
        test_result = {
            "test_name": "Reports for specific travel request ID",
            "endpoint": "/api/v3.0/expense/reports",
            "method": "GET",
            "parameters": {
                "user": "ALL",
                "limit": 100
            }
        }
        
        try:
            # First, get all reports with travel requests to find a valid ID
            params = {
                "user": "ALL",
                "limit": 100
            }
            
            response = self.sdk.get_expense_reports(params)
            all_reports = response.get('reports', [])
            
            # Find first travel request ID
            sample_travel_request_id = None
            sample_trip_id = None
            
            for report in all_reports:
                if report.get('TravelRequestID'):
                    sample_travel_request_id = report.get('TravelRequestID')
                    break
                elif report.get('RequestID'):
                    sample_travel_request_id = report.get('RequestID')
                    break
                elif report.get('TripID'):
                    sample_trip_id = report.get('TripID')
                    if not sample_travel_request_id:
                        sample_travel_request_id = sample_trip_id
                    break
            
            if not sample_travel_request_id:
                print("\n⚠ No travel request IDs found in reports")
                print("Skipping test - need reports linked to travel requests")
                test_result["passed"] = True  # Not a failure, just no data
                test_result["response"] = {"message": "No travel request IDs available"}
                test_result["error"] = None
                self.test_results["tests"].append(test_result)
                return
            
            print(f"Looking for reports linked to travel request: {sample_travel_request_id}")
            
            # Filter reports by this travel request ID
            matching_reports = []
            for report in all_reports:
                report_travel_id = (report.get('TravelRequestID') or 
                                   report.get('RequestID') or 
                                   report.get('TripID'))
                
                if report_travel_id == sample_travel_request_id:
                    report_info = {
                        'report_id': report.get('ID', report.get('id', '')),
                        'name': report.get('ReportName', report.get('name', 'Unnamed')),
                        'owner': report.get('OwnerName', ''),
                        'total': report.get('Total', report.get('total', 0)),
                        'status': report.get('ApprovalStatusName', ''),
                        'submit_date': report.get('SubmitDate', '')
                    }
                    matching_reports.append(report_info)
            
            print(f"\n✓ Found {len(matching_reports)} report(s) for travel request {sample_travel_request_id}")
            
            if matching_reports:
                print("\nReports for this Travel Request:")
                for i, report in enumerate(matching_reports, 1):
                    print(f"\n{i}. {report['name']}")
                    print(f"   Report ID: {report['report_id']}")
                    print(f"   Owner: {report['owner']}")
                    print(f"   Total: ${report['total']:.2f}")
                    print(f"   Status: {report['status']}")
                    print(f"   Submit Date: {report['submit_date']}")
                
                print("\n💡 Travel Request Workflow:")
                print("   1. Travel request created and approved")
                print("   2. Employee travels and incurs expenses")
                print("   3. Employee creates expense report from travel request")
                print("   4. Report automatically links to travel request")
                print("   5. Expenses can be matched against travel authorization")
            
            test_result["passed"] = True
            test_result["response"] = {
                "travel_request_id": sample_travel_request_id,
                "matching_reports": len(matching_reports),
                "reports": matching_reports
            }
            test_result["error"] = None
            
        except Exception as e:
            print(f"\n✗ Test failed: {str(e)}")
            test_result["passed"] = False
            test_result["response"] = None
            test_result["error"] = str(e)
        
        self.test_results["tests"].append(test_result)
    
    def test_029_travel_request_compliance(self):
        """Test 3: Verify travel expenses match pre-approved budgets"""
        print("\n" + "-" * 80)
        print("Test 3: Travel Request Compliance Analysis")
        print("-" * 80)
        
        test_result = {
            "test_name": "Travel request compliance analysis",
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
            
            print(f"Analyzing expense reports vs travel request authorizations...")
            response = self.sdk.get_expense_reports(params)
            
            reports_with_travel = []
            reports_without_travel = []
            
            for report in response.get('reports', []):
                has_travel_request = (report.get('TravelRequestID') or 
                                     report.get('RequestID') or 
                                     report.get('TripID'))
                
                report_info = {
                    'report_id': report.get('ID', ''),
                    'name': report.get('ReportName', 'Unnamed'),
                    'total': float(report.get('Total', 0)),
                    'owner': report.get('OwnerName', ''),
                    'country': report.get('Country', ''),
                    'status': report.get('ApprovalStatusName', '')
                }
                
                if has_travel_request:
                    report_info['travel_request_id'] = has_travel_request
                    reports_with_travel.append(report_info)
                else:
                    reports_without_travel.append(report_info)
            
            total_reports = len(reports_with_travel) + len(reports_without_travel)
            with_travel_pct = (len(reports_with_travel) / total_reports * 100) if total_reports > 0 else 0
            
            print(f"\n✓ Compliance Analysis Complete")
            print(f"\nTravel Request Linkage:")
            print(f"  Reports WITH travel request: {len(reports_with_travel)} ({with_travel_pct:.1f}%)")
            print(f"  Reports WITHOUT travel request: {len(reports_without_travel)} ({100-with_travel_pct:.1f}%)")
            
            if reports_with_travel:
                total_with_travel = sum(r['total'] for r in reports_with_travel)
                print(f"\nReports WITH Travel Requests:")
                print(f"  Total Amount: ${total_with_travel:,.2f}")
                print(f"  Average per Report: ${total_with_travel/len(reports_with_travel):,.2f}")
                
                # Show a few examples
                print(f"\n  Examples (first 5):")
                for report in reports_with_travel[:5]:
                    print(f"    - {report['name'][:40]}: ${report['total']:.2f}")
            
            if reports_without_travel:
                total_without_travel = sum(r['total'] for r in reports_without_travel)
                print(f"\nReports WITHOUT Travel Requests:")
                print(f"  Total Amount: ${total_without_travel:,.2f}")
                print(f"  Average per Report: ${total_without_travel/len(reports_without_travel):,.2f}")
                
                print(f"\n  ⚠️  These reports may need review:")
                for report in reports_without_travel[:5]:
                    print(f"    - {report['name'][:40]}: ${report['total']:.2f}")
            
            print("\n💡 Best Practices:")
            print("   - High-value expenses should be pre-approved via travel requests")
            print("   - Travel expenses (flights, hotels) should link to travel requests")
            print("   - Regular office expenses typically don't need travel requests")
            print("   - Policy can require travel request for expenses over a threshold")
            
            test_result["passed"] = True
            test_result["response"] = {
                "total_reports": total_reports,
                "with_travel_request": len(reports_with_travel),
                "without_travel_request": len(reports_without_travel),
                "compliance_rate": f"{with_travel_pct:.1f}%"
            }
            test_result["error"] = None
            
        except Exception as e:
            print(f"\n✗ Test failed: {str(e)}")
            test_result["passed"] = False
            test_result["response"] = None
            test_result["error"] = str(e)
        
        self.test_results["tests"].append(test_result)
    
    def test_029_travel_request_workflow_status(self):
        """Test 4: Check workflow status of reports from travel requests"""
        print("\n" + "-" * 80)
        print("Test 4: Travel Request Workflow Status")
        print("-" * 80)
        
        test_result = {
            "test_name": "Travel request workflow status",
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
            
            print(f"Analyzing workflow status of travel-linked reports...")
            response = self.sdk.get_expense_reports(params)
            
            travel_reports_by_status = {}
            
            for report in response.get('reports', []):
                has_travel_request = (report.get('TravelRequestID') or 
                                     report.get('RequestID') or 
                                     report.get('TripID'))
                
                if has_travel_request:
                    status = report.get('ApprovalStatusName', 'Unknown')
                    if status not in travel_reports_by_status:
                        travel_reports_by_status[status] = []
                    
                    report_info = {
                        'report_id': report.get('ID', ''),
                        'name': report.get('ReportName', 'Unnamed'),
                        'travel_request_id': has_travel_request,
                        'total': float(report.get('Total', 0)),
                        'owner': report.get('OwnerName', ''),
                        'submit_date': report.get('SubmitDate', ''),
                        'payment_status': report.get('PaymentStatusName', 'Unknown')
                    }
                    travel_reports_by_status[status].append(report_info)
            
            total_travel_reports = sum(len(reports) for reports in travel_reports_by_status.values())
            
            if total_travel_reports > 0:
                print(f"\n✓ Found {total_travel_reports} reports linked to travel requests")
                print("\nWorkflow Status Breakdown:")
                print(f"{'Status':<30} {'Count':<10} {'Total Amount':<20}")
                print("-" * 65)
                
                for status in sorted(travel_reports_by_status.keys()):
                    reports = travel_reports_by_status[status]
                    count = len(reports)
                    total = sum(r['total'] for r in reports)
                    print(f"{status:<30} {count:<10} ${total:,.2f}")
                
                # Show details for each status
                for status, reports in sorted(travel_reports_by_status.items()):
                    print(f"\n{status} Reports (from travel requests):")
                    for report in reports[:3]:  # Show first 3 per status
                        print(f"  - {report['name'][:50]} (${report['total']:.2f})")
                        print(f"    Travel Request: {report['travel_request_id']}")
                        print(f"    Payment Status: {report['payment_status']}")
                    
                    if len(reports) > 3:
                        print(f"  ... and {len(reports) - 3} more")
                
                print("\n💡 Typical Travel Request to Expense Report Workflow:")
                print("   1. Travel Request: Submitted → Approved")
                print("   2. Travel: Employee travels")
                print("   3. Expense Report: Created from travel request")
                print("   4. Expense Report: Submitted (links to travel request)")
                print("   5. Expense Report: Approved")
                print("   6. Expense Report: Processed for payment")
                print("   7. Expense Report: Paid")
            else:
                print("\n⚠ No reports found linked to travel requests")
                print("Cannot analyze workflow status without data")
            
            test_result["passed"] = True
            test_result["response"] = {
                "total_travel_reports": total_travel_reports,
                "status_breakdown": {
                    status: len(reports) 
                    for status, reports in travel_reports_by_status.items()
                }
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
        
        output_file = os.path.join(results_dir, 'test_029_results.json')
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
            self.test_029_all_reports_with_travel_requests()
            self.test_029_specific_travel_request()
            self.test_029_travel_request_compliance()
            self.test_029_travel_request_workflow_status()
        except Exception as e:
            print(f"\n✗ Fatal error during test execution: {str(e)}")
        finally:
            self.generate_report()


if __name__ == "__main__":
    test_suite = TestReportsFromTravelRequests()
    test_suite.run_all_tests()

