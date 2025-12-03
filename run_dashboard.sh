#!/bin/bash
# Construction Check Dashboard Launcher
# Run this script from the project root directory

echo "============================================================"
echo "Construction Check - Unified Dashboard"
echo "============================================================"
echo ""
echo "Starting dashboard server..."
echo "Open your browser to: http://127.0.0.1:8050"
echo ""
echo "Press Ctrl+C to stop the server"
echo "============================================================"
echo ""

# Change to dashboards directory and run the unified dashboard
cd "$(dirname "$0")/dashboards" && python3 unified_dashboard.py
