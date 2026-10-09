#!/usr/bin/env bash
# Rebuilds demo/site/ and (with the "deploy" argument) publishes the fm1-demo Worker.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 tools/build_demo.py
if [ "${1:-}" = "deploy" ]; then
  cd demo
  CLOUDFLARE_API_TOKEN="$(tr -d '[:space:]' < "$HOME/.cf_token")" \
  CLOUDFLARE_ACCOUNT_ID="$(tr -d '[:space:]' < "$HOME/.cf_account")" \
  "${WRANGLER:-$HOME/gc-ops/node_modules/.bin/wrangler}" deploy
fi
