import cv2
from cvzone.HandTrackingModule import HandDetector

detector = HandDetector(detectionCon=0.7, maxHands=1)

def detect_fingers(img):
    hands, img = detector.findHands(img)
    if hands:
        fingers = detector.fingersUp(hands[0])
        return fingers, img
    return None, img