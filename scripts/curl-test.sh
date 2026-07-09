#!/usr/bin/env bash
# Tests the /api/timeline_post endpoints (POST, GET, DELETE) against a locally
# running Flask dev server. Creates a random test post, confirms it shows up
# via GET, then deletes it so test data doesn't pile up in the shared database.

set -e  # exit immediately if any command fails, so we don't silently continue on a broken request

# script should run from wherever invoked
# resolves directory this script lives in, then go up 1 level to repo root
# BASH_SOURCE is a built-in bash array variable that bash maintains automatically for every running script, similar to how $1, $2, $@, or $0 are already populated before script even starts. 
# BASH_SOURCE is an array tracking the source filename at each level of the call stack:
    # BASH_SOURCE[0] = the file currently executing (the innermost/current one)
    # BASH_SOURCE[1] = the file that sourced or called that file, if any and so on up the chain
# Piping through cd + pwd forces it into a full absolute path

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$(cd "$SCRIPT_DIR/.." && pwd)/.env"

set -a    # auto-export every var defined while sourcing
source "$ENV_FILE"
set +a    # set +a turns off the "allexport" feature, meaning that newly created or modified variables will no longer be automatically exported to child processes

# :? gives a clear error if the var is missing, instead of curl silently hitting an empty URL
BASE_URL="${TEST_BASE_URL:?TEST_BASE_URL not set in .env}"

# Generate a random suffix so repeated runs don't collide on identical content, so we can visually confirm THIS run's post
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

# Pull the created post's id out of the JSON response using python's json module (avoids depending on jq being installed)
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