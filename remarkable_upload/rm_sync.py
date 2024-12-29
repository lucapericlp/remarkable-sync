import os
import click
import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Callable, Optional, Sequence, List, Tuple

from tqdm import tqdm

from remarkable_upload.config import DIR_TO_UPLOAD, MAX_RM_UPLOAD_WORKERS, TARGET_FILE_EXT
from remarkable_upload.rm_client import RemarkableCloudClient, threadsafe_upload
from remarkable_upload.rm_document import find_target_folder


logger = logging.getLogger(__name__)


@dataclass
class SyncCandidates:
    to_upload: List[Path]
    skipped: List[Path]
    total_files: int


class RemarkableSyncer:
    def __init__(
        self,
        client: RemarkableCloudClient,
        get_target_docs: Callable[[], Sequence[Path]],
        upload_workers: int = MAX_RM_UPLOAD_WORKERS,
        get_doc_name: Callable[[Path], str] = lambda x: x.stem,
    ):
        logger.info(f"Using {upload_workers=} for concurrent uploads.")
        self.client = client
        self.get_target_docs = get_target_docs
        self.get_doc_name = get_doc_name

    def determine_sync_candidates(
        self, *, rm_dir_name: Optional[str] = None
    ) -> SyncCandidates:
        """
        First step of sync process: Determine which files need to be synced
        and which already exist on the device.

        Returns:
            SyncCandidates object containing files to upload and skipped files
        """
        rm_docs = self.client.get()
        folder_id = find_target_folder(rm_docs, rm_dir_name).id if rm_dir_name else None
        is_target_dir_child = lambda x: x.parent == folder_id
        rm_docs_names = {doc.visibleName for doc in rm_docs if is_target_dir_child(doc)}

        skipped, to_upload = [], []
        target_docs = self.get_target_docs()
        total_files = len(target_docs)

        for doc in target_docs:
            if self.get_doc_name(doc) in rm_docs_names:
                skipped.append(doc)
            else:
                to_upload.append(doc)

        # Pretty print sync candidates
        print("\nSync Candidates Summary:")
        print("=" * 50)
        print(f"Total files found: {total_files}")
        print(f"Files to upload: {len(to_upload)}")
        print(f"Files to skip (already exist): {len(skipped)}")

        if to_upload:
            print("\nFiles to be uploaded:")
            for doc in to_upload:
                print(f"  - {doc.name}")
        print("=" * 50)

        return SyncCandidates(to_upload=to_upload, skipped=skipped, total_files=total_files)

    def perform_sync(
        self, candidates: SyncCandidates, folder_id: Optional[str] = None
    ) -> Tuple[List[Path], List[Path]]:
        """
        Second step of sync process: Actually upload the files that were determined
        as candidates for sync.

        Returns:
            Tuple of (successful_uploads, failed_uploads)
        """
        if not candidates.to_upload:
            print("\nNo files to sync!")
            return [], []

        with ThreadPoolExecutor(max_workers=MAX_RM_UPLOAD_WORKERS) as executor:
            partialed_upload = partial(threadsafe_upload, parent=folder_id)
            failed_uploads, successful_uploads = [], []

            print("\nStarting sync process...")
            for upload_response, doc in tqdm(
                zip(executor.map(partialed_upload, candidates.to_upload), candidates.to_upload),
                total=len(candidates.to_upload),
            ):
                if not upload_response or not upload_response.ok:
                    logger.error(f"Failed to upload {doc.name} due to {upload_response=}")
                    failed_uploads.append(doc)
                else:
                    successful_uploads.append(doc)

        # Calculate and display sync results
        success_rate = (len(successful_uploads) / len(candidates.to_upload)) * 100
        print("\nSync Results:")
        print("=" * 50)
        print(f"Overall success rate: {success_rate:.1f}%")
        print(f"Successfully uploaded: {len(successful_uploads)} files")
        print(f"Failed to upload: {len(failed_uploads)} files")

        if failed_uploads:
            print("\nFailed uploads:")
            for doc in failed_uploads:
                print(f"  - {doc.name}")
        print("=" * 50)

        return successful_uploads, failed_uploads

    def sync(self, *, rm_dir_name: Optional[str] = None):
        """
        Main sync method that coordinates the two-step sync process:
        1. Determine what needs to be synced
        2. Perform the actual sync
        """
        # Step 1: Determine what to sync
        candidates = self.determine_sync_candidates(rm_dir_name=rm_dir_name)

        # Get folder ID if needed
        folder_id = None
        if rm_dir_name:
            rm_docs = self.client.get()
            folder_id = find_target_folder(rm_docs, rm_dir_name).id

        # Step 2: Perform the sync
        successful_uploads, failed_uploads = self.perform_sync(candidates, folder_id)
        return successful_uploads, failed_uploads


@click.command()
@click.option("--rm-dir-name", default=None, help="Name of the folder to upload files to")
@click.option("--upload-dir", default=DIR_TO_UPLOAD, help="Directory to upload files from")
@click.option("--target-file-ext", default=TARGET_FILE_EXT, help="File extension to upload from your target local directory")
@click.option("--max-upload-workers", default=MAX_RM_UPLOAD_WORKERS, help="Number of concurrent uploads to the Remarkable Cloud")
@click.option("--dry-run", is_flag=True, help="Only show what would be synced without performing the actual sync")
def sync(rm_dir_name, upload_dir, target_file_ext, max_upload_workers, dry_run):
    client = RemarkableCloudClient()
    get_files = lambda: list(sorted(Path(upload_dir).rglob(f"*.{target_file_ext}"), key=os.path.getmtime))
    syncer = RemarkableSyncer(client, get_files, max_upload_workers)

    if dry_run:
        syncer.determine_sync_candidates(rm_dir_name=rm_dir_name)
    else:
        syncer.sync(rm_dir_name=rm_dir_name)


if __name__ == "__main__":
    sync()
