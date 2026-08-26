
import cv2
import mediapipe as mp


class HandDetector:
    def __init__(self, max_hands=2, detection_confidence=0.7, track_confidence=0.5):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            model_complexity=1,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=track_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.results = None

    def find_hands(self, image, draw=True):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # mediapipe runs faster when the image is marked read-only
        image_rgb.flags.writeable = False
        self.results = self.hands.process(image_rgb)
        image_rgb.flags.writeable = True

        if self.results.multi_hand_landmarks and draw:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                    landmark_drawing_spec=self.mp_draw.DrawingSpec(color=(0, 0, 0), thickness=2, circle_radius=2),
                    connection_drawing_spec=self.mp_draw.DrawingSpec(color=(255, 255, 255), thickness=2)
                )
        return image

    def find_position(self, image, hand_no=0):
        landmarks = []
        if self.results.multi_hand_landmarks and hand_no < len(self.results.multi_hand_landmarks):
            hand = self.results.multi_hand_landmarks[hand_no]
            h, w, c = image.shape
            for id, lm in enumerate(hand.landmark):
                landmarks.append([id, int(lm.x * w), int(lm.y * h)])
        return landmarks

    def get_hand_type(self, hand_index, handedness_list):
        if handedness_list and hand_index < len(handedness_list):
            return handedness_list[hand_index].classification[0].label
        return None


class HandTracker:
    def __init__(self, detection_confidence=0.8, max_hands=2):
        self.hand_detector = HandDetector(detection_confidence=detection_confidence, max_hands=max_hands)
        self.left_hand_present = False
        self.right_hand_present = False
        self.left_hand_landmarks = None
        self.right_hand_landmarks = None

    def process_hands(self, image):
        image = self.hand_detector.find_hands(image)

        self.left_hand_present = False
        self.right_hand_present = False
        self.left_hand_landmarks = None
        self.right_hand_landmarks = None

        if self.hand_detector.results and self.hand_detector.results.multi_hand_landmarks:
            num_hands = len(self.hand_detector.results.multi_hand_landmarks)
            handedness_list = self.hand_detector.results.multi_handedness

            for i in range(num_hands):
                landmarks = self.hand_detector.find_position(image, hand_no=i)
                hand_type = self.hand_detector.get_hand_type(i, handedness_list)

                if hand_type == "Right":
                    self.right_hand_landmarks = landmarks
                    self.right_hand_present = True
                elif hand_type == "Left":
                    self.left_hand_landmarks = landmarks
                    self.left_hand_present = True

        return image

    def cleanup(self):
        cv2.destroyAllWindows()
