#!/bin/bash
# Construction Check Dashboard Stopper
# Stops the background tmux dashboard session

SESSION_NAME="ccheck-dashboard"

echo "============================================================"
echo "Construction Check - Dashboard Stopper"
echo "============================================================"
echo ""

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo "❌ Error: tmux is not installed"
    exit 1
fi

# Check if session exists
if ! tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "⚠️  Dashboard is not running (no tmux session found)"
    exit 1
fi

echo "🛑 Stopping dashboard..."

# Kill the tmux session
tmux kill-session -t "$SESSION_NAME"

# Verify it's stopped
sleep 1
if ! tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "✅ Dashboard stopped successfully!"
else
    echo "❌ Error: Failed to stop dashboard"
    exit 1
fi

echo "============================================================"
