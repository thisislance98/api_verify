# Concur API Test Suite

This test suite verifies all 500+ API endpoints from the CSV file against real Concur environments.

## Structure

```
tests/
├── config/
│   ├── test_accounts.json      # Test account credentials for all environments
│   ├── config_loader.py        # Configuration loader utility
│   └── __init__.py
├── api_tests/
│   ├── test_001_manager_reports_to_approve.py
│   ├── test_002_overdue_reports_for_approval.py
│   ├── test_003_reports_sent_back.py
│   ├── test_005_reports_being_processed_for_payment.py
│   ├── results/
│   │   ├── test_001_results.json
│   │   ├── test_002_results.json
│   │   ├── test_003_results.json
│   │   └── test_005_results.json
│   └── __init__.py
└── README.md
```

## Configuration

Test credentials are stored in `config/test_accounts.json` with support for multiple environments:

### Available Environments

1. **integration** - Integration Environment (default)
2. **us2** - US2 Data Center
3. **eu2** - EU2 Data Center
4. **apj1** - APJ1 Data Center
5. **uspscc** - USPSCC Government Cloud

### Available Account Roles

Each environment has different test accounts with various roles:

- **manager_approver** - Manager who can approve reports (default)
- **expense_user** - Regular expense user
- **delegate_user** - Delegate user
- **administrator** - Admin account
- And more environment-specific accounts

## Usage

### Viewing Available Configurations

```bash
cd tests/config
python config_loader.py
```

This will display all available environments and accounts.

### Using Credentials in Tests

```python
from tests.config import get_test_credentials
from concur_expense_sdk import ConcurExpenseSDK, ConcurConfig

# Get credentials (uses default: manager_approver in integration)
creds = get_test_credentials()

# Or specify environment and role
creds = get_test_credentials('expense_user', 'us2')

# Initialize SDK
config = ConcurConfig(
    client_id=creds['client_id'],
    client_secret=creds['client_secret'],
    username=creds['username'],
    password=creds['password'],
    base_url=creds['base_url'],
    token_url=creds['token_url']
)

sdk = ConcurExpenseSDK(config)
```

### Running Tests

Run a specific test:

```bash
python tests/api_tests/test_001_manager_reports_to_approve.py
```

Run all tests:

```bash
# TODO: Add test runner script
```

## Test Data Preparation

**Important**: When running tests, if there is no test data available for the scenario you're testing, you should create it first.

For example:
- If testing "reports to approve", ensure there are submitted reports waiting for approval
- If testing "overdue reports", create reports and let them become overdue
- If testing "reports sent back", create and submit a report, then send it back as a manager
- If testing "pending reimbursements", ensure approved reports exist that need extraction

Each test file may include helper methods to create the necessary test data. Check the test file's `setup()` or data creation methods before running the test suite.

### Test Pass Criteria

**A test should NOT be considered a pass unless:**
- ✅ It tests against actual data (not empty responses)
- ✅ The results are perfect (all assertions pass, data structure is correct)
- ✅ The API response contains the expected data matching the test scenario

Tests that pass with empty results or without verifying actual data are considered invalid and should be re-run with proper test data.

### Tracking Test Progress

**When creating, updating, or fixing tests, update `TEST_VALIDATION_REPORT.md` as you go:**

- Add new tests to the "Recent Updates" section with date and description
- Update test counts in the summary tables (✅ VALID, ❌ INVALID, ⚠️ PARTIAL)
- Document any issues, limitations, or manual steps required
- Update statistics and compliance rate
- Mark action items as complete when resolved

This ensures the validation report stays current and provides accurate tracking of test suite health.

## Test Case Format

Each test file follows this structure:

```python
#!/usr/bin/env python3
"""
Test Case #XXX: Test Name
User Query: <Natural language query>
Service: <Service Category>
API: <HTTP Method> <Endpoint Path>

Description of what is being tested.
"""

from tests.config import get_test_credentials
from concur_expense_sdk import ConcurExpenseSDK, ConcurConfig

class TestClassName:
    def setup(self):
        """Initialize SDK with test credentials"""
        creds = get_test_credentials('manager_approver', 'integration')
        # ... initialize SDK
    
    def test_1_scenario_one(self):
        """Test specific scenario"""
        # ... test logic
    
    def test_2_scenario_two(self):
        """Test another scenario"""
        # ... test logic
    
    def generate_report(self):
        """Generate test results JSON"""
        # ... save results
    
    def run_all_tests(self):
        """Execute all tests"""
        # ... run test suite

if __name__ == "__main__":
    test_suite = TestClassName()
    test_suite.run_all_tests()
```

## Test Results

Test results are saved in JSON format under `api_tests/results/`:

```json
{
  "test_case": "001",
  "user_query": "Can I see all expense reports I need to approve this week?",
  "api_endpoint": "GET /expensereports/v4/users/{userId}/context/MANAGER/reportsToApprove",
  "service": "Expense Reports & Status",
  "tests": [
    {
      "test_name": "Basic retrieval without filters",
      "endpoint": "/expensereports/v4/users/{userId}/context/MANAGER/reportsToApprove",
      "method": "GET",
      "passed": true,
      "response": {...},
      "error": null
    }
  ],
  "summary": {
    "total": 3,
    "passed": 3,
    "failed": 0,
    "success_rate": "100.0%",
    "timestamp": "2025-11-06T10:01:19.645374"
  }
}
```

## Adding New Test Accounts

To add a new test account to `config/test_accounts.json`:

```json
{
  "environments": {
    "integration": {
      "accounts": {
        "new_account_role": {
          "username": "user@example.com",
          "password": "password123",
          "role": "Role Description",
          "note": "Optional note about this account"
        }
      }
    }
  }
}
```

## Test Coverage

This suite aims to verify all 500+ API scenarios from `concur_api_500_rows.csv`:

- ✅ Test #001: Manager Reports to Approve
- ✅ Test #002: Overdue Reports for Approval  
- ✅ Test #003: Reports Sent Back to Employees
- ✅ Test #005: Reports Being Processed for Payment
- ✅ Test #007: Reports in Exception Review
- ✅ Test #008: Pending Reports by Employee
- ✅ Test #009: Pending Reimbursements Total
- ✅ Test #010: Approved But Not Extracted Reports
- ✅ Test #011: My Reports Submitted in Last Quarter
- ✅ Test #012: Expense Reports Over $5000
- ✅ Test #013: Reports Waiting for Finance Review
- ✅ Test #014: Reports Filtered by Cost Center
- ✅ Test #015: Reports Paid via ACH Last Month
- ✅ Test #016: Average Approval Time for Reports This Quarter
- ✅ Test #018: Reports with Policy Exceptions
- ✅ Test #019: Reports Eligible for Early Payment
- ✅ Test #020: Expense Reports with Missing Manager Approval
- ✅ Test #021: Reports Approved Yesterday
- ✅ Test #022: Reports from Employees in Specific Location
- ✅ Test #023: Reports Open for More Than 30 Days
- ✅ Test #024: Reports with Foreign Currency Expenses
- ✅ Test #024: Reports Pending Processor Approval
- ✅ Test #025: Reimbursement History for Past Year
- ✅ Test #026: Reports That Exceed Approval Threshold
- ✅ Test #029: Reports Created from Travel Requests
- ✅ Test #030: Reports with Specific Report Names
- ✅ Test #031: Reports with Comments from Approvers
- ✅ Test #033: Payment Method for Approved Reports
- ✅ Test #034: Reports Where I'm Listed as a Delegate
- ✅ Test #035: Reports Needing Receipts Before Approval
- ✅ Test #036: Reports with Corporate Card Expenses
- ✅ Test #038: Workflow History of Expense Report
- ⏳ Tests #004, #006, #017, #027-028, #032, #037, #039-500: In Progress

## Environment Variables (Not Used)

This test suite does NOT use `.env` files. All configuration is in `config/test_accounts.json`.

## Security Note

The `test_accounts.json` file contains test credentials for non-production environments. These accounts should be:

- ✅ Used only for testing
- ✅ Isolated in sandbox/test environments
- ✅ Regularly rotated
- ❌ Never used in production
- ❌ Never committed with production credentials

