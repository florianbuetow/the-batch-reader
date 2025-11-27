#!/bin/bash
# Hook script called after combine-transcripts target
# Customize this script for your own post-processing needs

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="$SCRIPT_DIR/data/output"

# Default behavior: On macOS, copy files to iCloud Drive for ElevenReader
if [[ "$(uname)" == "Darwin" ]]; then
    ICLOUD_BASE="$HOME/Library/Mobile Documents/com~apple~CloudDocs"
    DEST_DIR="$ICLOUD_BASE/Elevenreader/Andrew Ng - The Batch"

    # Ensure iCloud Drive base exists
    if [[ -d "$ICLOUD_BASE" ]]; then
        # Create destination folder if it doesn't exist
        mkdir -p "$DEST_DIR"

        # Copy 6-month period files (overwrite existing)
        count=0
        for file in "$OUTPUT_DIR"/*_jan_jun.txt "$OUTPUT_DIR"/*_jul_dec.txt; do
            if [[ -f "$file" ]]; then
                cp "$file" "$DEST_DIR/"
                ((count++))
            fi
        done

        echo "Copied $count files to iCloud Drive"
    else
        echo "Warning: iCloud Drive not found at $ICLOUD_BASE"
    fi
else
    echo "hook.sh: Not on macOS, skipping iCloud sync"
fi
