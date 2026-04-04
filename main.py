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
        self.resize_edge = Qt.Edge(0)
        self.border_width = 8
        
        self.setWindowTitle("snip2path")
        self.setMinimumSize(300, 220)
        self.resize(350, 280)
        self.setMaximumSize(800, 600)
        
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setMouseTracking(True)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- ヘッダー ---
        self.header = QFrame()
        self.header.setFixedHeight(40)
        self.header.setStyleSheet("background-color: #0078d4; border: none;")
        h_layout = QHBoxLayout(self.header)
        h_layout.setContentsMargins(15, 0, 0, 0)
        
        title_label = QLabel("snip2path")
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 16px; background: transparent;")
        
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
        self.content_frame = QFrame()
        self.content_frame.setStyleSheet("background-color: white; border: 2px solid #0078d4; border-top: none;")
        c_layout = QVBoxLayout(self.content_frame)
        c_layout.setContentsMargins(20, 10, 20, 20)
        c_layout.setSpacing(15)
        
        self.status_label = QLabel("Loading...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("font-size: 11px; color: #666; border: none; background: transparent;")
        c_layout.addWidget(self.status_label)
        
        self.btn_snip = QPushButton("🚀 START SNIP")
        self.btn_snip.setMinimumHeight(80)
        self.btn_snip.setStyleSheet("""
            QPushButton { background-color: #f8f9fa; border: 2px solid #ddd; font-weight: bold; font-size: 22px; border-radius: 5px; }
            QPushButton:hover { background-color: #e2e6ea; }
        """)
        self.btn_snip.clicked.connect(self.logic.start_snipping)
        c_layout.addWidget(self.btn_snip)

        self.btn_link = QPushButton("🔗 Link to Project")
        self.btn_link.setMinimumHeight(40)
        self.btn_link.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.btn_link.clicked.connect(self.logic.ui_link_project)
        c_layout.addWidget(self.btn_link)

        self.btn_config = QPushButton("⚙️ Change Storage")
        self.btn_config.setMinimumHeight(40)
        self.btn_config.setStyleSheet("font-size: 14px;")
        self.btn_config.clicked.connect(self.logic.ui_set_master)
        c_layout.addWidget(self.btn_config)
        
        self.main_layout.addWidget(self.content_frame)
        self.update_status()

    def update_status(self, message=None):
        if message:
            self.status_label.setText(message)
            QTimer.singleShot(3000, lambda: self.update_status())
            return
        path = self.logic.project_mgr.master_img_path
        if path:
            self.status_label.setText(f"Master Path:\n{str(path.parent)}")
        else:
            self.status_label.setText("Storage: NOT SET")

    def _get_edge(self, pos):
        edge = Qt.Edge(0)
        if pos.x() <= self.border_width: edge |= Qt.LeftEdge
        if pos.x() >= self.width() - self.border_width: edge |= Qt.RightEdge
        if pos.y() <= self.border_width: edge |= Qt.TopEdge
        if pos.y() >= self.height() - self.border_width: edge |= Qt.BottomEdge
        return edge

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.position().toPoint()
            self.resize_edge = self._get_edge(pos)
            if self.resize_edge != Qt.Edge(0):
                self.old_rect = self.geometry()
                self.press_pos = event.globalPosition().toPoint()
            elif self.header.rect().contains(pos):
                self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        global_pos = event.globalPosition().toPoint()

        if not event.buttons():
            edge = self._get_edge(pos)
            if edge == (Qt.LeftEdge | Qt.TopEdge) or edge == (Qt.RightEdge | Qt.BottomEdge): self.setCursor(Qt.SizeFDiagCursor)
            elif edge == (Qt.RightEdge | Qt.TopEdge) or edge == (Qt.LeftEdge | Qt.BottomEdge): self.setCursor(Qt.SizeBDiagCursor)
            elif edge & (Qt.LeftEdge | Qt.RightEdge): self.setCursor(Qt.SizeHorCursor)
            elif edge & (Qt.TopEdge | Qt.BottomEdge): self.setCursor(Qt.SizeVerCursor)
            else: self.setCursor(Qt.ArrowCursor)
            return

        if self.resize_edge != Qt.Edge(0):
            diff = global_pos - self.press_pos
            r = QRect(self.old_rect)
            if self.resize_edge & Qt.LeftEdge: r.setLeft(self.old_rect.left() + diff.x())
            if self.resize_edge & Qt.RightEdge: r.setRight(self.old_rect.right() + diff.x())
            if self.resize_edge & Qt.TopEdge: r.setTop(self.old_rect.top() + diff.y())
            if self.resize_edge & Qt.BottomEdge: r.setBottom(self.old_rect.bottom() + diff.y())
            if r.width() >= self.minimumWidth() and r.height() >= self.minimumHeight():
                self.setGeometry(r)
        elif self.old_pos:
            delta = global_pos - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = global_pos

    def mouseReleaseEvent(self, event):
        self.old_pos = None
        self.resize_edge = Qt.Edge(0)

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
        success, _ = self.capturer.capture_and_save(rect)
        if success:
            if self.viewer is not None:
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
        visible_windows = [w for w in QApplication.topLevelWidgets() if w.isVisible() and w != self.menu]
        if not visible_windows:
            self.menu.show()

    def run(self):
        self.menu.show()
        sys.exit(self.qt_app.exec())

if __name__ == "__main__":
    app_instance = SnipApp()
    app_instance.run()
