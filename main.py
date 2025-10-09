import cv2
import numpy as np
from HandTrackingModule import HandDetector
from GestureRecognition import *

brushColor = (255, 0, 255)
brushThickness = 15
eraserSize = 50

cap = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.8)
xp, yp = 0, 0
canvas = None
mode = 'draw'
selected_shape = 'freestyle'
drawing = False
start_point = None

colors = [(255, 0, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 0, 0)]
shapes = ['rectangle', 'circle', 'triangle']

x_start = 10

def draw_shape(img, shape, start, end, color, thickness):
    if shape == 'rectangle':
        cv2.rectangle(img, start, end, color, thickness)
    elif shape == 'circle':
        center = ((start[0] + end[0]) // 2, (start[1] + end[1]) // 2)
        radius = int(np.hypot(end[0] - start[0], end[1] - start[1]) / 2)
        cv2.circle(img, center, radius, color, thickness)
    elif shape == 'triangle':
        pt1 = start
        pt2 = (end[0], start[1])
        pt3 = ((start[0] + end[0]) // 2, end[1])
        pts = np.array([pt1, pt2, pt3], np.int32)
        cv2.polylines(img, [pts], isClosed=True, color=color, thickness=thickness)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)

    if canvas is None:
        canvas = np.zeros_like(frame)

    frame = detector.findHands(frame)
    lmList = detector.findPosition(frame, draw=False)
    fingers = detector.fingersUp()

    if lmList:
        if is_ok_sign(lmList):
            mode = 'draw'
            selected_shape = 'freestyle'
        elif is_peace_sign(fingers):
            mode = 'select'
        elif is_l_sign(fingers, lmList):
            mode = 'resize'
        elif is_three_fingers(fingers):
            canvas = np.zeros_like(frame)
        elif is_index_only(fingers):
            mode = 'erase'
        elif is_rock_sign(fingers):
            eraserSize += 5
            if eraserSize > 200:
                eraserSize = 50

        x1, y1 = lmList[8][1], lmList[8][2]

        if mode == 'select':
            if y1 < 70:
                for i in range(len(colors)):
                    if (x1 > x_start + i*70) and (x1 < x_start + (i+1)*70 - 10):
                        brushColor = colors[i]
                        if brushColor == (0,0,0):
                            mode = 'erase'
                        else:
                            mode = 'draw'
                        selected_shape = 'freestyle'
                        xp, yp = 0, 0
            elif 120 < y1 < 160:
                for i in range(len(shapes)):
                    if (x1 > x_start + i*70) and (x1 < x_start + (i+1)*70 - 10):
                        selected_shape = shapes[i]
                        mode = 'draw'
                        xp, yp = 0, 0

        if mode == 'draw':
            if selected_shape == 'freestyle':
                cv2.circle(frame, (x1, y1), brushThickness, brushColor, cv2.FILLED)
                if xp == 0 and yp == 0:
                    xp, yp = x1, y1
                cv2.line(canvas, (xp, yp), (x1, y1), brushColor, brushThickness)
                xp, yp = x1, y1
                drawing = False
            else:
                if not drawing:
                    start_point = (x1, y1)
                    drawing = True
                else:
                    temp = canvas.copy()
                    draw_shape(temp, selected_shape, start_point, (x1, y1), brushColor, brushThickness)
                    frame = cv2.addWeighted(frame, 0.5, temp, 0.5, 0)
                if fingers[0] == 0:  # finger lifted
                    draw_shape(canvas, selected_shape, start_point, (x1, y1), brushColor, brushThickness)
                    drawing = False
                    start_point = None
                    xp, yp = 0, 0

        elif mode == 'erase':
            cv2.circle(frame, (x1, y1), eraserSize, (0, 0, 0), cv2.FILLED)
            if xp == 0 and yp == 0:
                xp, yp = x1, y1
            cv2.line(canvas, (xp, yp), (x1, y1), (0, 0, 0), eraserSize)
            xp, yp = x1, y1

        elif mode == 'resize':
            xp, yp = 0, 0
    else:
        xp, yp = 0, 0
        drawing = False
        start_point = None

    imgGray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
    frame = cv2.bitwise_and(frame, imgInv)
    frame = cv2.bitwise_or(frame, canvas)

    for i, color in enumerate(colors):
        cv2.rectangle(frame, (x_start + i*70, 0), (x_start + (i+1)*70 - 10, 70), color, cv2.FILLED)
        if color == brushColor and mode != 'erase':
            cv2.rectangle(frame, (x_start + i*70, 0), (x_start + (i+1)*70 - 10, 70), (255, 255, 255), 3)

    for i, shape in enumerate(shapes):
        cv2.rectangle(frame, (x_start + i*70, 120), (x_start + (i+1)*70 - 10, 160), (50, 50, 50), cv2.FILLED)
        cv2.putText(frame, shape.title(), (x_start + i*70 + 5, 145), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        if selected_shape == shape and mode == 'draw':
            cv2.rectangle(frame, (x_start + i*70, 120), (x_start + (i+1)*70 - 10, 160), (255, 255, 255), 3)

    cv2.putText(frame, f'Mode: {mode}', (10, 460), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("Virtual Painter", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

    if cv2.getWindowProperty("Virtual Painter", cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
cv2.destroyAllWindows()
