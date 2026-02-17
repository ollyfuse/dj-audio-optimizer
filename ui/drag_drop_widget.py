from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
import os

class DragDropWidget(QLabel):
    files_dropped = Signal(list)
    
    def __init__(self, text):
        super().__init__(text)
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #00ff88;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                color: #888;
                font-size: 16px;
            }
            QLabel:hover {
                border-color: #00ff00;
                background-color: #2a2a2a;
            }
        """)
        self.setMinimumHeight(120)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QLabel {
                    border: 2px dashed #00ff00;
                    border-radius: 10px;
                    padding: 40px;
                    text-align: center;
                    color: #00ff88;
                    font-size: 16px;
                    background-color: #2a2a2a;
                }
            """)
    
    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #00ff88;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                color: #888;
                font-size: 16px;
            }
        """)
    
    def dropEvent(self, event: QDropEvent):
        files = []
        audio_extensions = {'.mp3', '.wav', '.flac', '.aiff', '.m4a', '.ogg'}
        
        for url in event.mimeData().urls():
            if url.isLocalFile():
                file_path = url.toLocalFile()
                _, ext = os.path.splitext(file_path.lower())
                if ext in audio_extensions:
                    files.append(file_path)
        
        if files:
            self.files_dropped.emit(files)
            event.acceptProposedAction()
        
        self.dragLeaveEvent(event)
