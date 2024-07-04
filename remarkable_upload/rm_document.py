from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass
class Document:
    id: str
    hash: str
    type: str
    visibleName: str
    pinned: bool
    lastModified: Optional[str] = None
    lastOpened: Optional[str] = None
    fileType: Optional[str] = None
    parent: Optional[str] = None

    def is_folder(self) -> bool:
        return self.type == "CollectionType"


def find_target_folder(docs: Iterable[Document], folder_name: str) -> Document:
    matched_folders = []
    for doc in filter(lambda x: x.is_folder(), docs):
        if doc.visibleName == folder_name:
            matched_folders.append(doc)
    if len(matched_folders) > 1:
        raise ValueError(f"Found multiple folders with name {folder_name}: {matched_folders}. Please specify a unique folder name.")
    elif len(matched_folders) == 1:
        return matched_folders[0]
    raise ValueError(f"Unable to find folder with name {folder_name}.")
