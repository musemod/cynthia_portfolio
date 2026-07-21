#!/usr/bin/env bash

# run this script on VPS (virtual private server, not locally)
# if the git commands or docker build fail, the script stops instead of continuing to a broken deploy
set -e

PROJECT_DIR=/root/cynthia_portfolio/

echo "1: Moving into project folder..."
cd "$PROJECT_DIR"

echo "2: Pulling latest code from GitHub..."
git fetch && git reset origin/main --hard

echo "3: spin Docker containers down first"
 docker compose -f docker-compose.prod.yml down

echo "4: Rebuilding image (if code changed) and starting container..."
docker compose -f docker-compose.prod.yml up -d --build

echo "Done! Site should be live."


# older comments / commands below, prior to containerization

# NOTE: if edited myportfolio.service, run `systemctl daemon-reload` manually before this script 

# VENV_DIR=/root/cynthia_portfolio/python3-virtualenv 

# absolute paths
# no need for end slash ‘/’ since ‘/’ already in activate env path, step 4

# "|| true" prevents script from stopping if there was no tmux session to kill
# echo "1: Killing existing flask_server tmux session..."

# tmux kill-session -t flask_server 2>/dev/null || true

# echo "4: Activating virtualenv and installing dependencies..."
# source "$VENV_DIR/bin/activate"
# pip install -r requirements.txt

# echo "5: Restarting myportfolio service"
# systemctl restart myportfolio

# echo "6: Showing my portfolio status"
# systemctl status myportfolio

# # tmux session is named flask_server so can be referenced later

# echo "5: Starting new detached tmux session with Flask server..."

# tmux new-session -d -s flask_server bash -c "cd '$PROJECT_DIR' && source '$VENV_DIR/bin/activate' && flask run --host=0.0.0.0"
