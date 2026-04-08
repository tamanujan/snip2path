import sys
import os
import pathlib
import base64
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QPushButton, QFileDialog, QLabel, QFrame, QSizePolicy, QComboBox, QStyle,
)
from PySide6.QtCore import Qt, QTimer, QBuffer, QIODevice, QByteArray
from PySide6.QtGui import QFontMetrics, QColor, QPalette

# プロジェクト内のモジュールをインポート可能にする
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from core.project_mgr import ProjectManager
    from core.capture import SnipCapturer
except ImportError:
    class ProjectManager:
        def __init__(self):
            self.app_dir = pathlib.Path.home() / ".snip2path"
            self.master_img_path = self.app_dir / "latest.png"
        def link_to_project(self, path): return True, ""
        def get_latest_path(self): return str(self.master_img_path)
    class SnipCapturer:
        def __init__(self, mgr): pass
        def capture_and_save(self, rect): return True, ""

STYLESHEET = """
    QWidget#MainRoot {
        background-color: #f5f5f5;
        color: #242424;
        font-family: 'Segoe UI', 'Meiryo', sans-serif;
    }
    QFrame#ContentBody {
        background-color: #f5f5f5;
        border: none;
    }
    QFrame#FormPanel {
        background-color: #ffffff;
        border: 1px solid #e5e5e5;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        border-bottom-left-radius: 0px;
        border-bottom-right-radius: 0px;
    }
    QLabel#CaptionLabel {
        font-size: 12px;
        font-weight: 600;
        color: #424242;
        background: transparent;
        padding: 0;
    }
    QLabel#StorageLineLabel {
        font-size: 12px;
        color: #242424;
        background-color: #ffffff;
        border: 1px solid #c4c4c4;
        border-radius: 4px;
        padding: 9px 12px;
    }
    QPushButton#SecondaryButton {
        background-color: #ffffff;
        color: #242424;
        border: 1px solid #8a8886;
        border-radius: 4px;
        font-size: 14px;
        font-weight: 600;
        padding: 12px 16px;
        min-height: 44px;
    }
    QPushButton#SecondaryButton:hover {
        background-color: #f3f2f1;
        border-color: #242424;
    }
    QPushButton#SnipButton {
        background-color: #0078d4;
        color: #ffffff;
        font-size: 19px;
        font-weight: 600;
        border: none;
        border-radius: 4px;
        padding: 16px;
        min-height: 88px;
    }
    QPushButton#SnipButton:hover { background-color: #106ebe; }
    QPushButton#SnipButton:disabled { background-color: #c7e0f4; color: #ffffff; }
    QComboBox#DelayCombo {
        background-color: #ffffff;
        color: #242424;
        border: 1px solid #c4c4c4;
        border-radius: 4px;
        font-size: 13px;
        padding: 8px 12px 8px 12px;
        padding-right: 36px;
        min-height: 40px;
    }
    QComboBox#DelayCombo:hover { border-color: #242424; }
    QComboBox#DelayCombo:focus { border-color: #0078d4; }
    QComboBox#DelayCombo::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: center right;
        width: 34px;
        border: none;
        border-left: 1px solid #c4c4c4;
        border-top-right-radius: 3px;
        border-bottom-right-radius: 3px;
        background-color: #f3f2f1;
    }
    QComboBox#DelayCombo::drop-down:hover {
        background-color: #edebe9;
    }
    QComboBox QAbstractItemView {
        background-color: #ffffff;
        color: #201f1e;
        selection-background-color: #0078d4;
        selection-color: #ffffff;
        border: 1px solid #8a8886;
        outline: none;
        padding: 2px;
    }
    QComboBox QAbstractItemView::item {
        min-height: 28px;
        padding: 4px 12px;
        color: #201f1e;
    }
    QComboBox QAbstractItemView::item:hover {
        background-color: #f3f2f1;
        color: #201f1e;
    }
    QComboBox QAbstractItemView::item:selected {
        background-color: #0078d4;
        color: #ffffff;
    }
"""

# Fixed size avoids resize/reflow quirks (rounded panel + combo focus ring) on Windows.
# No in-window title bar — OS caption shows "snip2path".
_MAIN_WINDOW_FIXED_SIZE = (400, 454)


class MainMenu(QWidget):
    def __init__(self, logic):
        super().__init__()
        self.logic = logic
        self.setObjectName("MainRoot")
        self.setWindowTitle("snip2path")
        w, h = _MAIN_WINDOW_FIXED_SIZE
        self.setFixedSize(w, h)
        self._storage_flash = None

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        body = QFrame()
        body.setObjectName("ContentBody")
        body.setAttribute(Qt.WA_StyledBackground, True)
        c_layout = QVBoxLayout(body)
        c_layout.setContentsMargins(18, 18, 18, 18)
        c_layout.setSpacing(0)

        form = QFrame()
        form.setObjectName("FormPanel")
        form.setAttribute(Qt.WA_StyledBackground, True)
        form.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        form_layout = QVBoxLayout(form)
        form_layout.setContentsMargins(14, 14, 18, 28)
        form_layout.setSpacing(0)

        cap = QLabel("Save location")
        cap.setObjectName("CaptionLabel")
        form_layout.addWidget(cap)
        form_layout.addSpacing(6)

        self.storage_value_label = QLabel()
        self.storage_value_label.setObjectName("StorageLineLabel")
        self.storage_value_label.setWordWrap(False)
        self.storage_value_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.storage_value_label.setMinimumHeight(36)
        form_layout.addWidget(self.storage_value_label)

        form_layout.addSpacing(16)

        delay_lbl = QLabel("Delay before snip")
        delay_lbl.setObjectName("CaptionLabel")
        form_layout.addWidget(delay_lbl)
        form_layout.addSpacing(6)

        self.combo_delay = QComboBox()
        self.combo_delay.setObjectName("DelayCombo")
        self.combo_delay.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.combo_delay.addItem("Instant", 0)
        self.combo_delay.addItem("3 seconds", 3)
        self.combo_delay.addItem("5 seconds", 5)
        self.combo_delay.addItem("7 seconds", 7)
        self.combo_delay.setMinimumHeight(42)
        form_layout.addWidget(self.combo_delay)
        self._apply_combo_popup_theme(self.combo_delay)
        form_layout.addSpacing(6)

        c_layout.addWidget(form)

        c_layout.addSpacing(18)

        self.btn_snip = QPushButton("🚀 Start snip")
        self.btn_snip.setObjectName("SnipButton")
        self.btn_snip.setCursor(Qt.PointingHandCursor)
        self.btn_snip.clicked.connect(self.logic.start_snipping)
        c_layout.addWidget(self.btn_snip)

        c_layout.addSpacing(12)

        self.btn_link = QPushButton("Link to project")
        self.btn_link.setObjectName("SecondaryButton")
        self.btn_link.setCursor(Qt.PointingHandCursor)
        self.btn_link.clicked.connect(self.logic.ui_link_project)
        c_layout.addWidget(self.btn_link)
        c_layout.addStretch(1)

        body.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        root.addWidget(body, 1)
        self.update_status()
        self.setStyleSheet(STYLESHEET + MainMenu._delay_combo_arrow_stylesheet())

    @staticmethod
    def _delay_combo_arrow_stylesheet() -> str:
        app = QApplication.instance()
        if app is None:
            return ""
        pm = app.style().standardPixmap(QStyle.StandardPixmap.SP_ArrowDown)
        if pm.isNull() or pm.width() <= 0:
            return ""
        ba = QByteArray()
        buf = QBuffer(ba)
        buf.open(QIODevice.OpenModeFlag.WriteOnly)
        if not pm.save(buf, "PNG"):
            return ""
        b64 = base64.standard_b64encode(bytes(ba)).decode("ascii")
        return f"""
    QComboBox#DelayCombo::down-arrow {{
        image: url(data:image/png;base64,{b64});
        width: 14px;
        height: 14px;
        margin-right: 7px;
    }}
    """

    @staticmethod
    def _apply_combo_popup_theme(combo: QComboBox):
        view = combo.view()
        view.setAutoFillBackground(True)
        pal = view.palette()
        pal.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
        pal.setColor(QPalette.ColorRole.AlternateBase, QColor("#f3f2f1"))
        pal.setColor(QPalette.ColorRole.Text, QColor("#201f1e"))
        pal.setColor(QPalette.ColorRole.Window, QColor("#ffffff"))
        pal.setColor(QPalette.ColorRole.Highlight, QColor("#0078d4"))
        pal.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        view.setPalette(pal)

    def showEvent(self, event):
        super().showEvent(event)
        if self._storage_flash is None:
            QTimer.singleShot(0, self._refresh_storage_path)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._storage_flash is None:
            self._refresh_storage_path()

    def _refresh_storage_path(self):
        app_dir = self.logic.project_mgr.app_dir
        path = str(app_dir)
        w = max(self.storage_value_label.width() - 24, 80)
        if w < 80:
            w = 280
        fm = QFontMetrics(self.storage_value_label.font())
        self.storage_value_label.setText(fm.elidedText(path, Qt.TextElideMode.ElideMiddle, w))

    def update_status(self, message=None):
        if message:
            self._storage_flash = message
            self.storage_value_label.setText(message)
            QTimer.singleShot(3000, lambda: self._clear_storage_flash_if(message))
            return
        self._storage_flash = None
        self._refresh_storage_path()

    def _clear_storage_flash_if(self, msg):
        if self._storage_flash == msg:
            self.update_status()

    def set_status_line(self, text):
        self._storage_flash = text
        self.storage_value_label.setText(text)

    def delay_seconds(self) -> int:
        v = self.combo_delay.currentData()
        return int(v) if v is not None else 0

    def closeEvent(self, event):
        QApplication.quit()
        event.accept()

class SnipApp:
    def __init__(self):
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
        self.qt_app = QApplication.instance() or QApplication(sys.argv)
        self.project_mgr = ProjectManager()
        self.capturer = SnipCapturer(self.project_mgr)
        self.menu = MainMenu(self)
        self.viewer = None
        self._countdown_timer = None
        self._delay_remaining = 0

    def ui_link_project(self):
        project_root = QFileDialog.getExistingDirectory(self.menu, "Select Project Root")
        if not project_root: return
        success, _ = self.project_mgr.link_to_project(project_root)
        if success: self.menu.update_status("🔗 Linked Successfully!")

    def start_snipping(self):
        delay_sec = self.menu.delay_seconds()
        if delay_sec <= 0:
            self._begin_overlay_snip()
            return
        self._delay_remaining = delay_sec
        self.menu.btn_snip.setEnabled(False)
        self.menu.btn_link.setEnabled(False)
        self.menu.set_status_line(f"Snip in {self._delay_remaining}s…")
        self._countdown_timer = QTimer(self.menu)
        self._countdown_timer.setInterval(1000)
        self._countdown_timer.timeout.connect(self._on_snip_countdown_tick)
        self._countdown_timer.start()

    def _on_snip_countdown_tick(self):
        self._delay_remaining -= 1
        if self._delay_remaining > 0:
            self.menu.set_status_line(f"Snip in {self._delay_remaining}s…")
            return
        if self._countdown_timer:
            self._countdown_timer.stop()
            self._countdown_timer.deleteLater()
            self._countdown_timer = None
        self.menu.btn_snip.setEnabled(True)
        self.menu.btn_link.setEnabled(True)
        self._begin_overlay_snip()

    def _begin_overlay_snip(self):
        self.menu.hide()

        from gui.overlay import SnippingOverlay
        self.overlay = SnippingOverlay()

        self.overlay.setAttribute(Qt.WA_DeleteOnClose)
        self.overlay.destroyed.connect(self._restore_menu)

        self.overlay.snip_finished.connect(self.on_snip)
        self.overlay.show()
        self.overlay.activateWindow()
        self.overlay.setFocus()

    def on_snip(self, rect):
        from gui.viewer import SnipViewer
        success, _ = self.capturer.capture_and_save(rect)
        if success:
            if self.viewer: self.viewer.close()
            self.viewer = SnipViewer(self.project_mgr.get_latest_path(), self.start_snipping)
            self.viewer.setAttribute(Qt.WA_DeleteOnClose)
            self.viewer.destroyed.connect(self._on_viewer_destroyed)
            # --- スニップ位置に移動する処理を復活 ---
            self.viewer.move(rect.x() - 1, rect.y() - 31)
            self.viewer.show()

    def _on_viewer_destroyed(self):
        self.viewer = None
        QTimer.singleShot(100, self._restore_menu)

    def _restore_menu(self):
        visible = [w for w in QApplication.topLevelWidgets() if w.isVisible() and w != self.menu]
        if not visible:
            if self._countdown_timer:
                self._countdown_timer.stop()
                self._countdown_timer.deleteLater()
                self._countdown_timer = None
            self.menu.btn_snip.setEnabled(True)
            self.menu.btn_link.setEnabled(True)
            self.menu.update_status()
            self.menu.show()
            self.menu.raise_()
            self.menu.activateWindow()

    def run(self):
        self.menu.show()
        sys.exit(self.qt_app.exec())

if __name__ == "__main__":
    app_instance = SnipApp()
    app_instance.run()