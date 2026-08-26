
import cv2
import mediapipe as mp


class HandTracker:
    def __init__(self, detection_confidence=0.7, max_hands=2):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            model_complexity=1,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.results = None

        self.left_hand_present = False
        self.right_hand_present = False
        self.left_hand_landmarks = None
        self.right_hand_landmarks = None

    def process_hands(self, image):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # mediapipe skips an internal copy if we mark it read-only
        image_rgb.flags.writeable = False
        self.results = self.hands.process(image_rgb)
        image_rgb.flags.writeable = True

        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                    landmark_drawing_spec=self.mp_draw.DrawingSpec(color=(0, 0, 0), thickness=2, circle_radius=2),
                    connection_drawing_spec=self.mp_draw.DrawingSpec(color=(255, 255, 255), thickness=2)
                )

        self.left_hand_present = False
        self.right_hand_present = False
        self.left_hand_landmarks = None
        self.right_hand_landmarks = None

        if self.results and self.results.multi_hand_landmarks:
            handedness_list = self.results.multi_handedness

            for i in range(len(self.results.multi_hand_landmarks)):
                hand = self.results.multi_hand_landmarks[i]
                h, w, c = image.shape
                landmarks = [[id, int(lm.x * w), int(lm.y * h)] for id, lm in enumerate(hand.landmark)]

                hand_type = handedness_list[i].classification[0].label if handedness_list else None

                if hand_type == "Right":
                    self.right_hand_landmarks = landmarks
                    self.right_hand_present = True
                elif hand_type == "Left":
                    self.left_hand_landmarks = landmarks
                    self.left_hand_present = True

        return image

    def cleanup(self):
        cv2.destroyAllWindows()
