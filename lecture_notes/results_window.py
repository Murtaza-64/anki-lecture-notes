import os

from aqt.qt import (
    QDesktopServices,
    QDialog,
    QListWidget,
    QListWidgetItem,
    QSplitter,
    Qt,
    QUrl,
    QVBoxLayout,
    QWebEngineSettings,
    QWebEngineView,
)


class ResultWindow(QDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setWindowTitle("Lecture Notes")

        self.results = QListWidget()
        self.results.itemActivated.connect(self.open_item)
        self.results.currentItemChanged.connect(self.show_page)

        self.viewer = QWebEngineView()
        # The built-in PDF viewer shows a blank page unless plugins are enabled
        self.viewer.settings().setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)

        splitter = QSplitter()
        splitter.addWidget(self.results)
        splitter.addWidget(self.viewer)
        splitter.setSizes([350, 850])

        layout = QVBoxLayout(self)
        layout.addWidget(splitter)
        self.resize(1200, 800)

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

    def show_page(self, current: QListWidgetItem | None, previous: QListWidgetItem | None) -> None:
        # clear() fires this too, with no current row
        if current is None:
            return
        path, page = current.data(Qt.ItemDataRole.UserRole)
        url = QUrl.fromLocalFile(path)
        url.setFragment(f"page={page}")
        self.viewer.setUrl(url)

    def open_item(self, item: QListWidgetItem) -> None:
        path, page = item.data(Qt.ItemDataRole.UserRole)
        # The whole PDF in the default app, for when the viewer isn't enough
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def keyPressEvent(self, event) -> None:
        # On macOS, Return doesn't activate a list row by itself
        item = self.results.currentItem()
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and item is not None:
            self.open_item(item)
        else:
            super().keyPressEvent(event)
