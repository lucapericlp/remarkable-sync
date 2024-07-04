# Remarkable Upload

Super simple script after quick reverse engineering of the Chrome extension.

## How it works

Takes your device token stored locally in your Chrome Extension Settings. Uses
that to generate a user token. Uses that to upload a file to the Remarkable cloud.

## Usage

```bash
python remarkable_upload/rm_post.py
```

If it's struggling to find your device token, use `./get_device_token.sh` to
investigate futher.
