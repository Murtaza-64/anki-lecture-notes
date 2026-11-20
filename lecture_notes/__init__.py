import os
import sys
from collections import Counter

addon_dir = os.path.dirname(__file__)
vendor_dir = os.path.join(addon_dir, "vendor")
sys.path.insert(0, vendor_dir)

from aqt import gui_hooks, mw
from aqt.operations import QueryOp
from aqt.qt import QAction, QFileDialog
from aqt.utils import showInfo, tooltip

from .core.card_text import build_query, clean_card_text
from .core.index import open_index, search_with_snippets
from .results_window import ResultWindow

USER_FILES_DIR = os.path.join(addon_dir, "user_files")
INDEX_PATH = os.path.join(USER_FILES_DIR, "index.db")
RESULTS_SHOWN = 5

print("lecture_notes: loaded")


def choose_notes_folder() -> str | None:
    folder = QFileDialog.getExistingDirectory(mw, "Choose your lecture notes folder")
    if not folder:
        return None
    config = mw.addonManager.getConfig(__name__)
    config["notes_folder"] = folder
    mw.addonManager.writeConfig(__name__, config)
    return folder


def notes_folder() -> str | None:
    # The saved folder if it still exists, otherwise ask for one
    folder = os.path.expanduser(mw.addonManager.getConfig(__name__)["notes_folder"])
    if folder and os.path.isdir(folder):
        return folder
    if folder:
        tooltip(f"Notes folder not found: {folder}")
    return choose_notes_folder()


def update_index() -> None:
    # Main thread: anything that may need the user happens before the background work starts
    folder = notes_folder()
    if folder is None:
        return

    os.makedirs(USER_FILES_DIR, exist_ok=True)
    QueryOp(
        parent=mw,
        op=lambda col: index_folder(folder),
        success=report_counts,
    ).without_collection().with_progress("Indexing lecture notes…").run_in_background()


def index_folder(folder: str) -> Counter:
    # Background thread: no UI calls, and a connection of its own
    # Imported here because PyMuPDF adds about half a second to Anki's startup
    from .core.sync import sync_folder

    conn = open_index(INDEX_PATH)
    try:
        return Counter(sync_folder(conn, folder).values())
    finally:
        conn.close()


def report_counts(counts: Counter) -> None:
    # Main thread again: QueryOp calls this with what index_folder returned
    if counts:
        showInfo(f"Indexed {counts['indexed']}, removed {counts['removed']}, failed {counts['failed']}")
    else:
        showInfo("Index is up to date: nothing changed.")


def change_notes_folder() -> None:
    if choose_notes_folder():
        update_index()


def find_pages() -> None:
    if not os.path.exists(INDEX_PATH):
        showInfo("No index yet: run Tools > Lecture Notes: Update index first.")
        return

    card = mw.reviewer.card
    if card is None:
        return

    # Only the side on screen, so the results can't give the answer away
    html = card.answer() if mw.reviewer.state == "answer" else card.question()
    query = build_query(clean_card_text(html))
    if not query:
        tooltip("This card has no text to search")
        return

    conn = open_index(INDEX_PATH)
    try:
        results = search_with_snippets(conn, query, limit=RESULTS_SHOWN)
    finally:
        conn.close()

    if not results:
        tooltip("No matching pages")
        return
    result_window.show_results(results)


def add_review_shortcut(state: str, shortcuts: list) -> None:
    if state == "review":
        shortcuts.append((mw.addonManager.getConfig(__name__)["shortcut"], find_pages))


result_window = ResultWindow(mw)

update_action = QAction("Lecture Notes: Update index", mw)
update_action.triggered.connect(update_index)
mw.form.menuTools.addAction(update_action)

folder_action = QAction("Lecture Notes: Choose notes folder…", mw)
folder_action.triggered.connect(change_notes_folder)
mw.form.menuTools.addAction(folder_action)

gui_hooks.state_shortcuts_will_change.append(add_review_shortcut)
