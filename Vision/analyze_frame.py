import cv2
import numpy as np
import json

CONFIG_FILE_PATH = "hsv_config.json"

def load_hsv_configs(filepath):
    with open(filepath, 'r') as f:
        configs = json.load(f)

    low_left = np.array(configs["camera_0"]["low_hsv"], dtype=np.uint8)
    upper_left = np.array(configs["camera_0"]["upper_hsv"], dtype=np.uint8)
    low_right = np.array(configs["camera_1"]["low_hsv"], dtype=np.uint8)
    upper_right = np.array(configs["camera_1"]["upper_hsv"], dtype=np.uint8)

    return low_left, upper_left, low_right, upper_right


def save_hsv_configs(filepath, low_hsv_configs_list, upper_hsv_configs_list):
    configs_to_save = {
        "camera_0": {
            "low_hsv": low_hsv_configs_list[0].tolist(),
            "upper_hsv": upper_hsv_configs_list[0].tolist()
        },
        "camera_1": {
            "low_hsv": low_hsv_configs_list[1].tolist(),
            "upper_hsv": upper_hsv_configs_list[1].tolist()
        }
    }
    try:
        with open(filepath, 'w') as f:
            json.dump(configs_to_save, f, indent=4)
        print(f"HSV configurations saved to {filepath}")
    except Exception as e:
        print(f"Error saving HSV configurations to {filepath}: {e}")

LOW_TARGET_HSV_LEFT, UPPER_TARGET_HSV_LEFT, LOW_TARGET_HSV_RIGHT, UPPER_TARGET_HSV_RIGHT = load_hsv_configs(CONFIG_FILE_PATH)

# Camera 0 (Left)
# LOW_TARGET_HSV_LEFT = np.array([98, 195, 59], dtype=np.uint8) # Replaced by loading
# UPPER_TARGET_HSV_LEFT = np.array([114, 255, 113], dtype=np.uint8) # Replaced by loading

# Camera 1 (Right)
# LOW_TARGET_HSV_RIGHT = np.array([107, 185, 62], dtype=np.uint8) # Replaced by loading
# UPPER_TARGET_HSV_RIGHT = np.array([111, 255, 126], dtype=np.uint8) # Replaced by loading

LOW_TARGET_HSV_CONFIGS = [LOW_TARGET_HSV_LEFT, LOW_TARGET_HSV_RIGHT]
UPPER_TARGET_HSV_CONFIGS = [UPPER_TARGET_HSV_LEFT, UPPER_TARGET_HSV_RIGHT]

MIN_CONTOUR_AREA = 80
MIN_RADIUS = 3

def on_trackbar_change(val):
    pass

def create_hsv_trackbars(initial_low_hsv, initial_upper_hsv):
    cv2.namedWindow("HSV Thresholds")
    cv2.createTrackbar("Low H", "HSV Thresholds", initial_low_hsv[0], 179, on_trackbar_change)
    cv2.createTrackbar("High H", "HSV Thresholds", initial_upper_hsv[0], 179, on_trackbar_change)
    cv2.createTrackbar("Low S", "HSV Thresholds", initial_low_hsv[1], 255, on_trackbar_change)
    cv2.createTrackbar("High S", "HSV Thresholds", initial_upper_hsv[1], 255, on_trackbar_change)
    cv2.createTrackbar("Low V", "HSV Thresholds", initial_low_hsv[2], 255, on_trackbar_change)
    cv2.createTrackbar("High V", "HSV Thresholds", initial_upper_hsv[2], 255, on_trackbar_change)

def set_trackbar_positions(low_hsv, high_hsv):
    cv2.setTrackbarPos("Low H", "HSV Thresholds", low_hsv[0])
    cv2.setTrackbarPos("High H", "HSV Thresholds", high_hsv[0])
    cv2.setTrackbarPos("Low S", "HSV Thresholds", low_hsv[1])
    cv2.setTrackbarPos("High S", "HSV Thresholds", high_hsv[1])
    cv2.setTrackbarPos("Low V", "HSV Thresholds", low_hsv[2])
    cv2.setTrackbarPos("High V", "HSV Thresholds", high_hsv[2])

def update_hsv_configs_from_trackbars(camera_idx_to_update):
    global LOW_TARGET_HSV_CONFIGS, UPPER_TARGET_HSV_CONFIGS
    LOW_TARGET_HSV_CONFIGS[camera_idx_to_update][0] = cv2.getTrackbarPos("Low H", "HSV Thresholds")
    UPPER_TARGET_HSV_CONFIGS[camera_idx_to_update][0] = cv2.getTrackbarPos("High H", "HSV Thresholds")
    LOW_TARGET_HSV_CONFIGS[camera_idx_to_update][1] = cv2.getTrackbarPos("Low S", "HSV Thresholds")
    UPPER_TARGET_HSV_CONFIGS[camera_idx_to_update][1] = cv2.getTrackbarPos("High S", "HSV Thresholds")
    LOW_TARGET_HSV_CONFIGS[camera_idx_to_update][2] = cv2.getTrackbarPos("Low V", "HSV Thresholds")
    UPPER_TARGET_HSV_CONFIGS[camera_idx_to_update][2] = cv2.getTrackbarPos("High V", "HSV Thresholds")

def get_target_masks(frame_hsv: np.ndarray, low_hsv_for_mask: np.ndarray, upper_hsv_for_mask: np.ndarray):
    h_channel, s_channel, v_channel = cv2.split(frame_hsv)

    low_h = int(low_hsv_for_mask[0])
    low_s = int(low_hsv_for_mask[1])
    low_v = int(low_hsv_for_mask[2])
    
    high_h = int(upper_hsv_for_mask[0])
    high_s = int(upper_hsv_for_mask[1])
    high_v = int(upper_hsv_for_mask[2])

    # hue mask
    if low_h <= high_h:
        mask_h = cv2.inRange(h_channel, low_h, high_h)
    else: 
        mask_h1 = cv2.inRange(h_channel, low_h, 179)
        mask_h2 = cv2.inRange(h_channel, 0, high_h)
        mask_h = cv2.bitwise_or(mask_h1, mask_h2)

    # saturation mask
    mask_s = cv2.inRange(s_channel, low_s, high_s)

    # value mask
    mask_v = cv2.inRange(v_channel, low_v, high_v)

    return mask_h, mask_s, mask_v

def get_targets(frame_hsv: np.ndarray, low_hsv: np.ndarray, upper_hsv: np.ndarray) -> list[tuple[tuple[int, int], int]]:
    mask_h, mask_s, mask_v = get_target_masks(frame_hsv, low_hsv, upper_hsv)
    # target_mask = cv2.bitwise_and(mask_h, cv2.bitwise_and(mask_s, mask_v))
    # combine masks: a pixel is included if it's in at least two of the H, S, V masks
    h_and_s = cv2.bitwise_and(mask_h, mask_s)
    h_and_v = cv2.bitwise_and(mask_h, mask_v)
    s_and_v = cv2.bitwise_and(mask_s, mask_v)
    
    target_mask = cv2.bitwise_or(h_and_s, cv2.bitwise_or(h_and_v, s_and_v))

    kernel = np.ones((3,3),np.uint8)
    opened_mask = cv2.morphologyEx(target_mask, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(opened_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    found_targets = []
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > MIN_CONTOUR_AREA:
            (x, y), radius = cv2.minEnclosingCircle(contour)
            center = (int(x), int(y))
            radius = int(radius)
            if radius > MIN_RADIUS:
                found_targets.append((center, radius))
    return found_targets

if __name__ == "__main__":
    from camera import Camera

    camera_left = Camera(0)
    camera_right = Camera(1)
    
    cameras = [camera_left, camera_right]
    current_camera_idx = 0
    active_camera_names = ["Left", "Right"]

    show_masks = True
    all_masks_width = 1920
    all_masks_height = 1080
    first_run_masks = True
    all_masks_display = None
    first_run_hsv_trackbars = True

    print("Starting frame analysis loop...")

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    font_color = (0, 255, 0) 
    line_type = 1
    text_offset_x = 5 
    text_offset_y = 15

    while True:
        active_camera = cameras[current_camera_idx]
        active_camera_name_str = active_camera_names[current_camera_idx]
        live_feed_window_name = f"Live Feed {active_camera_name_str}"

        active_low_hsv = LOW_TARGET_HSV_CONFIGS[current_camera_idx]
        active_upper_hsv = UPPER_TARGET_HSV_CONFIGS[current_camera_idx]

        frame_hsv = active_camera.get_frame()

        if frame_hsv is None:
            print(f"Error: Failed to get frame from {active_camera_name_str} camera.")
        else:
            if show_masks:
                if first_run_hsv_trackbars:
                    create_hsv_trackbars(active_low_hsv, active_upper_hsv)
                    first_run_hsv_trackbars = False
                
                update_hsv_configs_from_trackbars(current_camera_idx)
                # refresh active_low_hsv and active_upper_hsv after potential update from trackbars
                active_low_hsv = LOW_TARGET_HSV_CONFIGS[current_camera_idx]
                active_upper_hsv = UPPER_TARGET_HSV_CONFIGS[current_camera_idx]

            targets = get_targets(frame_hsv, active_low_hsv, active_upper_hsv)
            frame_display_bgr = cv2.cvtColor(frame_hsv, cv2.COLOR_HSV2BGR)
            if targets:
                for center, radius in targets:
                    cv2.circle(frame_display_bgr, center, radius, (0, 255, 0), 2)
                    cv2.circle(frame_display_bgr, center, 2, (0, 0, 255), 3)
            cv2.imshow(live_feed_window_name, frame_display_bgr)

            if show_masks:
                if first_run_masks:
                    cv2.namedWindow("All Masks", cv2.WINDOW_NORMAL)
                    cv2.setWindowProperty("All Masks", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                    all_masks_display = np.zeros((all_masks_height, all_masks_width, 3), dtype=np.uint8)
                    first_run_masks = False
                
                if all_masks_display is not None:
                    mask_h_display, mask_s_display, mask_v_display = get_target_masks(frame_hsv, active_low_hsv, active_upper_hsv)
                    
                    h_and_s_display = cv2.bitwise_and(mask_h_display, mask_s_display)
                    h_and_v_display = cv2.bitwise_and(mask_h_display, mask_v_display)
                    s_and_v_display = cv2.bitwise_and(mask_s_display, mask_v_display)
                    final_mask_display = cv2.bitwise_or(h_and_s_display, cv2.bitwise_or(h_and_v_display, s_and_v_display))

                    quad_width = all_masks_width // 2
                    quad_height = all_masks_height // 2

                    mask_h_bgr = cv2.cvtColor(mask_h_display, cv2.COLOR_GRAY2BGR)
                    mask_s_bgr = cv2.cvtColor(mask_s_display, cv2.COLOR_GRAY2BGR)
                    mask_v_bgr = cv2.cvtColor(mask_v_display, cv2.COLOR_GRAY2BGR)
                    final_mask_bgr = cv2.cvtColor(final_mask_display, cv2.COLOR_GRAY2BGR)
                    
                    if quad_width > 0 and quad_height > 0:
                        resized_h = cv2.resize(mask_h_bgr, (quad_width, quad_height))
                        resized_s = cv2.resize(mask_s_bgr, (quad_width, quad_height))
                        resized_v = cv2.resize(mask_v_bgr, (quad_width, quad_height))
                        resized_final = cv2.resize(final_mask_bgr, (quad_width, quad_height))
                        
                        all_masks_display[0:quad_height, 0:quad_width] = resized_h
                        all_masks_display[0:quad_height, quad_width:all_masks_width] = resized_s
                        all_masks_display[quad_height:all_masks_height, 0:quad_width] = resized_v
                        all_masks_display[quad_height:all_masks_height, quad_width:all_masks_width] = resized_final

                        cv2.putText(all_masks_display, "Hue Mask", (text_offset_x, text_offset_y), font, font_scale, font_color, line_type)
                        cv2.putText(all_masks_display, "Saturation Mask", (quad_width + text_offset_x, text_offset_y), font, font_scale, font_color, line_type)
                        cv2.putText(all_masks_display, "Value Mask", (text_offset_x, quad_height + text_offset_y), font, font_scale, font_color, line_type)
                        cv2.putText(all_masks_display, f"Combined Mask ({active_camera_name_str})", (quad_width + text_offset_x, quad_height + text_offset_y), font, font_scale, font_color, line_type)
                    
                    cv2.imshow("All Masks", all_masks_display)
            else:
                if not first_run_masks:
                    try:
                        cv2.destroyWindow("All Masks")
                    except:
                        pass
                    first_run_masks = True
                    all_masks_display = None
                
                if not first_run_hsv_trackbars: 
                    try:
                        cv2.destroyWindow("HSV Thresholds")
                    except:
                        pass
                    first_run_hsv_trackbars = True

        key = cv2.waitKey(1) & 0xFF
        if key != 255 and key != -1 : # 255 or -1 often mean no key pressed btw
            print(f"Key pressed: {key}")

        if key == ord('q'):
            break
        elif key == 13:
            print(f"showing masks: {show_masks}")
            if show_masks:
                print("calling save_hsv_configs...")
                save_hsv_configs(CONFIG_FILE_PATH, LOW_TARGET_HSV_CONFIGS, UPPER_TARGET_HSV_CONFIGS)
        elif key == ord('m'):
            show_masks = not show_masks
            if not show_masks: 
                if not first_run_masks:
                    try:
                        cv2.destroyWindow("All Masks")
                    except:
                        pass
                    first_run_masks = True 
                    all_masks_display = None
                if not first_run_hsv_trackbars:
                    try:
                        cv2.destroyWindow("HSV Thresholds")
                    except:
                        pass
                    first_run_hsv_trackbars = True
            else:
                if first_run_hsv_trackbars:
                    pass
                    
        elif key == ord('1'):
            if current_camera_idx != 0:
                print("Switching to Left Camera")
                try: 
                    cv2.destroyWindow(f"Live Feed {active_camera_names[1]}")
                except:
                    pass 
                current_camera_idx = 0
                if show_masks and not first_run_hsv_trackbars:
                    set_trackbar_positions(LOW_TARGET_HSV_CONFIGS[current_camera_idx], UPPER_TARGET_HSV_CONFIGS[current_camera_idx])
        elif key == ord('2'):
            if current_camera_idx != 1:
                print("Switching to Right Camera")
                try: 
                    cv2.destroyWindow(f"Live Feed {active_camera_names[0]}")
                except:
                    pass
                current_camera_idx = 1
                if show_masks and not first_run_hsv_trackbars:
                    set_trackbar_positions(LOW_TARGET_HSV_CONFIGS[current_camera_idx], UPPER_TARGET_HSV_CONFIGS[current_camera_idx])
    
    print("Exiting...")
    camera_left.stop()
    camera_right.stop()
    cv2.destroyAllWindows()