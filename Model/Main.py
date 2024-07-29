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

# Load pre-trained hand detection model
protoFile = "pose_deploy.prototxt"
weightsFile = "pose_iter_102000.caffemodel"
net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)

# Create a window to display the volume slider
cv2.namedWindow('Volume Control')
cv2.createTrackbar('Volume', 'Volume Control', 0, 100, lambda x: None)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame horizontally for a later selfie-view display
    frame = cv2.flip(frame, 1)

    # Resize frame for faster processing
    height, width = frame.shape[:2]
    aspect_ratio = width / height
    target_height = 360
    target_width = int(target_height * aspect_ratio)
    frame_resized = cv2.resize(frame, (target_width, target_height))

    # Convert frame to grayscale
    gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)

    # Detect hand landmarks
    blob = cv2.dnn.blobFromImage(gray, 1.0 / 255, (368, 368), (0, 0, 0), swapRB=False, crop=False)
    net.setInput(blob)
    output = net.forward()

    # Extract landmarks corresponding to index finger and thumb
    landmarks = []
    for i in range(output.shape[1]):
        x = int(output[0, i, 0] * width)
        y = int(output[0, i, 1] * height)
        landmarks.append((x, y))

    # Calculate distance between index finger and thumb
    index_finger = landmarks[8]
    thumb = landmarks[4]
    distance = np.linalg.norm(np.array(index_finger) - np.array(thumb))

    # Map distance to volume level (adjust as needed)
    max_distance = 300
    min_distance = 20
    volume_level = (distance - min_distance) / (max_distance - min_distance)
    volume_level = np.clip(volume_level, 0, 1)

    # Change system volume based on distance
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






