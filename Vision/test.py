HORIZONTAL_FOV = 55.28168977
VERTICAL_FOV = 32.82769798

HOROZONTAL_RES = 1920
VERTICAL_RES = 1080

SEPERATION_DISTANCE = 99

import cv2

# Attempt to open the first camera
cap1 = cv2.VideoCapture(0) # 0 is usually the default built-in camera
# Attempt to open the second camera
cap2 = cv2.VideoCapture(1) # 1 is often the next available camera

if not cap1.isOpened():
    print("Error: Could not open camera 1.")
    exit()

if not cap2.isOpened():
    print("Error: Could not open camera 2.")
    exit()

# Set common properties (optional, but good for consistency if cameras support it)
# You might need to adjust these resolutions based on your cameras' capabilities
cap1.set(cv2.CAP_PROP_FRAME_WIDTH, HOROZONTAL_RES)
cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, VERTICAL_RES)
cap2.set(cv2.CAP_PROP_FRAME_WIDTH, HOROZONTAL_RES)
cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, VERTICAL_RES)


while True:
    # Capture frame-by-frame from the first camera
    ret1, frame1 = cap1.read()
    # Capture frame-by-frame from the second camera
    ret2, frame2 = cap2.read()

    if not ret1:
        print("Error: Can't receive frame from camera 1. Exiting ...")
        break
    if not ret2:
        print("Error: Can't receive frame from camera 2. Exiting ...")
        break

    # Display the resulting frames
    cv2.imshow('Camera 1 Feed', frame1)
    cv2.imshow('Camera 2 Feed', frame2)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture and destroy windows
cap1.release()
cap2.release()
cv2.destroyAllWindows()

