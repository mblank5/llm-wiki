#!/bin/bash
# convert.sh — One-command paper conversion: arxiv2md + place in raw/untracked
# Usage: bash convert.sh <arxiv_id> [wiki_dir]
# Example: bash convert.sh 2603.25562 ~/my-wiki
set -e

ARXIV_ID="${1:?Usage: bash convert.sh <arxiv_id> [wiki_dir]}"
WIKI_DIR="${2:-.}"

# Extract year and month from arxiv ID (YYMM.NNNNN)
YEAR_PART="${ARXIV_ID:0:2}"
MONTH_PART="${ARXIV_ID:2:2}"
FULL_YEAR="20${YEAR_PART}"

TARGET_DIR="$WIKI_DIR/raw/untracked/$FULL_YEAR/$MONTH_PART"
mkdir -p "$TARGET_DIR"

echo "Converting arxiv:$ARXIV_ID..."
arxiv2md "$ARXIV_ID" -o "$TARGET_DIR/${ARXIV_ID}.md"

echo "  -> $TARGET_DIR/${ARXIV_ID}.md"
echo ""
echo "Ready to ingest:"
echo "  cd $WIKI_DIR && wiki ingest \"$FULL_YEAR/$MONTH_PART/${ARXIV_ID}.md\" -y"
