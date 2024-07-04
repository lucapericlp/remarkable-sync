import os
import logging
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path
from typing import Callable, Optional, Sequence

from tqdm import tqdm

from remarkable_upload.config import DIR_TO_UPLOAD, MAX_RM_UPLOAD_WORKERS, TARGET_FILE_EXT
from remarkable_upload.rm_client import RemarkableCloudClient, threadsafe_upload
from remarkable_upload.rm_document import find_target_folder

logger = logging.getLogger(__name__)


class RemarkableSyncer:
    def __init__(
        self,
        client: RemarkableCloudClient,
        get_target_docs: Callable[[], Sequence[Path]],
        get_doc_name: Callable[[Path], str] = lambda x: x.stem,
    ):
        self.client = client
        self.get_target_docs = get_target_docs
        self.get_doc_name = get_doc_name

    def sync(self, *, rm_dir_name: Optional[str] = None):
        """
        Syncs local files to the Remarkable Cloud (optionally under a specific folder)

        N.B rm_dir_name must just be the folder name and not the full path on your device
        """
        rm_docs = self.client.get()
        folder_id = find_target_folder(rm_docs, rm_dir_name).id if rm_dir_name else None
        is_target_dir_child = lambda x: x.parent == folder_id
        rm_docs_names = {doc.visibleName for doc in rm_docs if is_target_dir_child(doc)}

        skipped, to_upload = [], []
        target_docs = self.get_target_docs()
        # Sequence over Iterable here to use len() usage (albeit at the cost of memory) for logging purposes
        total_files = len(target_docs)

        for doc in target_docs:
            if self.get_doc_name(doc) in rm_docs_names:
                logger.info(
                    f"Skipping {doc.stem} as it already exists in the target folder!"
                )
                skipped.append(doc)
            else:
                to_upload.append(doc)

        logger.info(
            f"Skipped {len(skipped)} already existing files out of {total_files=}"
        )

        with ThreadPoolExecutor(max_workers=MAX_RM_UPLOAD_WORKERS) as executor:
            partialed_upload = partial(threadsafe_upload, parent=folder_id)
            failed_upload, successful_upload = [], []
            for upload_response, doc in tqdm(
                zip(executor.map(partialed_upload, to_upload), to_upload),
                total=len(to_upload),
            ):
                if not upload_response or not upload_response.ok:
                    logger.error(
                        f"Failed to upload {doc.name} due to {upload_response=}"
                    )
                    failed_upload.append(doc)
                else:
                    successful_upload.append(doc)
            logger.info(
                f"Successfully uploaded {len(successful_upload)} files out of {total_files=}"
            )
            logger.info(
                f"Failed to upload {len(failed_upload)} files out of {total_files=}"
            )


if __name__ == "__main__":
    client = RemarkableCloudClient()
    get_files = lambda: list(sorted(Path(DIR_TO_UPLOAD).rglob(f"*.{TARGET_FILE_EXT}"), key=os.path.getmtime))
    syncer = RemarkableSyncer(client, get_files)
    syncer.sync(rm_dir_name="Zotero")
