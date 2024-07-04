from requests import Response, Session
from pathlib import Path

from remarkable_upload.rm_new import get_device_token, get_user_token

import json

class Remarkable:
    def __init__(self, user_token: str):
        self.user_token = user_token

    def upload(self, file_path: Path, content_type: str) -> Response:
        url = "https://internal.cloud.remarkable.com/doc/v2/files"
        headers = {
            "accept": "*/*",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            'accept-encoding': 'gzip, deflate, br, zstd',
            "authorization": f"Bearer {self.user_token}",
            "rm-meta": "eyJmaWxlX25hbWUiOiJQcm9hY3RpdmUgRGV0ZWN0aW9uIG9mIFZvaWNlIENsb25pbmcgd2l0aCBMb2NhbGl6ZWQgV2F0ZXJtYXJraW5nIn0=",
            "rm-source": "RoR-Browser",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "none",
            "origin": "chrome-extension://bfhkfdnddlhfippjbflipboognpdpoeh",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            #  "content-type": "application/epub+zip",
            "referrerPolicy": "strict-origin-when-cross-origin",
            "content-type": content_type,
        }

        session = Session()

        body = Path(file_path).read_bytes()
        response = session.post(url, data=body, headers=headers)

        return response


if __name__ == '__main__':
    device_token = get_device_token()
    if not device_token:
        print("No device token found.")
        exit(1)
    user_token = get_user_token(device_token)
    rm = Remarkable(user_token)
    _file, _content_type = Path("2401.17264v2.pdf"), "application/pdf"
    result = rm.upload(_file, _content_type)
    print(result.status_code, result.text)
