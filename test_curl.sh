#!/bin/bash

# Test Manager Approval Endpoint via curl
# First, get an access token

echo "=== Getting Access Token ==="
TOKEN_RESPONSE=$(curl -s -X POST https://integration.api.concursolutions.com/oauth2/v0/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=486c51f1-1d22-41cf-b743-ca90fd4279d4" \
  -d "client_secret=3b615a2e-d467-40be-83c7-3e6286625813" \
  -d "grant_type=password" \
  -d "username=mgr3@p10005178e93.com" \
  -d "password=password12")

ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo "✓ Access token obtained"
echo

# Decode the JWT to get user ID
USER_ID=$(echo $ACCESS_TOKEN | cut -d'.' -f2 | base64 -d 2>/dev/null | python3 -c "import sys, json; print(json.load(sys.stdin)['concur.profile'].split('/')[-1])")
echo "✓ User ID: $USER_ID"
echo

# Test the manager approval endpoint
echo "=== Testing Manager Approval Endpoint ==="
echo "GET /expensereports/v4/users/$USER_ID/context/MANAGER/reportsToApprove"
echo

curl -X GET "https://integration.api.concursolutions.com/expensereports/v4/users/$USER_ID/context/MANAGER/reportsToApprove" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Accept: application/json" | python3 -m json.tool

echo
echo "=== Test Complete ==="

