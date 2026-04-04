from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPixmap

class SnipViewer(QWidget):
    def __init__(self, image_path, redo_callback):
        super().__init__()
        self.redo_callback = redo_callback
        self.old_pos = None
        
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- ヘッダー（高さを30pxに拡大） ---
        self.header = QFrame()
        self.header.setStyleSheet("background-color: #0078d4; color: white; border: none;")
        self.header.setFixedHeight(30)
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(10, 0, 5, 0)

        # 文字サイズを12pxに拡大
        title = QLabel("Snip")
        title.setStyleSheet("font-size: 12px; font-weight: bold; color: white; background: transparent; border: none;")
        
        # Retryボタンを大きく (幅60px, 高さ22px)
        btn_redo = QPushButton("Retry")
        btn_redo.setFixedSize(60, 22)
        btn_redo.setStyleSheet("background-color: #005a9e; border: none; font-size: 11px; color: white; font-weight: bold;")
        btn_redo.clicked.connect(self.on_redo)

        # ×ボタンを大きく (25x22px)
        btn_close = QPushButton("×")
        btn_close.setFixedSize(30, 22)
        btn_close.setStyleSheet("background-color: #e81123; border: none; color: white; font-weight: bold; font-size: 14px;")
        btn_close.clicked.connect(self.close)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(btn_redo)
        header_layout.addWidget(btn_close)
        layout.addWidget(self.header)

        self.label = QLabel()
        pixmap = QPixmap(image_path)
        self.label.setPixmap(pixmap)
        self.label.setStyleSheet("border: 1px solid #1a1a1a; background-color: black;")
        layout.addWidget(self.label)

        self.resize(pixmap.size().width() + 2, pixmap.size().height() + 32)

    def on_redo(self):
        self.close()
        self.redo_callback()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()
