import cv2
import threading
from gaze_tracking import GazeTracking
from talk import iniciar_interface_talk  # Isso assume que talk.py está na mesma pasta

gaze = GazeTracking()
webcam = cv2.VideoCapture(0)
threading.Thread(target=iniciar_interface_talk, daemon=True).start()

while True:
    try:
        _, frame = webcam.read()
        gaze.refresh(frame)
        frame = gaze.annotated_frame()
        text = ""

        if gaze.is_blinking():
            text = "Blinking"
        elif gaze.is_right():
            text = "Right"
        elif gaze.is_left():
            text = "Left"
        elif gaze.is_center():
            text = "Center"
        else:
            text = "Missing"

        cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

        left_pupil = gaze.pupil_left_coords()
        right_pupil = gaze.pupil_right_coords()

        cv2.putText(frame, "Left pupil:  " + str(left_pupil), (90, 130),
                    cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
        cv2.putText(frame, "Right pupil: " + str(right_pupil), (90, 165),
                    cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)

        cv2.imshow("Gaze Tracking", frame)

        if cv2.waitKey(1) == 27:  # ESC
            break
    except KeyboardInterrupt:
        print("Exiting...")
        break

webcam.release()
cv2.destroyAllWindows()
