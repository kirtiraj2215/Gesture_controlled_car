import cv2
import mediapipe as mp
import requests
import warnings

# Suppress specific deprecation warnings
warnings.filterwarnings("ignore", category=UserWarning, module="google.protobuf")

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Capture video from the webcam
cap = cv2.VideoCapture(0)

def is_fingers_raised(landmarks):
    """ Check if all fingers are raised """
    fingers_raised = all(
        landmarks.landmark[mp_hands.HandLandmark(finger_tip)].y <
        landmarks.landmark[mp_hands.HandLandmark(finger_pip)].y
        for finger_tip, finger_pip in [
            (mp_hands.HandLandmark.THUMB_TIP, mp_hands.HandLandmark.THUMB_IP),
            (mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.INDEX_FINGER_PIP),
            (mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_PIP),
            (mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_PIP),
            (mp_hands.HandLandmark.PINKY_TIP, mp_hands.HandLandmark.PINKY_PIP)
        ]
    )
    return fingers_raised

def is_index_raised(landmarks):
    """ Check if only the index finger is raised """
    index_raised = (landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y <
                    landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP].y)
    other_fingers_folded = all(
        landmarks.landmark[mp_hands.HandLandmark(finger_tip)].y >
        landmarks.landmark[mp_hands.HandLandmark(finger_pip)].y
        for finger_tip, finger_pip in [
            (mp_hands.HandLandmark.THUMB_TIP, mp_hands.HandLandmark.THUMB_IP),
            (mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_PIP),
            (mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_PIP),
            (mp_hands.HandLandmark.PINKY_TIP, mp_hands.HandLandmark.PINKY_PIP)
        ]
    )
    return index_raised and other_fingers_folded

def is_thumb_raised(landmarks):
    """ Check if only the thumb is raised """
    thumb_raised = (landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y <
                    landmarks.landmark[mp_hands.HandLandmark.THUMB_IP].y)
    other_fingers_folded = all(
        landmarks.landmark[mp_hands.HandLandmark(finger_tip)].y >
        landmarks.landmark[mp_hands.HandLandmark(finger_pip)].y
        for finger_tip, finger_pip in [
            (mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.INDEX_FINGER_PIP),
            (mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_PIP),
            (mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_PIP),
            (mp_hands.HandLandmark.PINKY_TIP, mp_hands.HandLandmark.PINKY_PIP)
        ]
    )
    return thumb_raised and other_fingers_folded

def is_pinky_raised(landmarks):
    """ Check if only the pinky finger is raised """
    pinky_raised = (landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].y <
                    landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP].y)
    other_fingers_folded = all(
        landmarks.landmark[mp_hands.HandLandmark(finger_tip)].y >
        landmarks.landmark[mp_hands.HandLandmark(finger_pip)].y
        for finger_tip, finger_pip in [
            (mp_hands.HandLandmark.THUMB_TIP, mp_hands.HandLandmark.THUMB_IP),
            (mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.INDEX_FINGER_PIP),
            (mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_PIP),
            (mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_PIP)
        ]
    )
    return pinky_raised and other_fingers_folded

def is_thumb_down(landmarks):
    """ Check if the thumb is pointing down """
    thumb_tip = landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y
    thumb_mcp = landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP].y

    # Thumb is down if thumb tip is below the thumb MCP joint
    return thumb_tip > thumb_mcp

def classify_hand_gesture(landmarks):
    if is_fingers_raised(landmarks):
        return "Move Forward"
    elif is_index_raised(landmarks):
        return "Turn Left"
    elif is_thumb_raised(landmarks):
        return "Stop"
    elif is_pinky_raised(landmarks):
        return "Turn Right"
    elif is_thumb_down(landmarks):
        return "Move Backward "
    else:
        return "Unknown"
    
def message(action):
    if action=="Move Forward":
        return "F"
    elif action=="Turn Left":
        return "L"
    elif action=="Stop":
        return "S"
    elif action=="Turn Right":
        return "R"
    elif action=="Move Backward ":
        return "B"
    else:
        return "U"
    
def send_message(msg):
    url = "http://10.10.2.63/send"
    headers = {'Content-Type': 'text/plain'}
    
    response = requests.post(url, data=msg, headers=headers)
    print(f"Sent message: {msg}")
    print(f"Response from ESP32: {response.text}")

while cap.isOpened():
    success, image = cap.read()
    if not success:
        break

    # Flip the image horizontally for a later selfie-view display
    image = cv2.flip(image, 1)
    # Convert the BGR image to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # Process the image and detect hands
    results = hands.process(image_rgb)

    action = "No Action"
    
    # Draw hand landmarks on the image and classify the gesture
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Classify the gesture based on the landmarks
            action = classify_hand_gesture(hand_landmarks)
            
    # Display the action on the image
    cv2.putText(image, f"Action: {action}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

    # Print the classified action
    print(f"Detected action: {action}")
    
    msg = message(action)
    
    # Print the message to be sent
    print(f"Message to send: {msg}")
    
    # Send the message if it's not unknown
    send_message(msg)

    # Display the image
    cv2.imshow('Hand Gesture Recognition', image)

    # Break loop on 'q' key press
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()
