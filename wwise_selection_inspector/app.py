from __future__ import annotations

import sys
from collections import Counter
from dataclasses import dataclass
from typing import Any

from PySide6.QtCore import QObject, Qt, QTimer, Signal
from PySide6.QtGui import QAction
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from waapi import WaapiClient

from wwise_selection_inspector import __app_name__


SELECTION_TOPIC = "ak.wwise.ui.selectionChanged"
GET_SELECTED_OBJECTS = "ak.wwise.ui.getSelectedObjects"
SINGLE_INSTANCE_SERVER_NAME = "kameron_wwise_selection_inspector"

RETURN_FIELDS = [
    "id",
    "name",
    "type",
    "path",
    "originalFilePath",
    "sound:originalWavFilePath",
]


@dataclass(frozen=True)
class WwiseObject:
    name: str
    object_type: str
    path: str


class SingleInstanceGuard(QObject):
    activate_requested = Signal()

    def __init__(self, server_name: str) -> None:
        super().__init__()
        self.server_name = server_name
        self.server = QLocalServer(self)

    def acquire(self) -> bool:
        socket = QLocalSocket()
        socket.connectToServer(self.server_name)

        if socket.waitForConnected(200):
            socket.write(b"activate")
            socket.flush()
            socket.waitForBytesWritten(200)
            socket.disconnectFromServer()
            return False

        QLocalServer.removeServer(self.server_name)

        if not self.server.listen(self.server_name):
            # Fail open. The inspector is still useful even if single-instance setup fails.
            return True

        self.server.newConnection.connect(self._on_new_connection)
        return True

    def _on_new_connection(self) -> None:
        while self.server.hasPendingConnections():
            socket = self.server.nextPendingConnection()
            if socket is None:
                continue

            socket.readyRead.connect(lambda socket=socket: self._read_socket(socket))
            if socket.bytesAvailable() > 0:
                self._read_socket(socket)

    def _read_socket(self, socket: QLocalSocket) -> None:
        socket.readAll()
        socket.disconnectFromServer()
        self.activate_requested.emit()


class SelectionBridge(QObject):
    selection_changed = Signal()
    connection_failed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.client: WaapiClient | None = None
        self.subscription: Any | None = None

    def connect(self) -> bool:
        try:
            self.client = WaapiClient()
            self.subscription = self.client.subscribe(SELECTION_TOPIC, self._on_selection_changed)
            return True
        except Exception as exc:
            self.connection_failed.emit(str(exc))
            self.client = None
            self.subscription = None
            return False

    def disconnect(self) -> None:
        if self.subscription is not None:
            try:
                self.subscription.unsubscribe()
            except Exception:
                pass
            self.subscription = None

        if self.client is not None:
            try:
                self.client.disconnect()
            except Exception:
                pass
            self.client = None

    def get_selected_objects(self) -> list[WwiseObject]:
        if self.client is None:
            return []

        result = self.client.call(
            GET_SELECTED_OBJECTS,
            {},
            {"return": RETURN_FIELDS},
        )

        objects = result.get("objects", [])
        return [
            WwiseObject(
                name=str(obj.get("name") or ""),
                object_type=str(obj.get("type") or "Unclassified"),
                path=str(
                    obj.get("path")
                    or obj.get("originalFilePath")
                    or obj.get("sound:originalWavFilePath")
                    or ""
                ),
            )
            for obj in objects
        ]

    def _on_selection_changed(self, *args: Any, **kwargs: Any) -> None:
        self.selection_changed.emit()


class WwiseSelectionInspectorWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.bridge = SelectionBridge()
        self.bridge.selection_changed.connect(self.refresh_selection)
        self.bridge.connection_failed.connect(self.show_connection_error)

        self.setWindowTitle(__app_name__)
        self.resize(460, 560)

        self.status_label = QLabel("Disconnected")
        self.status_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.count_label = QLabel("Selected Objects: 0")
        self.count_label.setObjectName("countLabel")

        self.type_label = QLabel("-")
        self.type_label.setWordWrap(True)
        self.type_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.list_widget = QListWidget()

        self.always_on_top_checkbox = QCheckBox("Always on top")
        self.always_on_top_checkbox.stateChanged.connect(self.apply_always_on_top)

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_to_wwise)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_selection)
        self.refresh_button.setEnabled(False)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.connect_button)
        button_layout.addWidget(self.refresh_button)
        button_layout.addStretch()
        button_layout.addWidget(self.always_on_top_checkbox)

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.count_label)
        layout.addWidget(self.type_label)
        layout.addWidget(self.list_widget)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.add_shortcuts()
        QTimer.singleShot(0, self.connect_to_wwise)

    def add_shortcuts(self) -> None:
        refresh_action = QAction(self)
        refresh_action.setShortcut("Ctrl+R")
        refresh_action.triggered.connect(self.refresh_selection)
        self.addAction(refresh_action)

    def activate_existing_window(self) -> None:
        self.show()
        self.setWindowState((self.windowState() & ~Qt.WindowMinimized) | Qt.WindowActive)
        self.raise_()
        self.activateWindow()

    def connect_to_wwise(self) -> None:
        self.bridge.disconnect()
        self.status_label.setText("Connecting to Wwise Authoring API...")

        if not self.bridge.connect():
            self.refresh_button.setEnabled(False)
            self.connect_button.setText("Reconnect")
            self.status_label.setText("Disconnected. Check Wwise Authoring API settings.")
            return

        self.refresh_button.setEnabled(True)
        self.connect_button.setText("Reconnect")
        self.status_label.setText("Connected to Wwise Authoring API")
        self.refresh_selection()

    def refresh_selection(self) -> None:
        try:
            objects = self.bridge.get_selected_objects()
        except Exception as exc:
            self.status_label.setText("Disconnected. Selection refresh failed.")
            self.refresh_button.setEnabled(False)
            self.show_connection_error(str(exc))
            return

        self.count_label.setText(f"Selected Objects: {len(objects)}")
        self.type_label.setText(self.format_type_counts(objects))
        self.list_widget.clear()

        for obj in objects:
            item = QListWidgetItem(f"[{obj.object_type}] {obj.name}\n{obj.path}")
            item.setToolTip(obj.path)
            self.list_widget.addItem(item)

    def format_type_counts(self, objects: list[WwiseObject]) -> str:
        if not objects:
            return "-"

        counts = Counter(obj.object_type for obj in objects)
        parts = [f"{object_type}: {count}" for object_type, count in sorted(counts.items())]
        return " / ".join(parts)

    def apply_always_on_top(self) -> None:
        flags = self.windowFlags()
        if self.always_on_top_checkbox.isChecked():
            flags |= Qt.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowStaysOnTopHint

        self.setWindowFlags(flags)
        self.show()

    def show_connection_error(self, message: str) -> None:
        QMessageBox.warning(
            self,
            "Wwise Connection Failed",
            "Failed to connect to Wwise Authoring API.\n\n"
            "Check the following:\n"
            "1. Wwise Authoring is running.\n"
            "2. Project > User Preferences > Enable Wwise Authoring API is enabled.\n"
            "3. WAAPI port access is not blocked.\n\n"
            f"Error: {message}",
        )

    def closeEvent(self, event: Any) -> None:
        self.bridge.disconnect()
        super().closeEvent(event)


def main() -> int:
    app = QApplication(sys.argv)

    guard = SingleInstanceGuard(SINGLE_INSTANCE_SERVER_NAME)
    if not guard.acquire():
        return 0

    window = WwiseSelectionInspectorWindow()
    guard.activate_requested.connect(window.activate_existing_window)
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
