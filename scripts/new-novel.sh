#!/usr/bin/env bash
# Copy the blank book. Name it. That copy is the novel.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TITLE="${*:-}"

if [[ -z "$TITLE" ]]; then
  echo "Usage: $0 \"The Title\""
  echo "Example: $0 \"Father of Mine\""
  exit 1
fi

SLUG="$(python3 -c '
import re, sys, unicodedata
plain = unicodedata.normalize("NFKD", sys.argv[1]).encode("ascii", "ignore").decode().lower()
print(re.sub(r"[^a-z0-9]+", "-", plain).strip("-"))
' "$TITLE")"

if [[ -z "$SLUG" ]]; then
  echo "Could not make a folder name from: $TITLE"
  exit 1
fi

DEST="$ROOT/novels/$SLUG"
JSON_TITLE="${TITLE//\\/\\\\}"
JSON_TITLE="${JSON_TITLE//\"/\\\"}"

if [[ -e "$DEST" ]]; then
  echo "Already exists: $DEST"
  exit 1
fi

cp -R "$ROOT/blank-book" "$DEST"
chmod -R u+w "$DEST"

cat > "$DEST/TODAY.md" <<EOF
# Today

**Novel:** $TITLE  
**Sitting:** none yet

This book has no pages yet.

Say *Interview me* — or keep talking if you already started in chat.

The partner will rewrite this page at the end of every sitting.
EOF

cat > "$DEST/README.md" <<EOF
# $TITLE

This folder is the whole book.

Open \`OPEN-ME.code-workspace\`. You will see the method on one side and this novel on the other.

Start at \`TODAY.md\`.
EOF

cat > "$DEST/OPEN-ME.code-workspace" <<EOF
{
  "folders": [
    {
      "name": "The method",
      "path": "../../writing-tools"
    },
    {
      "name": "$JSON_TITLE",
      "path": "."
    }
  ],
  "settings": {
    "editor.wordWrap": "on",
    "files.autoSave": "onFocusChange"
  }
}
EOF

echo "Book folder: $DEST"
echo "Open: $DEST/OPEN-ME.code-workspace"
echo "Then say: Interview me"
