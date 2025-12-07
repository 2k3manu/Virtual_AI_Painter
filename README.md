# Artificial Intelligence Virtual Painter

A real-time virtual painter application that uses computer vision to track hand gestures for painting on a virtual canvas. Built using Python, OpenCV, and MediaPipe.

## Features

- **Real-time Hand Tracking**: Uses MediaPipe to track hand landmarks.
- **Gesture Control**:
  - **Draw**: OK Sign (Pinch).
  - **Select**: Peace Sign (Select colors/shapes/buttons).
  - **Resize**: L-Sign (Adjust brush size dynamically).
  - **Clear**: Three Fingers Up (or "Clear" button).
  - **Erase**: Index Finger Pointing.
  - **Eraser Size**: Rock Sign.
- **Virtual Tools**: Brush, Eraser, Shapes (Rectangle, Circle, Triangle).
- **New Features**:
  - **Save Artwork**: Save your creation to `Gallery/` folder.
  - **Undo**: Undo your last stroke.
  - **Dynamic Sizing**: Visual gesture-based resizing.

## How to run

1. Install dependencies: `pip install -r requirements.txt`
2. Run the application: `python main.py`

### Windows (Easy Run)

Double-click `run_on_windows.bat`. It will automatically create an isolated environment, install dependencies, and launch the app.

3. **Controls**:
   - **Colors/Shapes**: Use Peace Sign, hover over the header to select.
   - **Buttons**: Use Peace Sign, hover over Save/Undo/Clear in the top right.
   - **Draw**: Use OK Sign to paint.
4. Press `ESC` to exit.

## Future enhancements

- Add more brush types (Texture brushes)
- Add "Redo" functionality
- Augmented reality 3D drawing
