#!/usr/bin/env python3
"""
Test the first endpoint from the CSV
"""
import requests
from dotenv import load_dotenv
from concur_expense_sdk import ConcurExpenseSDK

# Load .env file
load_dotenv()

# Initialize SDK
sdk = ConcurExpenseSDK()

# Get the access token
token = sdk._get_access_token()
print(f"✓ Token obtained: {token[:50]}...")

# Get user ID
user_id = sdk.get_user_id()
print(f"✓ User ID: {user_id}")

# Test the endpoint from CSV Row 1
print("\n" + "="*60)
print("Testing CSV Row 1")
print("="*60)
print("User Utterance: Can I see all expense reports I need to approve this week?")
print("Endpoint: GET /expensereports/v4/users/{userId}/context/MANAGER/reportsToApprove")
print("")

# Make the request
url = f"https://integration.api.concursolutions.com/expensereports/v4/users/{user_id}/context/MANAGER/reportsToApprove"
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json"
}

response = requests.get(url, headers=headers)

print(f"HTTP Status: {response.status_code}")
print(f"\nResponse:")
print("-" * 60)

if response.status_code == 200:
    try:
        data = response.json()
        print(f"✓ Success! Received JSON response")
        print(f"\nResponse structure:")
        if isinstance(data, dict):
            for key in data.keys():
                print(f"  - {key}: {type(data[key]).__name__}")
        print(f"\nFull response:")
        import json
        print(json.dumps(data, indent=2))
        
        # Analyze if it answers the question
        print("\n" + "="*60)
        print("Analysis: Does this endpoint answer the question?")
        print("="*60)
        if 'reports' in data or 'data' in data or isinstance(data, list):
            print("✓ YES - This endpoint returns reports that need approval")
        else:
            print("? UNCLEAR - Response structure doesn't clearly show reports")
            
    except Exception as e:
        print(f"✗ Error parsing JSON: {e}")
        print(f"Raw response: {response.text[:500]}")
else:
    print(f"✗ Error: {response.status_code}")
    print(f"Response: {response.text[:500]}")

