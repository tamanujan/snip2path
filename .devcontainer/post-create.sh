#!/usr/bin/env bash

set -e

echo "🔧 Fix CRLF (Windows対策)..."
sed -i 's/\r$//' "$0" || true

echo "🔧 Installing jq..."
sudo apt-get update
sudo apt-get install -y jq

echo "🤖 Installing Claude Code..."
if curl -fsSL https://claude.ai/install.sh -o install-claude.sh; then
  bash install-claude.sh || echo "⚠ install script failed"
else
  echo "⚠ download failed"
fi

echo "✅ Done"