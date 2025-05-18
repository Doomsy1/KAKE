import cv2
import numpy as np
from picamera2 import Picamera2
import time
# P5V04A

HORIZONTAL_FOV = 55.28168977
VERTICAL_FOV = 32.82769798

HOROZONTAL_RES = 1920 // 4
VERTICAL_RES = 1080 // 4

FPS = 30

LEFT_CAMERA_INDEX = 0
RIGHT_CAMERA_INDEX = 1
SEPERATION_DISTANCE = 99

print("Available cameras:")
cameras = Picamera2.global_camera_info()
if not cameras:
    print("No cameras found by Picamera2.")
else:
    for i, cam_info in enumerate(cameras):
        print(f"Camera {i}: {cam_info}")

if len(cameras) < 2:
    print(f"Error: Expected 2 cameras, but only found {len(cameras)}.")

# Camera 0
print(f"Attempting to initialize camera at index {LEFT_CAMERA_INDEX}...")
picam2_0 = Picamera2(LEFT_CAMERA_INDEX)
config0 = picam2_0.create_preview_configuration(main={"size": (HOROZONTAL_RES, VERTICAL_RES)})
picam2_0.configure(config0)
picam2_0.start()
print(f"Camera at index {LEFT_CAMERA_INDEX} initialized.")

# Camera 1
picam2_1 = None
if len(cameras) > RIGHT_CAMERA_INDEX:
    print(f"Attempting to initialize camera at index {RIGHT_CAMERA_INDEX}...")
    picam2_1 = Picamera2(RIGHT_CAMERA_INDEX)
    config1 = picam2_1.create_preview_configuration(main={"size": (HOROZONTAL_RES, VERTICAL_RES)})
    picam2_1.configure(config1)
    picam2_1.start()
    print(f"Camera at index {RIGHT_CAMERA_INDEX} initialized.")
else:
    print(f"Skipping initialization of camera at index {RIGHT_CAMERA_INDEX}")

# warmup
time.sleep(1)

try:
    while True:
        frame0_rgb = picam2_0.capture_array()
        if frame0_rgb is not None:
            frame0_flipped = cv2.flip(frame0_rgb, -1)
            frame0_bgr = cv2.cvtColor(frame0_flipped, cv2.COLOR_RGB2BGR)
            frame0_hsv = cv2.cvtColor(frame0_bgr, cv2.COLOR_BGR2HSV)
            frame0_display_bgr = cv2.cvtColor(frame0_hsv, cv2.COLOR_HSV2BGR)
            cv2.imshow('PiCamera Feed 0 (HSV input, BGR display)', frame0_display_bgr)

        if picam2_1:
            frame1_rgb = picam2_1.capture_array()
            if frame1_rgb is not None:
                frame1_flipped = cv2.flip(frame1_rgb, -1)
                frame1_bgr = cv2.cvtColor(frame1_flipped, cv2.COLOR_RGB2BGR)
                frame1_hsv = cv2.cvtColor(frame1_bgr, cv2.COLOR_BGR2HSV)
                frame1_display_bgr = cv2.cvtColor(frame1_hsv, cv2.COLOR_HSV2BGR)
                cv2.imshow('PiCamera Feed 1 (HSV input, BGR display)', frame1_display_bgr)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    print("Stopping cameras...")
    picam2_0.stop()
    if picam2_1:
        picam2_1.stop()
    cv2.destroyAllWindows()
    print("Cameras stopped and windows closed.")
