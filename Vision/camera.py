import cv2
import numpy as np
from picamera2 import Picamera2 # type: ignore
import time

class Camera:
    DIAGONAL_FOV = 62
    # HORZONTAL_FOV = 55.28168977
    # VERTICAL_FOV = 32.82769798

    HORZONTAL_FOV = 51.0
    VERTICAL_FOV = 39.6

    # HORZONTAL_RES = 1280
    # VERTICAL_RES = 720

    HORZONTAL_RES = 640
    VERTICAL_RES = 480

    FPS = 30 * 2
    
    def __init__(self, index):
        print(f"Initializing camera at index {index}...")
        self.camera = Picamera2(index)
        self.camera.configure(self.camera.create_video_configuration(main={"size": (self.HORZONTAL_RES, self.VERTICAL_RES)}))
        self.camera.start()
        # self.camera.set_controls({"ExposureTime": 5000}) 
        time.sleep(0.1) # warmup

    def get_frame(self):
        frame_rgb = self.camera.capture_array()

        if frame_rgb is None:
            return None

        frame_flipped = cv2.flip(frame_rgb, -1) 
        
        frame_bgr = cv2.cvtColor(frame_flipped, cv2.COLOR_RGB2BGR)
        
        # BGR -> HSV
        frame_hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
        
        return frame_hsv
    
    def stop(self):
        print("Stopping camera...")
        self.camera.stop()


if __name__ == "__main__":
    camera = Camera(0)
    while True:
        frame_hsv = camera.get_frame()
        if frame_hsv is not None:
            frame_display_bgr = cv2.cvtColor(frame_hsv, cv2.COLOR_HSV2BGR)
            
            height, width = frame_display_bgr.shape[:2]
            center_x = width // 2
            center_y = height // 2
            
            center_pixel_hsv = frame_hsv[center_y, center_x]
            print(f"Center pixel HSV: {center_pixel_hsv}")
            
            crosshair_size = 25
            crosshair_color = (0, 255, 0)
            crosshair_thickness = 4
            
            cv2.line(frame_display_bgr, 
                    (center_x - crosshair_size, center_y),
                    (center_x + crosshair_size, center_y),
                    crosshair_color, crosshair_thickness)
            
            cv2.line(frame_display_bgr,
                    (center_x, center_y - crosshair_size),
                    (center_x, center_y + crosshair_size),
                    crosshair_color, crosshair_thickness)
            
            cv2.imshow("HSV Feed (Displayed as BGR)", frame_display_bgr)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    camera.stop()
    cv2.destroyAllWindows()