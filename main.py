import sys
import os
import pathlib
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QFileDialog, QMessageBox, QLabel, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QPoint, QRect, QSize

# プロジェクト内のモジュールをインポート可能にする
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from core.project_mgr import ProjectManager
    from core.capture import SnipCapturer
except ImportError:
    class ProjectManager:
        def __init__(self): self.master_img_path = None
        def save_master_path(self, path): pass
        def link_to_project(self, path): return True, ""
        def get_latest_path(self): return ""
    class SnipCapturer:
        def __init__(self, mgr): pass
        def capture_and_save(self, rect): return True, ""

STYLESHEET = """
    QWidget { background-color: #ffffff; color: #333333; font-family: 'Segoe UI', 'Meiryo', sans-serif; }
    QFrame#ContentFrame { background-color: #ffffff; border: none; }
    QLabel#TitleLabel { color: white; font-weight: bold; font-size: 16px; background: transparent; }
    QLabel#StatusLabel {
        font-size: 11px; color: #444444; background: #f0f2f5;
        padding: 8px; border: 1px solid #dcdfe6; border-radius: 4px;
    }
    QPushButton {
        background-color: #ffffff; color: #606266; border: 1px solid #dcdfe6;
        border-radius: 5px; font-size: 14px; font-weight: bold; padding: 10px;
    }
    QPushButton#SnipButton {
        background-color: #0078d4; color: white; font-size: 22px; border: none; border-radius: 8px;
    }
    QPushButton#SnipButton:hover { background-color: #1a88df; }
"""

class MainMenu(QWidget):
    def __init__(self, logic):
        super().__init__()
        self.logic = logic
        self.setWindowTitle("snip2path")
        self.resize(400, 340)
        self.setStyleSheet(STYLESHEET)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.header = QFrame()
        self.header.setFixedHeight(35)
        self.header.setStyleSheet("background-color: #0078d4;")
        h_layout = QHBoxLayout(self.header)
        title = QLabel("snip2path")
        title.setObjectName("TitleLabel")
        h_layout.addWidget(title)
        layout.addWidget(self.header)

        self.content = QFrame()
        self.content.setObjectName("ContentFrame")
        c_layout = QVBoxLayout(self.content)
        
        self.status_label = QLabel("Storage: NOT SET")
        self.status_label.setObjectName("StatusLabel")
        c_layout.addWidget(self.status_label)
        
        self.btn_snip = QPushButton("🚀 START SNIP")
        self.btn_snip.setObjectName("SnipButton")
        self.btn_snip.setMinimumHeight(100)
        self.btn_snip.clicked.connect(self.logic.start_snipping)
        c_layout.addWidget(self.btn_snip)
        
        low_layout = QHBoxLayout()
        self.btn_link = QPushButton("🔗 Link to Project")
        self.btn_link.clicked.connect(self.logic.ui_link_project)
        self.btn_config = QPushButton("⚙️ Change Storage")
        self.btn_config.clicked.connect(self.logic.ui_set_master)
        low_layout.addWidget(self.btn_link)
        low_layout.addWidget(self.btn_config)
        c_layout.addLayout(low_layout)
        
        layout.addWidget(self.content)
        self.update_status()

    def update_status(self, message=None):
        if message:
            self.status_label.setText(message)
            QTimer.singleShot(3000, lambda: self.update_status())
            return
        path = self.logic.project_mgr.master_img_path
        self.status_label.setText(f"Storage: {path.parent if path else 'NOT SET'}")

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

    def ui_set_master(self):
        path = QFileDialog.getExistingDirectory(self.menu, "Select Master Folder")
        if path:
            self.project_mgr.save_master_path(path)
            self.menu.update_status("✅ Storage Updated")

    def ui_link_project(self):
        if not self.project_mgr.master_img_path: return
        project_root = QFileDialog.getExistingDirectory(self.menu, "Select Project Root")
        if not project_root: return
        success, _ = self.project_mgr.link_to_project(project_root)
        if success: self.menu.update_status("🔗 Linked Successfully!")

    def start_snipping(self):
        if not self.project_mgr.master_img_path: return
        self.menu.hide()
        
        from gui.overlay import SnippingOverlay
        self.overlay = SnippingOverlay()
        
        # 閉じられた時にメイン画面を戻す
        self.overlay.setAttribute(Qt.WA_DeleteOnClose)
        self.overlay.destroyed.connect(self._restore_menu)
        
        self.overlay.snip_finished.connect(self.on_snip)
        self.overlay.show()
        # ESCキーを効かせるためのフォーカス
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
            self.menu.show()
            self.menu.raise_()
            self.menu.activateWindow()

    def run(self):
        self.menu.show()
        sys.exit(self.qt_app.exec())

if __name__ == "__main__":
    app_instance = SnipApp()
    app_instance.run()