#!/bin/env bash
# run this script on VPS (virtual private server, not locally)
# if pip install fails, or the git commands fail, the script stops instead of continuing on to start a broken server
set -e

PROJECT_DIR=/root/cynthia_portfolio/
VENV_DIR=/root/cynthia_portfolio/python3-virtualenv 
# absolute paths
# no need for end slash ‘/’ since ‘/’ already in activate env path, step 4

# "|| true" prevents script from stopping if there was no tmux session to kill
echo "1: Killing existing flask_server tmux session..."
tmux kill-session -t flask_server 2>/dev/null || true

echo "2: Moving into project folder..."
cd "$PROJECT_DIR"

echo "3: Pulling latest code from GitHub..."
git fetch && git reset origin/main --hard

echo "4: Activating virtualenv and installing dependencies..."
source "$VENV_DIR/bin/activate"
pip install -r requirements.txt

# tmux session is named flask_server so can be referenced later
echo "5: Starting new detached tmux session with Flask server..."
tmux new-session -d -s flask_server bash -c "cd '$PROJECT_DIR' && source '$VENV_DIR/bin/activate' && flask run --host=0.0.0.0"

# decided not to include live site URL here since still in progress
echo "Done! Site should be live."
