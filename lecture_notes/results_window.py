import os

from aqt.qt import QDesktopServices, QDialog, QListWidget, QListWidgetItem, Qt, QUrl, QVBoxLayout


class ResultWindow(QDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setWindowTitle("Lecture Notes")
        self.results = QListWidget()
        self.results.itemActivated.connect(self.open_item)
        layout = QVBoxLayout(self)
        layout.addWidget(self.results)
        self.resize(600, 300)

    def show_results(self, results: list[tuple[str, int, str]]) -> None:
        self.results.clear()
        for path, page, snippet in results:
            item = QListWidgetItem(f"{os.path.basename(path)}  p.{page}\n{snippet}")
            item.setData(Qt.ItemDataRole.UserRole, (path, page))
            self.results.addItem(item)
        self.results.setCurrentRow(0)
        self.show()
        self.raise_()
        self.activateWindow()

    def open_item(self, item: QListWidgetItem) -> None:
        path, page = item.data(Qt.ItemDataRole.UserRole)
        # Opens at page 1 for now
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def keyPressEvent(self, event) -> None:
        # On macOS, Return doesn't activate a list row by itself
        item = self.results.currentItem()
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and item is not None:
            self.open_item(item)
        else:
            super().keyPressEvent(event)
