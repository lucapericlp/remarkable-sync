import os
import re
import binascii
import json
import base64
from functools import lru_cache
from mmap import PROT_READ, mmap
from pathlib import Path

import requests

url = "https://webapp.cloud.remarkable.com/token/json/2/user/new"
USER = os.environ["USER"]
EXTENSION_SETTINGS = f"/Users/{USER}/Library/Application Support/Google/Chrome/Default/Local Extension Settings/bfhkfdnddlhfippjbflipboognpdpoeh"


def strings(fname, n=6):
    with open(fname, "rb") as f, mmap(f.fileno(), 0, prot=PROT_READ) as m:
        for match in re.finditer(("([\w/]{%s}[\w/]*)" % n).encode(), m):
            yield match.group(0)


def get_device_token() -> str:
    for logs in sorted(
        Path(EXTENSION_SETTINGS).glob("*.log"), key=os.path.getmtime, reverse=True
    ):
        all_device_tokens = []
        _logs = [log for log in strings(logs)]
        for idx, line in enumerate(_logs):
            if line.decode() == "deviceToken":
                try:
                    jwt = [item for item in map(lambda x: json.loads(base64.b64decode(x.decode()).decode()), _logs[idx + 1 : idx + 3])]
                except (json.decoder.JSONDecodeError, binascii.Error):
                    continue
                valid_header = jwt[0] == {"alg": "HS256", "typ": "JWT"}
                valid_payload = set(jwt[1].keys()) == {"iat", "auth0-userid", "device-desc", "device-id", "iss", "jti", "sub", "nbf"}
                if not valid_header or not valid_payload:
                    continue
                device_token = ".".join([
                    jwt_part.decode()
                    for jwt_part in _logs[idx + 1: idx + 4]
                ])
                signature = _logs[idx+4].decode()
                device_token_with_signature = f"{device_token}-{signature}"
                all_device_tokens.append(device_token_with_signature)
        if all_device_tokens:
            most_recent_device_token = all_device_tokens[-1]
            return most_recent_device_token
    raise ValueError("Device token could not be found!")


def get_user_token(device_token: str) -> str:
    headers = {
        "accept": "*/*",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "authorization": f"Bearer {device_token}",
        "content-length": "0",
        "origin": "chrome-extension://bfhkfdnddlhfippjbflipboognpdpoeh",
        "priority": "u=1, I",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "none",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    }

    response = requests.post(url, headers=headers)
    if not response.ok:
        raise ValueError(f"Failed to get user token: {response.text}")

    return response.text


@lru_cache
def get_cached_user_token() -> str:
    return get_user_token(get_device_token())


if __name__ == "__main__":
    device_token = get_device_token()
    print(get_user_token(device_token))
