import os
import sys

vendor_dir = os.path.join(os.path.dirname(__file__), "vendor")
sys.path.insert(0, vendor_dir)

from aqt import mw
from aqt.qt import QAction
from aqt.utils import showInfo

print("lecture_notes: loaded")


def show_card_count() -> None:
    showInfo(f"Card count: {mw.col.card_count()}")


action = QAction("Lecture Notes: card count", mw)
action.triggered.connect(show_card_count)
mw.form.menuTools.addAction(action)
