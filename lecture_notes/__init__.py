import os
import sys
from collections import Counter

addon_dir = os.path.dirname(__file__)
vendor_dir = os.path.join(addon_dir, "vendor")
sys.path.insert(0, vendor_dir)

from aqt import mw
from aqt.qt import QAction
from aqt.utils import showInfo

NOTES_DIR = os.path.expanduser("~/Documents/Revision/Misc")
USER_FILES_DIR = os.path.join(addon_dir, "user_files")
INDEX_PATH = os.path.join(USER_FILES_DIR, "index.db")

print("lecture_notes: loaded")


def update_index() -> None:
    # Imported here because PyMuPDF adds about half a second to Anki's startup
    from .core.index import open_index
    from .core.sync import sync_folder

    if not os.path.isdir(NOTES_DIR):
        showInfo(f"Notes folder not found: {NOTES_DIR}")
        return

    os.makedirs(USER_FILES_DIR, exist_ok=True)
    conn = open_index(INDEX_PATH)
    try:
        counts = Counter(sync_folder(conn, NOTES_DIR).values())
    finally:
        conn.close()

    if counts:
        showInfo(f"Indexed {counts['indexed']}, removed {counts['removed']}, failed {counts['failed']}")
    else:
        showInfo("Index is up to date: nothing changed.")


action = QAction("Lecture Notes: Update index", mw)
action.triggered.connect(update_index)
mw.form.menuTools.addAction(action)
