#!/bin/bash
# Script to start the Playwright MCP server for browser automation

echo "Starting Playwright MCP server on port 8808..."
npx @playwright/mcp@latest --port 8808 --shared-browser-context &
echo "Playwright MCP server started in background."