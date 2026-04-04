import sys
import os
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QMessageBox, QLabel, QFrame
from PySide6.QtCore import Qt, QTimer, QPoint, QRect

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.project_mgr import ProjectManager
from core.capture import SnipCapturer

class MainMenu(QWidget):
    def __init__(self, logic):
        super().__init__()
        self.logic = logic
        self.old_pos = None
        self.resize_edge = 0
        self.border_width = 10
        
        self.setWindowTitle("snip2path")
        self.setMinimumSize(320, 320)
        self.resize(380, 350)
        self.setMaximumSize(800, 600)
        
        # 【修正】Qt.WindowStaysOnTopHint を削除し、普通のウィンドウ挙動に。
        # 枠なし（Frameless）は維持してデザインを守ります。
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        
        self.setMouseTracking(True)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setStyleSheet("background-color: white; border: 1px solid #0078d4;")

        # --- ヘッダー ---
        self.header = QFrame()
        self.header.setFixedHeight(40)
        self.header.setStyleSheet("background-color: #0078d4; border: none;")
        self.header.setMouseTracking(True)
        h_layout = QHBoxLayout(self.header)
        h_layout.setContentsMargins(15, 0, 0, 0)
        
        title_label = QLabel("snip2path")
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 16px; border: none; background: transparent;")
        
        self.btn_close = QPushButton("×")
        self.btn_close.setFixedSize(50, 40)
        self.btn_close.setStyleSheet("""
            QPushButton { background-color: #e81123; color: white; font-weight: bold; border: none; font-size: 20px; }
            QPushButton:hover { background-color: #f1707a; }
        """)
        self.btn_close.clicked.connect(self.close)
        
        h_layout.addWidget(title_label)
        h_layout.addStretch()
        h_layout.addWidget(self.btn_close)
        self.main_layout.addWidget(self.header)

        # --- コンテンツエリア ---
        self.content_container = QFrame()
        self.content_container.setMouseTracking(True)
        self.content_container.setStyleSheet("border: none; background: transparent;")
        c_layout = QVBoxLayout(self.content_container)
        c_layout.setContentsMargins(20, 15, 20, 20)
        c_layout.setSpacing(15)
        
        self.status_label = QLabel("Loading...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("font-size: 10px; color: #777; border: none; background: transparent;")
        c_layout.addWidget(self.status_label)
        
        btn_style = """
            QPushButton { 
                background-color: #fcfcfc; 
                border: 1px solid #ddd; 
                border-radius: 4px; 
                color: #333;
                padding: 10px;
            }
            QPushButton:hover { 
                background-color: #f0f7ff; 
                border: 1px solid #0078d4; 
            }
        """

        self.btn_snip = QPushButton("🚀 START SNIP")
        self.btn_snip.setSizePolicy(self.btn_snip.sizePolicy().Policy.Expanding, self.btn_snip.sizePolicy().Policy.Expanding)
        self.btn_snip.setStyleSheet(btn_style + "font-weight: bold; font-size: 20px;")
        self.btn_snip.clicked.connect(self.logic.start_snipping)
        c_layout.addWidget(self.btn_snip, stretch=2)

        self.btn_link = QPushButton("🔗 Link to Project")
        self.btn_link.setSizePolicy(self.btn_link.sizePolicy().Policy.Expanding, self.btn_link.sizePolicy().Policy.Expanding)
        self.btn_link.setStyleSheet(btn_style + "font-size: 14px; font-weight: bold;")
        self.btn_link.clicked.connect(self.logic.ui_link_project)
        c_layout.addWidget(self.btn_link, stretch=1)

        self.btn_config = QPushButton("⚙️ Change Storage")
        self.btn_config.setSizePolicy(self.btn_config.sizePolicy().Policy.Expanding, self.btn_config.sizePolicy().Policy.Expanding)
        self.btn_config.setStyleSheet(btn_style + "font-size: 14px;")
        self.btn_config.clicked.connect(self.logic.ui_set_master)
        c_layout.addWidget(self.btn_config, stretch=1)
        
        self.main_layout.addWidget(self.content_container)
        self.update_status()

    def update_status(self, message=None):
        if message:
            self.status_label.setText(message)
            QTimer.singleShot(3000, lambda: self.update_status())
            return
        path = self.logic.project_mgr.master_img_path
        self.status_label.setText(f"Master Path:\n{str(path.parent)}" if path else "Storage: NOT SET")

    def _get_edge(self, pos):
        edge = 0
        if pos.x() <= self.border_width: edge |= 1
        if pos.x() >= self.width() - self.border_width: edge |= 2
        if pos.y() <= self.border_width: edge |= 4
        if pos.y() >= self.height() - self.border_width: edge |= 8
        return edge

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.position().toPoint()
            self.resize_edge = self._get_edge(pos)
            if self.resize_edge > 0:
                self.old_rect = self.geometry()
                self.press_pos = event.globalPosition().toPoint()
            elif self.header.rect().contains(pos):
                self.old_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        global_pos = event.globalPosition().toPoint()
        if not event.buttons():
            edge = self._get_edge(pos)
            if edge in (1, 2): self.setCursor(Qt.SizeHorCursor)
            elif edge in (4, 8): self.setCursor(Qt.SizeVerCursor)
            elif edge in (5, 10): self.setCursor(Qt.SizeFDiagCursor)
            elif edge in (6, 9): self.setCursor(Qt.SizeBDiagCursor)
            else: self.setCursor(Qt.ArrowCursor)
            return
        if self.resize_edge > 0:
            diff = global_pos - self.press_pos
            r = QRect(self.old_rect)
            if self.resize_edge & 1: r.setLeft(self.old_rect.left() + diff.x())
            if self.resize_edge & 2: r.setRight(self.old_rect.right() + diff.x())
            if self.resize_edge & 4: r.setTop(self.old_rect.top() + diff.y())
            if self.resize_edge & 8: r.setBottom(self.old_rect.bottom() + diff.y())
            if r.width() >= self.minimumWidth() and r.height() >= self.minimumHeight():
                self.setGeometry(r)
        elif self.old_pos:
            delta = global_pos - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = global_pos
        event.accept()

    def mouseReleaseEvent(self, event):
        self.old_pos = None
        self.resize_edge = 0
        event.accept()

    def closeEvent(self, event):
        QApplication.quit()
        event.accept()

class SnipApp:
    def __init__(self):
        self.qt_app = QApplication.instance() or QApplication(sys.argv)
        self.qt_app.setQuitOnLastWindowClosed(True)
        self.project_mgr = ProjectManager()
        self.capturer = SnipCapturer(self.project_mgr)
        self.menu = MainMenu(self)
        self.viewer = None

    def run(self):
        self.menu.show()
        sys.exit(self.qt_app.exec())

    def ui_set_master(self):
        path = QFileDialog.getExistingDirectory(self.menu, "Select Master Folder")
        if path:
            self.project_mgr.save_master_path(path)
            self.menu.update_status("✅ Storage Updated")

    def ui_link_project(self):
        if not self.project_mgr.master_img_path:
            QMessageBox.warning(self.menu, "Error", "Set Master Storage first!")
            return
        path = QFileDialog.getExistingDirectory(self.menu, "Select Project Root")
        if path:
            success, _ = self.project_mgr.link_to_project(path)
            if success:
                self.menu.update_status("🔗 Linked Successfully!")

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
        if self.capturer.capture_and_save(rect)[0]:
            if self.viewer:
                try: self.viewer.close()
                except: pass
            self.viewer = SnipViewer(self.project_mgr.get_latest_path(), self.start_snipping)
            self.viewer.setAttribute(Qt.WA_DeleteOnClose)
            self.viewer.destroyed.connect(self._on_viewer_destroyed)
            self.viewer.move(rect.x() - 1, rect.y() - 31)
            self.viewer.show()
        else:
            self._restore_menu()

    def _on_viewer_destroyed(self):
        self.viewer = None
        QTimer.singleShot(100, self._restore_menu)

    def _restore_menu(self):
        if not [w for w in QApplication.topLevelWidgets() if w.isVisible() and w != self.menu]:
            self.menu.show()

if __name__ == "__main__":
    SnipApp().run()
