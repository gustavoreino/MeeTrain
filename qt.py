import sys
import random
import cv2
from gaze_tracking import GazeTracking
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QTimer


class CameraApp(QWidget):

    def __init__(self):

        super().__init__()
        self.setWindowTitle("Camera Feed")
        self.image_label = QLabel()
        self.image_label.setFixedSize(640, 480)
        self.status_label = QLabel("Waiting for gaze...")
        self.status_label.setAlignment(QtCore.Qt.AlignTop)
        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.image_label)
        self.setLayout(layout)

        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        self.gaze = GazeTracking()

        
        layout.addWidget(self.status_label)

        # Create a timer to grab frames
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # in milliseconds (~33ms ≈ 30 FPS)

    def update_frame(self):
        
        ret, frame = self.cap.read()
        if not ret:
            return

        # Always refresh gaze with the ORIGINAL frame (in BGR!)
        self.gaze.refresh(frame)

        # Get the annotated frame (still in BGR)
        annotated_frame = self.gaze.annotated_frame()

        # Draw additional pupil coordinates
        left_pupil = self.gaze.pupil_left_coords()
        right_pupil = self.gaze.pupil_right_coords()
        cv2.putText(annotated_frame, "Left pupil:  " + str(left_pupil), (90, 130),
                    cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
        cv2.putText(annotated_frame, "Right pupil: " + str(right_pupil), (90, 165),
                    cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)

        # Determine gaze direction
        if self.gaze.is_blinking():
            message = "Blinking"
        elif self.gaze.is_right():
            message = "Right"
        elif self.gaze.is_left():
            message = "Left"
        elif self.gaze.is_center():
            message = "Center"
        else:
            message = "Missing"
        self.status_label.setText(message)

        # Convert BGR to RGB for Qt display
        rgb_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(qt_image))


    def closeEvent(self, event):
        self.cap.release()

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.hello = ["Hallo Welt", "Hei maailma", "Hola Mundo", "Привет мир"]

        self.button = QtWidgets.QPushButton("Click me!")
        self.text = QtWidgets.QLabel("Hello World",
                                     alignment=QtCore.Qt.AlignCenter)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)

        self.button.clicked.connect(self.magic)

    @QtCore.Slot()
    def magic(self):
        self.text.setText(random.choice(self.hello))

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = CameraApp()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())