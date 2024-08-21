import cv2
import mediapipe as mp

# Initialize MediaPipe Hands and Drawing Utils
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Define a function to count fingers
def count_fingers(landmarks):
    landmarks = [(landmark.x, landmark.y, landmark.z) for landmark in landmarks]

    count = 0

    # Define the landmarks for the fingers
    thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
    thumb_ip = landmarks[mp_hands.HandLandmark.THUMB_IP]
    thumb_mcp = landmarks[mp_hands.HandLandmark.THUMB_CMC]
    index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    index_mcp = landmarks[mp_hands.HandLandmark.INDEX_FINGER_MCP]
    middle_tip = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    middle_mcp = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
    ring_tip = landmarks[mp_hands.HandLandmark.RING_FINGER_TIP]
    ring_mcp = landmarks[mp_hands.HandLandmark.RING_FINGER_MCP]
    pinky_tip = landmarks[mp_hands.HandLandmark.PINKY_TIP]
    pinky_mcp = landmarks[mp_hands.HandLandmark.PINKY_MCP]

    # Define thresholds for detecting if a finger is raised
    thumb_threshold = 0.1

    if thumb_tip[1] < thumb_threshold:
        count += 1
    
    if index_tip[1] < index_mcp[1]:
        count += 1

    if middle_tip[1] < middle_mcp[1]:
        count += 1

    if ring_tip[1] < ring_mcp[1]:
        count += 1

    if pinky_tip[1] < pinky_mcp[1]:
        count += 1

    # If all fingers are raised, return 6
    
    return count

# Initialize the video capture
cap = cv2.VideoCapture(0)

with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the frame to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        # Draw hand landmarks and count fingers
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw landmarks and connections
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Count fingers
                num_fingers = count_fingers(hand_landmarks.landmark)
                
                # Display the count on the frame
                cv2.putText(frame, f'Fingers Raised: {num_fingers}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        # Show the frame
        cv2.imshow('Hand Tracking', frame)

        # Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Release resources
cap.release()
cv2.destroyAllWindows()