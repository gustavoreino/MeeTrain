from PyQt6.QtWidgets import (
    QMainWindow, 
    QApplication, 
    QPushButton, 
    QVBoxLayout, 
    QWidget)

import threading

import sys

import cv2
from gaze_tracking import GazeTracking

gaze = GazeTracking()
webcam = cv2.VideoCapture(0)

class MainWindow(QMainWindow):

    def WebcamFrame():
        while True:
        # We get a new frame from the webcam
        _, frame = webcam.read()

        # We send this frame to GazeTracking to analyze it
        gaze.refresh(frame)

        frame = gaze.annotated_frame()
        text = ""

        if gaze.is_blinking():
            text = "Pisca"
        elif gaze.is_right():
            text = "Pare de olhar pra direita"
        elif gaze.is_left():
            text = "Pare de olhar pra direita"
        elif gaze.is_center():
            text = "Tá certo"
        else:
            text = "OLHA DIREITO IDIOTA"

        cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

        left_pupil = gaze.pupil_left_coords()
        right_pupil = gaze.pupil_right_coords()
        cv2.putText(frame, "Left pupil:  " + str(left_pupil), (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
        cv2.putText(frame, "Right pupil: " + str(right_pupil), (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)

        cv2.imshow("Demo", frame)

        if cv2.waitKey(1) == 27:
            break

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Eye Train")

        button = QPushButton("Start")
        button.pressed.connect(self.close)

        layout = QVBoxLayout()
        widgets = [
            button,
        ]

        for w in widgets:
            layout.addWidget(w)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)
        self.show()


app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()