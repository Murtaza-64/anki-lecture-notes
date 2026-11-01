import os
import sys
from collections import Counter

addon_dir = os.path.dirname(__file__)
vendor_dir = os.path.join(addon_dir, "vendor")
sys.path.insert(0, vendor_dir)

from aqt import gui_hooks, mw
from aqt.qt import QAction
from aqt.utils import showInfo

from .core.card_text import build_query, clean_card_text
from .core.index import open_index, search

NOTES_DIR = os.path.expanduser("~/Documents/Revision/Misc")
USER_FILES_DIR = os.path.join(addon_dir, "user_files")
INDEX_PATH = os.path.join(USER_FILES_DIR, "index.db")
RESULTS_SHOWN = 5

print("lecture_notes: loaded")


def update_index() -> None:
    # Imported here because PyMuPDF adds about half a second to Anki's startup
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


def find_pages() -> None:
    if not os.path.exists(INDEX_PATH):
        showInfo("No index yet: run Tools > Lecture Notes: Update index first.")
        return

    card = mw.reviewer.card
    if card is None:
        return

    text = " ".join(clean_card_text(field) for field in card.note().values())
    query = build_query(text)
    if not query:
        print("lecture_notes: this card has no text to search")
        return

    conn = open_index(INDEX_PATH)
    try:
        results = search(conn, query, limit=RESULTS_SHOWN)
    finally:
        conn.close()

    print(f"lecture_notes: top {len(results)} pages")
    for path, page in results:
        print(f"  {os.path.basename(path)} p.{page}")


def add_review_shortcut(state: str, shortcuts: list) -> None:
    if state == "review":
        shortcuts.append(("n", find_pages))


action = QAction("Lecture Notes: Update index", mw)
action.triggered.connect(update_index)
mw.form.menuTools.addAction(action)

gui_hooks.state_shortcuts_will_change.append(add_review_shortcut)
