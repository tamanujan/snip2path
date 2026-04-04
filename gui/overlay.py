from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRect, Signal, QPoint
from PySide6.QtGui import QPainter, QColor, QPen

class SnippingOverlay(QWidget):
    snip_finished = Signal(QRect)
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.CrossCursor)
        self.showFullScreen()
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.is_selecting = False

    def paintEvent(self, event):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(0, 0, 0, 100))
        if self.is_selecting:
            r = QRect(self.start_point, self.end_point).normalized()
            p.setCompositionMode(QPainter.CompositionMode_Clear)
            p.fillRect(r, Qt.transparent)
            p.setCompositionMode(QPainter.CompositionMode_SourceOver)
            p.setPen(QPen(QColor(255, 255, 255), 2))
            p.drawRect(r)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.start_point = self.end_point = e.pos()
            self.is_selecting = True
            self.update()

    def mouseMoveEvent(self, e):
        if self.is_selecting:
            self.end_point = e.pos()
            self.update()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.is_selecting = False
            r = QRect(self.start_point, self.end_point).normalized()
            if r.width() > 5: self.snip_finished.emit(r)
            self.close()
