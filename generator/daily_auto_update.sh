#!/usr/bin/env bash
set -e

PROJECT_DIR="/root/projects/iviz-credit-cards"
LOG_FILE="$PROJECT_DIR/logs/auto_update.log"
mkdir -p "$PROJECT_DIR/logs"

echo "=== [$(date '+%Y-%m-%d %H:%M:%S')] Starting Daily Cards Sync ===" >> "$LOG_FILE"

# 1. Build Static Pages
echo "--- Building Pages ---" >> "$LOG_FILE"
python3 "$PROJECT_DIR/generator/build_pages.py" >> "$LOG_FILE" 2>&1

# 2. Deploy to Cloudflare Pages
echo "--- Deploying to Cloudflare Pages ---" >> "$LOG_FILE"
# Source environment variables if .env exists
if [ -f "$PROJECT_DIR/.env" ]; then
  set -a
  source "$PROJECT_DIR/.env"
  set +a
fi

export CLOUDFLARE_API_TOKEN="${CLOUDFLARE_API_TOKEN:?set this in your environment or .env}"
export CLOUDFLARE_ACCOUNT_ID="${CLOUDFLARE_ACCOUNT_ID:?set this in your environment or .env}"
/root/node_modules/.bin/wrangler pages deploy "$PROJECT_DIR/dist" --project-name=ringgit-iviztrading --branch=main --commit-dirty=true >> "$LOG_FILE" 2>&1

# 3. Purge Cloudflare Cache
echo "--- Purging Cache ---" >> "$LOG_FILE"
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/${CLOUDFLARE_ZONE_ID:?missing zone id}/purge_cache" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{"purge_everything":true}' >> "$LOG_FILE" 2>&1

echo "=== [$(date '+%Y-%m-%d %H:%M:%S')] Done ===" >> "$LOG_FILE"
