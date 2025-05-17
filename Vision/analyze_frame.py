import cv2
import numpy as np

TARGET_HSV = np.array([110, 200, 90])
Hue_TOLERANCE = 30
Saturation_TOLERANCE = 45
Value_TOLERANCE = 25

def get_target_masks(frame_hsv: np.ndarray):
    h, s, v = cv2.split(frame_hsv)

    target_h, target_s, target_v = TARGET_HSV[0], TARGET_HSV[1], TARGET_HSV[2]
    
    h_low = int((target_h - Hue_TOLERANCE + 180) % 180)
    h_high = int((target_h + Hue_TOLERANCE + 180) % 180)

    if h_low <= h_high:
        mask_h = cv2.inRange(h, h_low, h_high)
    else: 
        mask_h1 = cv2.inRange(h, h_low, 179) 
        mask_h2 = cv2.inRange(h, 0, h_high)
        mask_h = cv2.bitwise_or(mask_h1, mask_h2)

    s_low = int(np.clip(target_s - Saturation_TOLERANCE, 0, 255))
    s_high = int(np.clip(target_s + Saturation_TOLERANCE, 0, 255))
    mask_s = cv2.inRange(s, s_low, s_high)

    v_low = int(np.clip(target_v - Value_TOLERANCE, 0, 255))
    v_high = int(np.clip(target_v + Value_TOLERANCE, 0, 255))
    mask_v = cv2.inRange(v, v_low, v_high)

    return mask_h, mask_s, mask_v

def get_targets(frame_hsv: np.ndarray) -> list[tuple[tuple[int, int], int]]:
    mask_h, mask_s, mask_v = get_target_masks(frame_hsv)
    target_mask = cv2.bitwise_and(mask_h, cv2.bitwise_and(mask_s, mask_v))

    contours, _ = cv2.findContours(target_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    found_targets = []
    min_contour_area = 50

    for contour in contours:
        area = cv2.contourArea(contour)
        if area > min_contour_area:
            (x, y), radius = cv2.minEnclosingCircle(contour)
            center = (int(x), int(y))
            radius = int(radius)
            if radius > 5: # Only consider circles with a reasonable radius
                found_targets.append((center, radius))
    return found_targets

if __name__ == "__main__":
    from camera import Camera
    camera = Camera(0)
    
    cv2.namedWindow("All Masks", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("All Masks", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    print("Starting frame analysis loop...")
    first_run = True
    all_masks_display = None

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    font_color = (0, 255, 0) 
    line_type = 1
    text_offset_x = 5
    text_offset_y = 15

    while True:
        frame_hsv = camera.get_frame()

        if frame_hsv is None:
            print("Error: Failed to get frame from camera.")
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            continue

        targets = get_targets(frame_hsv)
        
        frame_display_bgr = cv2.cvtColor(frame_hsv, cv2.COLOR_HSV2BGR)

        if targets:
            print(f"Target(s) DETECTED: {len(targets)} found")
            for center, radius in targets:
                # circle green
                cv2.circle(frame_display_bgr, center, radius, (0, 255, 0), 2)
                cv2.circle(frame_display_bgr, center, 2, (0, 0, 255), 3)
        
        cv2.imshow("Live Feed (HSV input, BGR display)", frame_display_bgr)
        
        mask_h_display, mask_s_display, mask_v_display = get_target_masks(frame_hsv)
        final_mask_display = cv2.bitwise_and(mask_h_display, cv2.bitwise_and(mask_s_display, mask_v_display))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    print("Exiting...")
    camera.stop()
    cv2.destroyAllWindows()