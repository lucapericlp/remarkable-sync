import base64
import json
import logging
import mimetypes
from functools import lru_cache
from pathlib import Path
from threading import current_thread
from typing import Optional, Sequence

from requests import Response, Session

from remarkable_upload.config import DEFAULT_ENDPOINT, DEFAULT_HOST
from remarkable_upload.rm_document import Document
from remarkable_upload.rm_tokens import get_cached_user_token

logger = logging.getLogger(__name__)


def get_content_type(file_path: str) -> Optional[str]:
    content_type, _ = mimetypes.guess_type(file_path)
    return content_type


class RemarkableCloudClient:
    def __init__(
        self,
        user_token: Optional[str] = None,
        host: Optional[str] = None,
        endpoint: Optional[str] = None,
    ):
        self.host = host or DEFAULT_HOST
        self.endpoint = endpoint or DEFAULT_ENDPOINT
        self.url = f"{self.host}/{self.endpoint}"
        self.user_token = user_token or get_cached_user_token()
        self.session = Session()
        self.base_headers = {
            "accept": "*/*",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "accept-encoding": "gzip, deflate, br, zstd",
            "authorization": f"Bearer {self.user_token}",
            "rm-source": "RoR-Browser",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "none",
            "origin": "chrome-extension://bfhkfdnddlhfippjbflipboognpdpoeh",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            "referrerPolicy": "strict-origin-when-cross-origin",
        }

    def get(self) -> Sequence[Document]:
        response = self.session.get(self.url, headers=self.base_headers)
        response.raise_for_status()
        return [Document(**_doc) for _doc in response.json()]

    def upload(
        self, file_path: Path, parent: Optional[str] = None
    ) -> Optional[Response]:
        content_type = get_content_type(str(file_path))
        if not content_type:
            logger.warning(
                f"Could not determine content type for {file_path.name}. Skipping upload..."
            )
            return None
        _name = file_path.stem
        body = file_path.read_bytes()
        rm_meta = {"file_name": str(_name)}
        if parent:
            rm_meta["parent"] = parent
        headers = {
            **self.base_headers,
            "content-type": content_type,
            "rm-meta": base64.b64encode(json.dumps(rm_meta).encode()),
        }
        response = self.session.post(self.url, data=body, headers=headers)

        return response


@lru_cache
def get_rm_client(
    thread_id: str, host: Optional[str] = None, endpoint: Optional[str] = None
) -> RemarkableCloudClient:
    user_token = get_cached_user_token()
    return RemarkableCloudClient(user_token, host, endpoint)


def threadsafe_upload(file_path: Path, parent: Optional[str]) -> Optional[Response]:
    thread_id = current_thread().name
    rm = get_rm_client(thread_id)
    return rm.upload(file_path, parent)


if __name__ == "__main__":
    rm = RemarkableCloudClient()
    get_result = rm.get()
    print(f"Found {len(get_result)} documents!")
    _file, _content_type = Path("test.pdf"), "application/pdf"
    result = rm.upload(_file, _content_type)
    if result:
        print(result.status_code, result.text)
    else:
        print("Failed to upload!")
