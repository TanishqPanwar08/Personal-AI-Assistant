import cv2
import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Function to change volume
def change_volume(volume_level):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMasterVolumeLevelScalar(volume_level, None)

# Initialize video capture
cap = cv2.VideoCapture(0)

# Create a window to display the volume slider
cv2.namedWindow('Volume Control')
cv2.createTrackbar('Volume', 'Volume Control', 0, 100, lambda x: None)

# Initialize volume_level
volume_level = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame horizontally for a later selfie-view display
    frame = cv2.flip(frame, 1)

    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define range of skin color in HSV
    lower_skin = np.array([0, 20, 70], dtype=np.uint8)
    upper_skin = np.array([20, 255, 255], dtype=np.uint8)

    # Threshold the HSV image to get only skin color
    mask = cv2.inRange(hsv, lower_skin, upper_skin)

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find the largest contour (the hand)
    if contours:
        hand_contour = max(contours, key=cv2.contourArea)

        # Find the centroid of the hand
        M = cv2.moments(hand_contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            # Draw a circle at the centroid of the hand
            cv2.circle(frame, (cx, cy), 10, (0, 255, 255), -1)

            # Change volume based on the vertical position of the hand
            volume_level = 1 - (cy / frame.shape[0])
            change_volume(volume_level)

    # Update the position of the slider based on the current volume level
    volume = int(volume_level * 100)
    cv2.setTrackbarPos('Volume', 'Volume Control', volume)

    # Display the resulting frame
    cv2.imshow('Hand Gesture Volume Control', frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and destroy all windows
cap.release()
cv2.destroyAllWindows()
