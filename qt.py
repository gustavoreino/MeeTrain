import sys
import random
import cv2
from gaze_tracking import GazeTracking
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QTextEdit
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QTimer

left_counter = 0

right_counter = 0

center_counter = 0

class Result(QWidget):
    def __init__(self):
        super().__init__()
        global center_counter
        global left_counter
        global right_counter
        if center_counter < left_counter & right_counter < left_counter :
            self.label_eye = QLabel("Tá olhando muito para a esquerda")
        elif center_counter < right_counter & left_counter < right_counter:
            self.label_eye = QLabel("Tá olhando muito para a direita")
        else:
            self.label_eye = QLabel("Você está focando bem no centro")
        #self.label_eye = QLabel(str(center_counter))
        self.label_resposta = QLabel("ChatGPT sugeriu:")
        self.texto_resposta = QTextEdit()
        self.texto_resposta.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.label_eye)
        layout.addWidget(self.label_resposta)
        layout.addWidget(self.texto_resposta)
        self.setLayout(layout)

class CameraApp(QWidget):

    def __init__(self):

        super().__init__()
        self.setWindowTitle("Camera Feed")
        self.image_label = QLabel()
        self.image_label.setFixedSize(640, 480)
        self.status_label = QLabel("Waiting for gaze...")
        self.status_label.setAlignment(QtCore.Qt.AlignTop)
        self.label_entrada = QLabel("Transcrição:")
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.image_label)
        layout.addWidget(self.label_entrada)
        layout.addWidget(self.text_display)
        self.setLayout(layout)

        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        self.gaze = GazeTracking()

        layout.addWidget(self.status_label)
        self.button = QtWidgets.QPushButton("Finish")
        self.button.clicked.connect(self.open_results_window)
        layout.addWidget(self.button, alignment=QtCore.Qt.AlignBottom)

        # Create a timer to grab frames
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # in milliseconds (~33ms ≈ 30 FPS)
        self.result_window = None
        self.counter = 0

    def update_frame(self):

        self.text_display.setText("")
        
        ret, frame = self.cap.read()
        if not ret:
            return

        # Always refresh gaze with the ORIGINAL frame (in BGR!)
        self.gaze.refresh(frame)

        # Get the annotated frame (still in BGR)
        annotated_frame = self.gaze.annotated_frame()

        # Draw additional pupil coordinates
        # left_pupil = self.gaze.pupil_left_coords()
        # right_pupil = self.gaze.pupil_right_coords()
        # cv2.putText(annotated_frame, "Left pupil:  " + str(left_pupil), (90, 130),
        #             cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
        # cv2.putText(annotated_frame, "Right pupil: " + str(right_pupil), (90, 165),
        #             cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)

        # Determine gaze direction
        if self.gaze.is_blinking():
            message = "Blinking"
        elif self.gaze.is_right():
            global right_counter
            right_counter += 1;
            message = "Right"
        elif self.gaze.is_left():
            global left_counter
            left_counter += 1;
            message = "Left"
        elif self.gaze.is_center():
            global center_counter
            center_counter += 1;
            message = "Center"
        else:
            message = "Missing"
        #self.status_label.setText(message)

        # Convert BGR to RGB for Qt display
        rgb_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(qt_image))

    def open_results_window(self):
        if self.result_window is None:
            self.result_window = Result()
        self.result_window.show()
        self.hide()

    def closeEvent(self, event):
        self.cap.release()

class FirstWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.button = QtWidgets.QPushButton("Record")
        self.button.clicked.connect(self.open_recording_window)

        self.layout = QtWidgets.QVBoxLayout(self)
        
        self.layout.addWidget(self.button, alignment=QtCore.Qt.AlignCenter)

        self.recording_window = CameraApp()

    def open_recording_window(self):
        self.recording_window.show()
        self.hide()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = FirstWindow()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())