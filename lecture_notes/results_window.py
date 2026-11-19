import os

from aqt.qt import QDialog, QListWidget, QVBoxLayout


class ResultWindow(QDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setWindowTitle("Lecture Notes")
        self.results = QListWidget()
        layout = QVBoxLayout(self)
        layout.addWidget(self.results)
        self.resize(600, 300)

    def show_results(self, results: list[tuple[str, int, str]]) -> None:
        self.results.clear()
        for path, page, snippet in results:
            self.results.addItem(f"{os.path.basename(path)}  p.{page}\n{snippet}")
        self.show()
        self.raise_()
        self.activateWindow()
