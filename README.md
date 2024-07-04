# Remarkable API Sync

Sync a directory to your Remarkable tablet using the Remarkable API.

## How it works

It takes your device token stored locally in your Chrome Extension Settings. It then uses
that to generate a user token which is used to:
1. get currently present documents under a given folder in the Remarkable Cloud
2. upload any new documents from the local folder to the Remarkable Cloud

## Usage

```bash
poetry run python remarkable_upload/rm_sync.py \
    --rm-dir-name Zotero \
    --upload-dir ~/Zotero/storage/ \
    --target-file-ext pdf \
    --max-upload-workers 2
```

If it's struggling to find your device token, use `./get_device_token.sh` to
investigate futher.
