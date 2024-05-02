from piosdk import Pioneer
import cv2
import time
import numpy as np

drone = Pioneer(method=2, pioneer_ip="127.0.0.1", pioneer_mavlink_port=8000, logger=False)
qr_code_detector = cv2.QRCodeDetector()
cam = cv2.VideoCapture(0)

def detect_qr(wait_time=60):
    global cam, qr_code_detector
    decode_start_time = time.time()
    while True:
        if time.time() - decode_start_time > float(wait_time):
            return None
        status, frame = cam.read()
        if np.sum(frame) == 0:
            continue
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            string, _, _ = qr_code_detector.detectAndDecode(gray)
            if (string is not None) and (string != ''):
                return string
        except:
            continue
