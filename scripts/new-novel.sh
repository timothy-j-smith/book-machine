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

SLUG="$(printf '%s' "$TITLE" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//')"

if [[ -z "$SLUG" ]]; then
  echo "Could not make a folder name from: $TITLE"
  exit 1
fi

DEST="$ROOT/novels/$SLUG"

if [[ -e "$DEST" ]]; then
  echo "Already exists: $DEST"
  exit 1
fi

cp -R "$ROOT/blank-book" "$DEST"

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
      "name": "$TITLE",
      "path": "."
    }
  ],
  "settings": {
    "editor.wordWrap": "on"
  }
}
EOF

echo "Book folder: $DEST"
echo "Open: $DEST/OPEN-ME.code-workspace"
echo "Then say: Interview me"
