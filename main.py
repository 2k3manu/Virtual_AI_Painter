import cv2
import numpy as np
from HandTrackingModule import HandDetector
from GestureRecognition import *
import os
import datetime

folderPath = "Header"
# Load header images if they exist, otherwise we draw them manually
# For this task, we will draw them manually as we don't have the assets.

undo_stack = []
redo_stack = []
MAX_HISTORY = 10

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
# UI Button Areas (Top Right)
# We will define them dynamically inside the loop based on frame width


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

        # Save state for Undo before drawing a new stroke
        if mode == 'draw' and not drawing and fingers[1] == 1 and fingers[2] == 0:
             # Only save if we are about to start drawing (index up, others down is typical draw, but we check drawing flag later)
             # Actually, best to save when 'drawing' flips from False to True
             pass

        x1, y1 = lmList[8][1], lmList[8][2]
        
        # Dynamic Resize (L-Sign)
        if mode == 'resize':
             thumb = lmList[4][1], lmList[4][2]
             index = lmList[8][1], lmList[8][2]
             length = math.hypot(index[0]-thumb[0], index[1]-thumb[1])
             # Map length 20-200 to 5-100
             brushThickness = int(np.interp(length, [20, 200], [5, 50]))
             eraserSize = int(np.interp(length, [20, 200], [20, 100]))
             # Visual indicator
             cv2.circle(frame, (x1, y1), brushThickness//2, brushColor, cv2.FILLED)
             cv2.putText(frame, f"Size: {brushThickness}", (x1+20, y1), cv2.FONT_HERSHEY_PLAIN, 1, (255,255,255), 1)

        # UI Interaction (Selection)
        if mode == 'select':
            # Colors and Shapes (Left Side)
            if y1 < 70:
                # ... existing color selection ...
                for i in range(len(colors)):
                    if (x1 > x_start + i*70) and (x1 < x_start + (i+1)*70 - 10):
                        brushColor = colors[i]
                        if brushColor == (0,0,0):
                            mode = 'erase'
                        else:
                            mode = 'draw'
                        selected_shape = 'freestyle'
                        xp, yp = 0, 0
            
            # Buttons (Right Side)
            # Assuming 640 width, let's put them at the end.
            w = frame.shape[1]
            # Clear (w-250 to w-170), Undo (w-160 to w-80), Save (w-70 to w)
            # Adjustable widths
            btn_w = 80
            
            if y1 < 70:
                # Clear
                if w - 3*btn_w < x1 < w - 2*btn_w:
                    canvas = np.zeros_like(frame) 
                    undo_stack = [] # Clear history on clear? Or save clear as a state? 
                    # Let's save the clear as a state so we can undo it.
                    # Wait, if we clear, we lose previous state. 
                    # Better: Push current to undo before clearing.
                    # But if we are in select mode, we are not drawing.
                    # Let's make "Clear" push to stack first.
                    if len(undo_stack) > 0 and not np.array_equal(undo_stack[-1], canvas):
                        undo_stack.append(canvas.copy())
                    canvas = np.zeros_like(frame)

                # Undo
                elif w - 2*btn_w < x1 < w - btn_w:
                    if len(undo_stack) > 0:
                        canvas = undo_stack.pop()
                    # Add delay to prevent rapid undo
                    cv2.waitKey(200)

                # Save
                elif w - btn_w < x1 < w:
                    # Save Image
                    if not os.path.exists("Gallery"):
                        os.makedirs("Gallery")
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    # Merge canvas and frame for the result
                    imgGray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
                    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
                    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
                    imgFinal = cv2.bitwise_and(frame, imgInv)
                    imgFinal = cv2.bitwise_or(imgFinal, canvas)
                    
                    filename = f"Gallery/Art_{timestamp}.jpg"
                    cv2.imwrite(filename, imgFinal)
                    cv2.putText(frame, "Saved!", (x1-50, y1+50), cv2.FONT_HERSHEY_PLAIN, 2, (0,255,0), 2)
                    cv2.waitKey(500)

            elif 120 < y1 < 160:
                for i in range(len(shapes)):
                    if (x1 > x_start + i*70) and (x1 < x_start + (i+1)*70 - 10):
                        selected_shape = shapes[i]
                        mode = 'draw'
                        xp, yp = 0, 0

        if mode == 'draw':
            if selected_shape == 'freestyle':
                # Undo State Save
                if not drawing: # Just started drawing
                     undo_stack.append(canvas.copy())
                     if len(undo_stack) > MAX_HISTORY:
                         undo_stack.pop(0)
                     drawing = True # Set flag

                cv2.circle(frame, (x1, y1), brushThickness, brushColor, cv2.FILLED)
                if xp == 0 and yp == 0:
                    xp, yp = x1, y1
                cv2.line(canvas, (xp, yp), (x1, y1), brushColor, brushThickness)
                xp, yp = x1, y1
                # drawing = False # Removing this, we handle drawing state with fingers
                if fingers[1] == 0: # Index up is draw, but if index goes down or other fingers change?
                    # Wait, logic is: Drawing if Index is UP. 
                    # If Index is NOT UP, we stop drawing.
                    drawing = False
                    xp, yp = 0, 0

            else:
                if not drawing:
                    undo_stack.append(canvas.copy()) # Save before shape
                    if len(undo_stack) > MAX_HISTORY:
                        undo_stack.pop(0)
                    start_point = (x1, y1)
                    drawing = True
                else:
                    temp = canvas.copy()
                    draw_shape(temp, selected_shape, start_point, (x1, y1), brushColor, brushThickness)
                    frame = cv2.addWeighted(frame, 0.5, temp, 0.5, 0)
                if fingers[1] == 0:  # finger lifted or other interaction
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

    # Draw Top Right Buttons
    w = frame.shape[1]
    btn_w = 80
    
    # Check if mouse/hand is in area to highlight
    # (Simplified: just draw static for now, highlight logic is in 'select' mode block)
    
    # Clear Button
    cv2.rectangle(frame, (w - 3*btn_w, 0), (w - 2*btn_w - 5, 70), (50, 50, 50), cv2.FILLED)
    cv2.putText(frame, "Clear", (w - 3*btn_w + 10, 45), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 2)

    # Undo Button
    cv2.rectangle(frame, (w - 2*btn_w, 0), (w - btn_w - 5, 70), (50, 50, 50), cv2.FILLED)
    cv2.putText(frame, "Undo", (w - 2*btn_w + 15, 45), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 2)

    # Save Button
    cv2.rectangle(frame, (w - btn_w, 0), (w - 5, 70), (50, 50, 50), cv2.FILLED)
    cv2.putText(frame, "Save", (w - btn_w + 15, 45), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 2)


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
