import os
import logging

logger = logging.getLogger(__name__)
DEFAULT_HOST = "https://internal.cloud.remarkable.com"
DEFAULT_ENDPOINT = "doc/v2/files"
DIR_TO_UPLOAD = os.environ["UPLOAD_DIR"]
TARGET_FILE_EXT = "pdf"
# be careful with this value as it can lead to rate limiting!
MAX_RM_UPLOAD_WORKERS = int(os.environ.get("MAX_RM_UPLOAD_WORKERS", 1))
logger.info(f"Using {MAX_RM_UPLOAD_WORKERS=} for concurrent uploads.")
