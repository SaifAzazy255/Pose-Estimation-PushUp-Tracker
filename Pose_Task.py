import cv2
import mediapipe as mp
import numpy as np

# Function to calculate the angle between 3 points
def calculate_angle(a, b, c):
    a = np.array(a) # First point (e.g., Shoulder)
    b = np.array(b) # Mid point (e.g., Elbow)
    c = np.array(c) # End point (e.g., Wrist)
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    if angle > 180.0: angle = 360 - angle
    return angle

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

video_path = "IMG_0029.MOV"  # Input video path
cap = cv2.VideoCapture(video_path)

# =====================================================================
# 🛠️ Settings Dashboard
# =====================================================================
start_frame = 150       # Frame to start processing from
end_frame = 550         # Frame to stop processing at

# UI Settings
box_width, box_height = 180, 70  
text_size_small = 0.5            
text_size_large = 0.8           
text_thickness = 1               

# Output video speed control (FPS)
# Decrease for slower playback (e.g., 30, 24, 20)
output_fps = 30  

# =====================================================================
# VideoWriter Configuration
# =====================================================================
out_width, out_height = 1280, 720
fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
out = cv2.VideoWriter('Pushup_Demo_Output.mp4', fourcc, output_fps, (out_width, out_height))

# Set the starting frame
cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

counter = 0
Status = None

print(f"Processing video and exporting at {output_fps} FPS...")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
        
    current_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
    
    # Stop processing if the current frame reaches the target end_frame
    if current_frame >= end_frame:
        print(f"\nFinished processing up to frame {current_frame}.")
        break
        
    # Resize frame and convert color space for MediaPipe
    frame = cv2.resize(frame, (out_width, out_height)) 
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)
    
    try:
        landmarks = results.pose_landmarks.landmark
        
        # 1. Extract coordinates (Right side)
        shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
        wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
        
        # 2. Calculate elbow angle
        angle = calculate_angle(shoulder, elbow, wrist)
        
        # 3. Convert coordinates to Pixel coordinates
        out_w, out_h = out_width, out_height
        shoulder_px = tuple(np.multiply(shoulder, [out_w, out_h]).astype(int))
        elbow_px = tuple(np.multiply(elbow, [out_w, out_h]).astype(int))
        wrist_px = tuple(np.multiply(wrist, [out_w, out_h]).astype(int))
        
        # 4. Draw the angle in White at the elbow (KEEP AS IS)
        cv2.putText(frame, str(int(angle)), elbow_px, 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
        
        # =====================================================================
        # NEW UI: Draw Point Numbers inside FILLED Red Circles
        # =====================================================================
        point_circle_radius = 20
        point_fill_color = (0, 0, 255) # Red Filled (BGR)
        point_text_color = (255, 255, 255) # White Text
        point_text_scale = 0.5
        point_text_thickness = 1
        
        # Helper to center text inside a circle
        def draw_centered_text_circle(img, center_px, text, offset=(0,0)):
            # Calculate final circle center with an offset to avoid blocking landmarks/angle
            final_center = (center_px[0] + offset[0], center_px[1] + offset[1])
            
            # Draw the FILLED circle background
            cv2.circle(img, final_center, point_circle_radius, point_fill_color, cv2.FILLED)
            
            # Calculate centering of text
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, point_text_scale, point_text_thickness)[0]
            text_x = final_center[0] - text_size[0] // 2
            text_y = final_center[1] + text_size[1] // 2
            
            # Draw the text on top
            cv2.putText(img, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 
                        point_text_scale, point_text_color, point_text_thickness, cv2.LINE_AA)

        # Draw UI for Shoulder (12), Elbow (14), Wrist (16) with distinct offsets
        # so they don't cover each other or the angle text.
        draw_centered_text_circle(frame, shoulder_px, "12", offset=(25, -25))
        
        # Offset 14 slightly different to not cover angle drawn at elbow_px
        draw_centered_text_circle(frame, elbow_px, "14", offset=(35, 30)) 
        
        draw_centered_text_circle(frame, wrist_px, "16", offset=(25, 25))
        # =====================================================================
        
        # 5. Push-up counting logic
        if angle > 160:
            Status = "UP"
        if angle < 90 and Status == 'UP':
            Status = "DOWN"
            counter += 1
            print(f"Push-up {counter} recorded at frame {current_frame}")
            
    except:
        pass
    
    # Draw the UI elements (Background box and text)
    cv2.rectangle(frame, (0,0), (box_width, box_height), (0,0,0), -1)
    
    cv2.putText(frame, 'REPS', (10, 20), cv2.FONT_HERSHEY_SIMPLEX, text_size_small, (255,255,255), 1, cv2.LINE_AA)
    cv2.putText(frame, str(counter), (10, 60), cv2.FONT_HERSHEY_SIMPLEX, text_size_large, (0,255,0), text_thickness, cv2.LINE_AA)
    
    cv2.putText(frame, 'Status', (90, 20), cv2.FONT_HERSHEY_SIMPLEX, text_size_small, (255,255,255), 1, cv2.LINE_AA)
    cv2.putText(frame, Status if Status else "-", (90, 60), cv2.FONT_HERSHEY_SIMPLEX, text_size_large, (0,255,0), text_thickness, cv2.LINE_AA)
    
    # Draw pose landmarks on the frame
    mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    
    # Write the processed frame to the output video
    out.write(frame)
    cv2.imshow('Push-up Counter Processing', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
out.release()
cv2.destroyAllWindows()
print("\nExport Complete!")