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
    # デバッグ用ダミー
    class ProjectManager:
        def __init__(self): self.master_img_path = None
        def save_master_path(self, path): pass
        def link_to_project(self, path): return True, ""
        def get_latest_path(self): return ""
    class SnipCapturer:
        def __init__(self, mgr): pass
        def capture_and_save(self, rect): return True, ""

# --- ライトモード・スタイルシート ---
STYLESHEET = """
    QWidget {
        background-color: #ffffff;
        color: #333333;
        font-family: 'Segoe UI', 'Meiryo', sans-serif;
    }
    
    QFrame#ContentFrame {
        background-color: #ffffff;
        border: none;
    }
    
    QLabel#TitleLabel {
        color: white;
        font-weight: bold;
        font-size: 16px;
        background: transparent;
    }
    
    QLabel#StatusLabel {
        font-size: 11px;
        color: #444444;
        background: #f0f2f5;
        padding: 8px;
        border: 1px solid #dcdfe6;
        border-radius: 4px;
    }
    
    QPushButton {
        background-color: #ffffff;
        color: #606266;
        border: 1px solid #dcdfe6;
        border-radius: 5px;
        font-size: 14px;
        font-weight: bold;
        padding: 10px;
    }
    QPushButton:hover {
        background-color: #ecf5ff;
        color: #409eff;
        border: 1px solid #c6e2ff;
    }
    QPushButton:pressed {
        background-color: #d9ecff;
    }
    
    QPushButton#SnipButton {
        background-color: #0078d4;
        color: white;
        font-size: 22px;
        border: none;
        border-radius: 8px;
    }
    QPushButton#SnipButton:hover {
        background-color: #1a88df;
    }
    QPushButton#SnipButton:pressed {
        background-color: #006cc1;
    }
"""

class MainMenu(QWidget):
    def __init__(self, logic):
        super().__init__()
        self.logic = logic
        
        self.setWindowTitle("snip2path")
        self.setMinimumSize(320, 260)
        self.resize(400, 340)
        self.setWindowFlags(Qt.WindowType.Window)
        
        self.setStyleSheet(STYLESHEET)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- ヘッダー ---
        self.header = QFrame()
        self.header.setFixedHeight(35)
        self.header.setStyleSheet("background-color: #0078d4; border: none;")
        h_layout = QHBoxLayout(self.header)
        h_layout.setContentsMargins(15, 0, 15, 0)
        
        title_label = QLabel("snip2path")
        title_label.setObjectName("TitleLabel")
        
        h_layout.addWidget(title_label)
        h_layout.addStretch()
        self.main_layout.addWidget(self.header)

        # --- コンテンツエリア ---
        self.content_frame = QFrame()
        self.content_frame.setObjectName("ContentFrame")
        c_layout = QVBoxLayout(self.content_frame)
        c_layout.setContentsMargins(20, 15, 20, 20)
        c_layout.setSpacing(15)
        
        # フルパス表示用のラベル（ここを修正）
        self.status_label = QLabel("Storage: NOT SET")
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status_label.setWordWrap(True) # 長いパスを折り返し
        self.status_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        c_layout.addWidget(self.status_label)
        
        button_layout = QVBoxLayout()
        button_layout.setSpacing(12)
        
        self.btn_snip = QPushButton("🚀 START SNIP")
        self.btn_snip.setObjectName("SnipButton")
        self.btn_snip.setMinimumHeight(100)
        self.btn_snip.setCursor(Qt.PointingHandCursor)
        self.btn_snip.clicked.connect(self.logic.start_snipping)
        button_layout.addWidget(self.btn_snip)
        
        lower_button_layout = QHBoxLayout()
        lower_button_layout.setSpacing(10)

        self.btn_link = QPushButton("🔗 Link to Project")
        self.btn_link.setMinimumHeight(45)
        self.btn_link.setCursor(Qt.PointingHandCursor)
        self.btn_link.clicked.connect(self.logic.ui_link_project)
        lower_button_layout.addWidget(self.btn_link)

        self.btn_config = QPushButton("⚙️ Change Storage")
        self.btn_config.setMinimumHeight(45)
        self.btn_config.setCursor(Qt.PointingHandCursor)
        self.btn_config.clicked.connect(self.logic.ui_set_master)
        lower_button_layout.addWidget(self.btn_config)
        
        button_layout.addLayout(lower_button_layout)
        c_layout.addLayout(button_layout)
        
        self.main_layout.addWidget(self.content_frame)
        self.update_status()

    def update_status(self, message=None):
        if message:
            self.status_label.setText(message)
            QTimer.singleShot(3000, lambda: self.update_status())
            return
        
        path = self.logic.project_mgr.master_img_path
        if path:
            full_path = str(path.parent)
            self.status_label.setText(f"Storage: {full_path}")
        else:
            self.status_label.setText("Storage: NOT SET")

    def closeEvent(self, event):
        QApplication.quit()
        event.accept()

class SnipApp:
    def __init__(self):
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
        self.qt_app = QApplication.instance() or QApplication(sys.argv)
        self.qt_app.setQuitOnLastWindowClosed(True)
        
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
        if not self.project_mgr.master_img_path:
            QMessageBox.warning(self.menu, "Error", "Set Master Storage first!")
            return
        project_root = QFileDialog.getExistingDirectory(self.menu, "Select Project Root")
        if not project_root: return
        snips_dir = pathlib.Path(project_root) / ".snips"
        if snips_dir.exists():
            msg = f"Already linked or folder exists:\n{snips_dir}\n\nDo you want to overwrite it?"
            reply = QMessageBox.question(self.menu, "Already Exists", msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                self.menu.update_status("⚠️ Linking Cancelled")
                return
        success, error_msg = self.project_mgr.link_to_project(project_root)
        if success: self.menu.update_status("🔗 Linked Successfully!")
        else: QMessageBox.critical(self.menu, "Link Error", f"Failed: {error_msg}")

    def start_snipping(self):
        if not self.project_mgr.master_img_path: return
        self.menu.hide()
        from gui.overlay import SnippingOverlay
        self.overlay = SnippingOverlay()
        self.overlay.snip_finished.connect(self.on_snip)
        self.overlay.show()

    def on_snip(self, rect):
        if rect.width() < 5 or rect.height() < 5:
            self._restore_menu()
            return
        from gui.viewer import SnipViewer
        success, _ = self.capturer.capture_and_save(rect)
        if success:
            if self.viewer: self.viewer.close()
            self.viewer = SnipViewer(self.project_mgr.get_latest_path(), self.start_snipping)
            self.viewer.setAttribute(Qt.WA_DeleteOnClose)
            self.viewer.destroyed.connect(self._on_viewer_destroyed)
            self.viewer.move(rect.x() - 1, rect.y() - 31)
            self.viewer.show()
        else: self._restore_menu()

    def _on_viewer_destroyed(self):
        self.viewer = None
        QTimer.singleShot(100, self._restore_menu)

    def _restore_menu(self):
        visible_windows = [w for w in QApplication.topLevelWidgets() if w.isVisible() and w != self.menu]
        if not visible_windows: self.menu.show()

    def run(self):
        self.menu.show()
        sys.exit(self.qt_app.exec())

if __name__ == "__main__":
    app_instance = SnipApp()
    app_instance.run()