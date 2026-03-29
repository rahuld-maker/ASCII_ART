import os
import urllib.request
import cv2
import mediapipe as mp
import random
import numpy as np

# --- Setup MediaPipe ---
use_solutions_api = True
hand_landmarker = None
mp_image = None
HandLandmark = None

try:
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
    HandLandmark = mp_hands.HandLandmark
except AttributeError:
    use_solutions_api = False
    from mediapipe.tasks.python.vision import HandLandmarker
    from mediapipe.tasks.python.vision.core import image as mp_image
    from mediapipe.tasks.python.vision.hand_landmarker import HandLandmark

    MODEL_URL = 'https://storage.googleapis.com/mediapipe-tasks/hand_landmarker/hand_landmarker.task'
    MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hand_landmarker.task')

    if not os.path.exists(MODEL_PATH):
        print('Downloading MediaPipe hand landmarker model...')
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)

    hand_landmarker = HandLandmarker.create_from_model_path(MODEL_PATH)

# --- Fruit Class ---
class Fruit:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.reset()

    def reset(self):
        self.x = random.randint(100, self.w - 100)
        self.y = self.h
        self.speed_y = random.randint(-18, -12) # Launch up
        self.speed_x = random.randint(-5, 5)     # Slight side movement
        self.radius = 30
        self.color = (0, 165, 255) # Orange color (BGR)
        self.is_sliced = False

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y += 1 # Gravity
        # Reset if it falls off screen
        if self.y > self.h + 50:
            self.reset()

# --- Main Game ---
cap = cv2.VideoCapture(0)
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

fruit = Fruit(640, 480) # Standardize size
score = 0

while cap.isOpened():
    success, frame = cap.read()
    if not success: break

    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (640, 480))
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Hand Tracking Logic
    if use_solutions_api:
        results = hands.process(rgb_frame)
        hand_landmarks = []
        if results.multi_hand_landmarks:
            for hand_lms in results.multi_hand_landmarks:
                hand_landmarks.append(hand_lms.landmark)
    else:
        mp_frame = mp_image.Image(mp_image.ImageFormat.SRGB, rgb_frame)
        results = hand_landmarker.detect(mp_frame)
        hand_landmarks = results.hand_landmarks if results.hand_landmarks else []

    # Update Fruit
    fruit.update()

    for hand_lms in hand_landmarks:
        tip = hand_lms[HandLandmark.INDEX_FINGER_TIP]
        tx, ty = int(tip.x * 640), int(tip.y * 480)

        # Draw Blade Tip
        cv2.circle(frame, (tx, ty), 10, (255, 255, 255), -1)

        # Collision Detection (Distance formula)
        distance = np.sqrt((tx - fruit.x)**2 + (ty - fruit.y)**2)
        if distance < fruit.radius:
            score += 1
            fruit.reset()

    # Draw Fruit
    cv2.circle(frame, (int(fruit.x), int(fruit.y)), fruit.radius, fruit.color, -1)
    
    # Draw Score
    cv2.putText(frame, f"Score: {score}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Hand-Controlled Fruit Ninja", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
if hand_landmarker is not None:
    hand_landmarker.close()
cv2.destroyAllWindows()