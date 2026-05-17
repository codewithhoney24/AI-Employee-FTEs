#!/bin/bash
# Script to stop the Playwright MCP server

echo "Stopping Playwright MCP server..."
# Find and kill the process running on port 8808
fuser -k 8808/tcp
echo "Playwright MCP server stopped."