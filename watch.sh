#!/bin/bash
#
# Default values for the parameters
RM_DIR_NAME="Zotero"
UPLOAD_DIR="$HOME/Zotero/storage/"
TARGET_FILE_EXT="pdf"
MAX_UPLOAD_WORKERS=2
# Zotero moves files around a lot, so we need to wait for a few events to accumulate
EVENT_ACCUMULATION_THRESHOLD=3

# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --rm-dir-name) RM_DIR_NAME="$2"; shift ;;
        --upload-dir) UPLOAD_DIR="$2"; shift ;;
        --target-file-ext) TARGET_FILE_EXT="$2"; shift ;;
        --max-upload-workers) MAX_UPLOAD_WORKERS="$2"; shift ;;
        --event-accumulation-threshold) EVENT_ACCUMULATION_THRESHOLD="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

events=()
echo "Begin collecting events until $EVENT_ACCUMULATION_THRESHOLD events are detected..."

# Use a single instance of fswatch and read its output line by line
fswatch -0 "$UPLOAD_DIR" | while read -d "" event; do
    if [[ "$event" == *.$TARGET_FILE_EXT ]]; then
        echo "Detected $TARGET_FILE_EXT file: $event"
        events+=("$event")
    fi

    if [ ${#events[@]} -ge $EVENT_ACCUMULATION_THRESHOLD ]; then
        events=()
        poetry run python remarkable_upload/rm_sync.py \
            --rm-dir-name "$RM_DIR_NAME" \
            --upload-dir "$UPLOAD_DIR" \
            --target-file-ext "$TARGET_FILE_EXT" \
            --max-upload-workers "$MAX_UPLOAD_WORKERS"
        echo "Refreshing event accumulation... Waiting until $EVENT_ACCUMULATION_THRESHOLD events are detected..."
    fi
done
