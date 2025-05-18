import cv2
import numpy as np
from camera import Camera

def calculate_hsv_stats(hsv_values_list):
    if not hasattr(hsv_values_list, '__len__') or len(hsv_values_list) == 0:
        return {
            'min': 0, 'q1': 0, 'median': 0, 'q3': 0, 'mean': 0, 'max': 0,
            'count': 0
        }
    
    values_array = np.array(hsv_values_list)
    stats = {
        'min': int(np.min(values_array)),
        'q1': int(np.percentile(values_array, 25)),
        'median': int(np.percentile(values_array, 50)),
        'q3': int(np.percentile(values_array, 75)),
        'mean': int(np.mean(values_array)),
        'max': int(np.max(values_array)),
        'count': len(values_array)
    }
    return stats

def main():
    camera_index = 0
    cam = Camera(camera_index)

    circle_radius = 75 # aim circle radius
    circle_color = (0, 0, 255)
    circle_thickness = 2

    print("Starting calibration test...")
    while True:
        frame_hsv = cam.get_frame()
        if frame_hsv is None:
            print(f"Error: Could not get frame from camera {camera_index}. Retrying...")
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            continue

        frame_bgr_display = cv2.cvtColor(frame_hsv, cv2.COLOR_HSV2BGR)
        
        height, width = frame_bgr_display.shape[:2]
        center_x, center_y = width // 2, height // 2

        # draw the red circle for aiming
        cv2.circle(frame_bgr_display, (center_x, center_y), circle_radius, circle_color, circle_thickness)

        cv2.imshow(f"Calibration Feed - Camera {camera_index}", frame_bgr_display)
        
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            print("Exiting...")
            break
        elif key == 13:  # ENTER
            print("\n--- Capturing HSV Data ---")
            
            # create a mask for the circle jo
            mask = np.zeros((height, width), dtype=np.uint8)
            cv2.circle(mask, (center_x, center_y), circle_radius, 255, -1) # filled circle

            # extract H, S, V channels from the original HSV frame
            h_channel, s_channel, v_channel = cv2.split(frame_hsv)

            # get pixels within the mask
            h_values_in_circle = h_channel[mask == 255]
            s_values_in_circle = s_channel[mask == 255]
            v_values_in_circle = v_channel[mask == 255]

            if h_values_in_circle.size == 0:
                print("No pixels found in the circle. Make sure the circle is on the object.")
                continue

            h_stats = calculate_hsv_stats(h_values_in_circle.tolist())
            s_stats = calculate_hsv_stats(s_values_in_circle.tolist())
            v_stats = calculate_hsv_stats(v_values_in_circle.tolist())

            print(f"Hue - Count: {h_stats['count']}")
            print(f"  Min: {h_stats['min']}, Q1: {h_stats['q1']}, Median: {h_stats['median']}, Q3: {h_stats['q3']}, Mean: {h_stats['mean']}, Max: {h_stats['max']}")
            
            print(f"Saturation - Count: {s_stats['count']}")
            print(f"  Min: {s_stats['min']}, Q1: {s_stats['q1']}, Median: {s_stats['median']}, Q3: {s_stats['q3']}, Mean: {s_stats['mean']}, Max: {s_stats['max']}")

            print(f"Value - Count: {v_stats['count']}")
            print(f"  Min: {v_stats['min']}, Q1: {v_stats['q1']}, Median: {v_stats['median']}, Q3: {v_stats['q3']}, Mean: {v_stats['mean']}, Max: {v_stats['max']}")
            print('--------------------------------')


    cam.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
