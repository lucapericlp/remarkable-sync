# Remarkable API Sync

Sync a directory to your Remarkable tablet using the Remarkable API.

## Pre-requisites

1. Installed & connected `Read on Remarkable` extension on your Chrome browser
2. `poetry` installed (https://python-poetry.org/docs/)
3. [Optional] `fswatch` installed for automated sync

## Usage

### Automated Sync
```bash
chmod +x watch.sh
./watch.sh --rm-dir-name Zotero \
    --upload-dir ~/Zotero/storage/ \
    --target-file-ext pdf \
    --max-upload-workers 2 \
    --event-accumulation-threshold 3
```

### Manual Sync
```bash
poetry run python remarkable_upload/rm_sync.py \
    --rm-dir-name Zotero \
    --upload-dir ~/Zotero/storage/ \
    --target-file-ext pdf \
    --max-upload-workers 2
```

If it's struggling to find your device token, use `./get_device_token.sh` to
investigate futher.

## How it works

It takes your device token stored locally in your Chrome Extension Settings. It then uses
that to generate a user token which is used to:
1. get currently present documents under a given folder in the Remarkable Cloud
2. upload any new documents from the local folder to the Remarkable Cloud

## OS Support

Currently only tested on MacOS. Device token extraction will not work on other OSs. Adding support should be straightforward, see `remarkable_upload/rm_tokens.py`.
