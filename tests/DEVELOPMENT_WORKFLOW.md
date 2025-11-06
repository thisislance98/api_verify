# Development Workflow: CSV to Tests

This document outlines the workflow for creating tests from the CSV file and extending the SDK.

## Workflow Pattern

For each row in `concur_api_500_rows.csv`, follow this pattern:

### 1. Add SDK Method

First, add a method to `concur_expense_sdk.py`:

```python
def method_name(self, parameters) -> Dict[str, Any]:
    """
    Brief description of what this method does.
    
    CSV Row #X: User query from CSV
    
    Args:
        param1: Description
        param2: Description
    
    Returns:
        Dictionary with results and metadata
    """
    # Implementation
    endpoint = "api/path/from/csv"
    params = {...}  # From API Request Payload column
    
    response = self._make_request("GET/POST/etc", endpoint, params=params)
    data = response.json()
    
    # Process and return standardized format
    return {
        'success': True,
        'data': processed_data,
        'count': len(items),
        'message': 'Success message'
    }
```

**Key Points:**
- ✅ Reference CSV row number in docstring
- ✅ Include user query from CSV
- ✅ Use consistent return format with `success`, `message`, `count`
- ✅ Handle both success and error cases
- ✅ Process API response into consistent format

### 2. Create Test File

Create `tests/api_tests/test_XXX_descriptive_name.py`:

```python
#!/usr/bin/env python3
"""
Test Case #XXX: Test Name from CSV
User Query: <User Utterance from CSV>
Service: <Service from CSV>
API: <API Request Type> <API Request URL>

Description of what is being tested.
"""

from tests.config import get_test_credentials
from concur_expense_sdk import ConcurExpenseSDK, ConcurConfig
import json
from datetime import datetime

class TestClassName:
    def __init__(self):
        self.sdk = None
        self.results = {
            'test_case': 'XXX',
            'user_query': '...',
            'api_endpoint': '...',
            'service': '...',
            'tests': [],
            'summary': {}
        }
    
    def setup(self):
        """Initialize SDK with test credentials"""
        creds = get_test_credentials('manager_approver', 'integration')
        config = ConcurConfig(**{...})
        self.sdk = ConcurExpenseSDK(config)
        # Authenticate and verify
    
    def test_1_basic_scenario(self):
        """Test basic functionality"""
        result = self.sdk.new_method()
        # Verify and record results
    
    def test_2_edge_cases(self):
        """Test edge cases and filters"""
        # Test variations
    
    def test_3_response_validation(self):
        """Validate response structure"""
        # Verify response fields
    
    def generate_report(self):
        """Generate JSON test report"""
        # Save to results/test_XXX_results.json
    
    def run_all_tests(self):
        """Execute all tests"""
        self.setup()
        self.test_1_basic_scenario()
        # ... other tests
        return self.generate_report()

if __name__ == "__main__":
    test_suite = TestClassName()
    test_suite.run_all_tests()
```

### 3. Run and Verify

```bash
python tests/api_tests/test_XXX_descriptive_name.py
```

Verify:
- ✅ All tests pass
- ✅ Results JSON is generated
- ✅ Response structure is validated
- ✅ Edge cases are covered

## Examples

### Example 1: Test #001 - Manager Reports to Approve

**CSV Row:**
```
Can I see all expense reports I need to approve this week?,
Expense Reports & Status,
GET,
/expensereports/v4/users/{userId}/context/MANAGER/reportsToApprove,
approvalStatus filter
```

**SDK Method:**
```python
def get_reports_to_approve(self, user: Optional[str] = None, 
                          approval_status: Optional[str] = None) -> Dict[str, Any]:
    """
    CSV Row #1: Can I see all expense reports I need to approve this week?
    """
    # Implementation...
```

**Result:** ✅ 100% Pass (3/3 tests)

### Example 2: Test #002 - Overdue Reports for Approval

**CSV Row:**
```
Which expense reports are overdue for approval?,
Expense Reports & Status,
GET,
/api/v3.0/expense/reports,
approvalStatusCode=A_PEND&submitDateBefore={7daysAgo}
```

**SDK Method:**
```python
def get_overdue_reports_for_approval(self, days_overdue: int = 7,
                                    approval_status_code: str = "A_PEND",
                                    limit: int = 50) -> Dict[str, Any]:
    """
    CSV Row #2: Which expense reports are overdue for approval?
    """
    # Implementation...
```

**Result:** ✅ 100% Pass (4/4 tests)

## Test Naming Convention

- **File:** `test_XXX_descriptive_name.py` where XXX is the row number (e.g., `test_001_manager_reports_to_approve.py`)
- **Class:** `TestDescriptiveName` in PascalCase
- **Methods:** `test_N_scenario_description` where N is sequential

## SDK Method Naming Convention

Choose clear, descriptive names that reflect the action:

- ✅ **Good:** `get_overdue_reports_for_approval()`, `list_reports_by_status()`, `create_expense_report()`
- ❌ **Bad:** `get_reports()`, `do_thing()`, `api_call()`

## Response Format Standard

All SDK methods should return a dictionary with:

```python
{
    'success': bool,          # True if request succeeded
    'data': ...,             # Main data payload (optional, use specific keys)
    'count': int,            # Number of items returned (if applicable)
    'message': str,          # Human-readable message
    'error': str or None,    # Error message if failed
    # Additional context-specific fields...
}
```

## Progress Tracking

| Test # | CSV Row | User Query | Status | Pass Rate |
|--------|---------|------------|--------|-----------|
| 001 | 2 | Can I see all expense reports I need to approve this week? | ✅ Done | 100% (3/3) |
| 002 | 3 | Which expense reports are overdue for approval? | ✅ Done | 100% (4/4) |
| 003 | 4 | Show me expense reports that were sent back to employees | ⏳ Next | - |
| ... | ... | ... | ⏳ Pending | - |

## Benefits of This Approach

1. **SDK grows organically** - Each test adds real functionality
2. **Tests stay clean** - Business logic in SDK, tests focus on verification
3. **Reusability** - SDK methods can be used in multiple tests
4. **Documentation** - CSV row references provide traceability
5. **Consistency** - Standardized patterns across all tests
6. **Maintainability** - Changes to APIs only require SDK updates

## Quick Reference

```bash
# View available test accounts
python tests/config/config_loader.py

# Run specific test
python tests/api_tests/test_XXX_name.py

# View test results
cat tests/api_tests/results/test_XXX_results.json | python -m json.tool

# Check SDK methods
grep -n "CSV Row" concur_expense_sdk.py
```

## Next Test: #003

**CSV Row 4:**
```
Show me expense reports that were sent back to employees,
Expense Reports & Status,
GET,
/api/v3.0/expense/reports,
approvalStatusCode=A_RESU
```

**SDK Method to Add:**
```python
def get_sent_back_reports(self, limit: int = 50) -> Dict[str, Any]:
    """
    CSV Row #3: Show me expense reports that were sent back to employees
    """
```

Ready to implement!

