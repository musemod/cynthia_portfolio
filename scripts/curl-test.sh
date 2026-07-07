#!/bin/env bash
# Tests the /api/timeline_post endpoints (POST, GET, DELETE) against a locally
# running Flask dev server. Creates a random test post, confirms it shows up
# via GET, then deletes it so test data doesn't pile up in the shared database.

set -e  # exit immediately if any command fails, so we don't silently continue on a broken request

BASE_URL="http://localhost:5000/api/timeline_post"

# Generate a random suffix so repeated runs don't collide on identical content,
# and so we can visually confirm THIS run's post
RANDOM_ID=$RANDOM
NAME="test_user_${RANDOM_ID}"
EMAIL="test${RANDOM_ID}@example.com"
CONTENT="Automated test post #${RANDOM_ID}"

echo "== Creating test post =="
# Straight single quotes here matter — curly/smart quotes break shell parsing
POST_RESPONSE=$(curl --silent --request POST "$BASE_URL" \
  -d "name=${NAME}" \
  -d "email=${EMAIL}" \
  -d "content=${CONTENT}")

echo "POST response: $POST_RESPONSE"

# Pull the created post's id out of the JSON response using python's json module
# (avoids depending on jq being installed)
POST_ID=$(echo "$POST_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")

if [ -z "$POST_ID" ]; then
  echo "FAILED: could not extract id from POST response"
  exit 1
fi

echo "Created post with id: $POST_ID"

echo ""
echo "== Verifying post appears in GET =="
GET_RESPONSE=$(curl --silent --request GET "$BASE_URL")
echo "GET response: $GET_RESPONSE"

# Check that our specific test content shows up somewhere in the response
if echo "$GET_RESPONSE" | grep -q "$CONTENT"; then
  echo "PASS: test post found in GET response"
else
  echo "FAIL: test post NOT found in GET response"
  exit 1
fi

echo ""
echo "== Cleaning up: deleting test post $POST_ID =="
DELETE_RESPONSE=$(curl --silent --request DELETE "$BASE_URL/$POST_ID")
echo "DELETE response: $DELETE_RESPONSE"

echo ""
echo "== Confirming post was removed =="
GET_AFTER_DELETE=$(curl --silent --request GET "$BASE_URL")

if echo "$GET_AFTER_DELETE" | grep -q "$CONTENT"; then
  echo "FAIL: test post still present after DELETE"
  exit 1
else
  echo "PASS: test post successfully deleted"
fi

echo ""
echo "All tests passed."