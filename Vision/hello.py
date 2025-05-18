# Artificial Intelligence was used in this file to : debug errors, and verify FOV calculations

from logging import PlaceHolder
import math
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from camera import Camera
from analyze_frame import get_targets, LOW_TARGET_HSV_CONFIGS, UPPER_TARGET_HSV_CONFIGS

def getAngle(cameranum: int) -> tuple[float, float]:
    # get the angles from the camera
    # cameranum = 0 or 1
    # return the angles in degrees
    # XZangle = horizontal angle between the x and z axis
    # YZangle = vertical angle between the y and z axis

    if cameranum == 0:
        XZangle = 10.8
        YZangle = 10
    elif cameranum == 1:
        XZangle = -11.1
        YZangle = 10

    return XZangle, YZangle 

class BallDetector:
    # this class is used to detect the ball in the camera
    # it will take the angles from the camera and return the 3D coordinates of the ball
    # it will also check if the ball is on the screen or not
    HORIZONTAL_FOV = 55.28168977
    VERTICAL_FOV = 32.82769798

    SEPERATION_DISTANCE = 10 # cm

    SCREEN_RANGE = 30


    def __init__(self, left_camera: Camera, right_camera: Camera):

        self.left_camera = left_camera
        self.right_camera = right_camera

        self.HORIZONTAL_RESOLUTION = self.left_camera.HORZONTAL_RES
        self.VERTICAL_RESOLUTION = self.left_camera.VERTICAL_RES

    def getAngle(self, pixel_x: int, pixel_y: int) -> tuple[float, float]:
        # get the angle from the camera
        # pixel_x = x coordinate of the target
        # pixel_y = y coordinate of the target
        # return the angle in degrees
        # XZangle = horizontal angle between the x and z axis
        # YZangle = vertical angle between the y and z axis

        yaw = self.HORIZONTAL_FOV * (pixel_x / self.HORIZONTAL_RESOLUTION) - self.HORIZONTAL_FOV / 2
        pitch = self.VERTICAL_FOV * (pixel_y / self.VERTICAL_RESOLUTION) - self.VERTICAL_FOV / 2
        return yaw, pitch

    def findPosition(self, XZangle1: float, YZangle1: float, XZangle2: float, YZangle2: float) -> tuple[float, float, float] | None:
        # take angles from two cameras and return the 3D coordinates of the object
        # XZangle1 = horizontal angle between the x and z axis of camera 1
        # YZangle1 = vertical angle between the y and z axis of camera 1
        # XZangle2 = horizontal angle between the x and z axis of camera 2
        # YZangle2 = vertical angle between the y and z axis of camera 2

        a = 90 - XZangle1
        b = 90 + XZangle2
        c = 180 - (a + b)
        d = (YZangle1 + YZangle2) / 2

        # Ccheck for potential division by zero or very small sine value
        sin_c_rad = math.sin(math.radians(c))
        if abs(sin_c_rad) < 1e-6:
            print(f"Error in findPosition: Triangulation unstable. Angle c = {c:.2f} degrees (XZangle1 - XZangle2), sin(c) is close to zero.")
            print(f"  XZangle1: {XZangle1:.2f}, XZangle2: {XZangle2:.2f}")
            return None # return None if triangulation is likely to fail

        r1 = self.SEPERATION_DISTANCE * math.sin(math.radians(b)) / sin_c_rad
        r2 = self.SEPERATION_DISTANCE * math.sin(math.radians(a)) / sin_c_rad

        z = r1 * math.sin(math.radians(a))
        x = -(self.SEPERATION_DISTANCE / 2) + r1 * math.cos(math.radians(a))
        y = -z * math.tan(math.radians(d))

        return x, y, z

    def _get_frame_and_targets(self, camera: Camera, low_hsv_config: np.ndarray, upper_hsv_config: np.ndarray):
        frame = camera.get_frame()
        if frame is None:
            print(f"Error: Failed to get frame from camera {camera.camera_id if hasattr(camera, 'camera_id') else 'unknown'}.")
            return None
        targets = get_targets(frame, low_hsv_config, upper_hsv_config)
        if not targets:
            return None
        if len(targets) > 1:
             print(f"Warning: {len(targets)} targets found in camera {camera.camera_id if hasattr(camera, 'camera_id') else 'unknown'}, expected 1. Using the first one.")
        return targets[0][0] # return only the center of the first target cuz idk how to do calculations for more

    def getTarget(self) -> tuple[float, float, float] | None:
        left_targets_center = None
        right_targets_center = None

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_left_processed = executor.submit(self._get_frame_and_targets, self.left_camera, LOW_TARGET_HSV_CONFIGS[0], UPPER_TARGET_HSV_CONFIGS[0])
            future_right_processed = executor.submit(self._get_frame_and_targets, self.right_camera, LOW_TARGET_HSV_CONFIGS[1], UPPER_TARGET_HSV_CONFIGS[1])

            left_targets_center = future_left_processed.result()
            right_targets_center = future_right_processed.result()

        if left_targets_center is None:
            print("Error: Failed to get targets from left camera pipeline.")
            return None
        if right_targets_center is None:
            print("Error: Failed to get targets from right camera pipeline.")
            return None
            
        left_yaw, left_pitch = self.getAngle(left_targets_center[0], left_targets_center[1])
        right_yaw, right_pitch = self.getAngle(right_targets_center[0], right_targets_center[1])
        
        position_3d = self.findPosition(left_yaw, left_pitch, right_yaw, right_pitch)
        
        if position_3d is None:
            print("Error: Failed to determine target 3D position from findPosition.")
            return None
    
        x, y, z = position_3d
        return x, y, z


# def calibrateCamera() -> list[float]:
#     # output [x, y, z, width, height]
#     # x,y = bottom left corner of the camera
#     bottomleft = findPosition()
#     bottomright = findPosition()
#     topleft = findPosition()
#     topright = findPosition()

#     x = (bottomleft[0] + topleft[0]) / 2
#     y = (bottomleft[1] + bottomright[1]) / 2
#     z = (bottomleft[2] + bottomright[2] + topleft[2] + topright[2]) / 4

#     l1 = bottomright[0] - bottomleft[0]
#     l2 = topright[0] - topleft[0]
#     width = (l1 + l2) / 2

#     h1 = bottomright[1] - bottomleft[1]
#     h2 = topright[1] - topleft[1]
#     height = (h1 + h2) / 2

#     return [x, y, z, width, height]


if __name__ == "__main__":
    import time
    left_camera = Camera(0)
    right_camera = Camera(1)
    ball_detector = BallDetector(left_camera, right_camera)
    while True:
        start_time = time.time()
        result = ball_detector.getTarget()
        end_time = time.time()
        fps = 1 / (end_time - start_time)
        # if result is None:
        #     pass
        # elif result[2] > 265:
        #     print(f'FPS: {fps:.2f} | {result}')
        # else:
        #     print("no ball")
        print(f'FPS: {fps:.2f} | {result}')