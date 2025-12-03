#!/bin/bash
# Construction Check Dashboard Launcher
# Runs the dashboard in a background tmux session

SESSION_NAME="ccheck-dashboard"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "============================================================"
echo "Construction Check - Unified Dashboard"
echo "============================================================"
echo ""

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo "❌ Error: tmux is not installed"
    echo "Install with: sudo apt install tmux"
    exit 1
fi

# Check if session already exists
if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "⚠️  Dashboard is already running in tmux session: $SESSION_NAME"
    echo ""
    echo "Options:"
    echo "  - View logs: tmux attach -t $SESSION_NAME"
    echo "  - Stop dashboard: ./stop_dashboard.sh"
    exit 1
fi

echo "🚀 Starting dashboard in background tmux session..."

# Create new tmux session and run dashboard
tmux new-session -d -s "$SESSION_NAME" "cd '$SCRIPT_DIR/dashboards' && python3 unified_dashboard.py"

# Give it a moment to start
sleep 2

# Check if it's running
if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "✅ Dashboard started successfully!"
    echo ""
    echo "📊 Open your browser to: http://127.0.0.1:8050"
    echo ""
    echo "Commands:"
    echo "  - View dashboard logs: tmux attach -t $SESSION_NAME"
    echo "  - Stop dashboard: ./stop_dashboard.sh"
    echo "  - (In tmux, detach with: Ctrl+B then D)"
else
    echo "❌ Error: Failed to start dashboard"
    exit 1
fi

echo "============================================================"
