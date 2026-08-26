
import cv2
import math
import numpy as np

# these match mediapipe's landmark numbering
THUMB_TIP = 4
INDEX_TIP = 8

# tuned by hand to feel natural — finger distance → audio param
PITCH_DISTANCE_MIN = 30
PITCH_DISTANCE_MAX = 150
REVERB_DISTANCE_MIN = 30
REVERB_DISTANCE_MAX = 150
VOLUME_DISTANCE_MIN = 50
VOLUME_DISTANCE_MAX = 300

PITCH_RANGE_MIN = 0.5
PITCH_RANGE_MAX = 2.0
REVERB_RANGE_MIN = 0.0
REVERB_RANGE_MAX = 2.0
VOLUME_RANGE_MIN = 0.0
VOLUME_RANGE_MAX = 2.0


class Visualizer:
    def draw_pitch_control(self, image, landmarks):
        thumb_x, thumb_y = landmarks[THUMB_TIP][1], landmarks[THUMB_TIP][2]
        index_x, index_y = landmarks[INDEX_TIP][1], landmarks[INDEX_TIP][2]

        distance = math.hypot(index_x - thumb_x, index_y - thumb_y)
        pitch = float(np.clip(
            np.interp(distance, [PITCH_DISTANCE_MIN, PITCH_DISTANCE_MAX], [PITCH_RANGE_MIN, PITCH_RANGE_MAX]),
            PITCH_RANGE_MIN, PITCH_RANGE_MAX
        ))

        cv2.line(image, (thumb_x, thumb_y), (index_x, index_y), (255, 0, 0), 3)
        cv2.circle(image, (thumb_x, thumb_y), 10, (255, 0, 0), cv2.FILLED)
        cv2.circle(image, (index_x, index_y), 10, (255, 0, 0), cv2.FILLED)

        mid_x, mid_y = (thumb_x + index_x) // 2, (thumb_y + index_y) // 2
        cv2.putText(image, f"Pitch: {pitch:.2f}x", (mid_x - 50, mid_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        return pitch

    def draw_reverb_control(self, image, landmarks):
        thumb_x, thumb_y = landmarks[THUMB_TIP][1], landmarks[THUMB_TIP][2]
        index_x, index_y = landmarks[INDEX_TIP][1], landmarks[INDEX_TIP][2]

        distance = math.hypot(index_x - thumb_x, index_y - thumb_y)
        reverb = float(np.clip(
            np.interp(distance, [REVERB_DISTANCE_MIN, REVERB_DISTANCE_MAX], [REVERB_RANGE_MIN, REVERB_RANGE_MAX]),
            REVERB_RANGE_MIN, REVERB_RANGE_MAX
        ))

        cv2.line(image, (thumb_x, thumb_y), (index_x, index_y), (0, 0, 255), 3)
        cv2.circle(image, (thumb_x, thumb_y), 10, (0, 0, 255), cv2.FILLED)
        cv2.circle(image, (index_x, index_y), 10, (0, 0, 255), cv2.FILLED)

        mid_x, mid_y = (thumb_x + index_x) // 2, (thumb_y + index_y) // 2
        cv2.putText(image, f"Reverb: {reverb:.1f}dB", (mid_x - 50, mid_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        return reverb

    def draw_volume_control(self, image, left_landmarks, right_landmarks):
        left_thumb_x, left_thumb_y = left_landmarks[THUMB_TIP][1], left_landmarks[THUMB_TIP][2]
        left_index_x, left_index_y = left_landmarks[INDEX_TIP][1], left_landmarks[INDEX_TIP][2]
        right_thumb_x, right_thumb_y = right_landmarks[THUMB_TIP][1], right_landmarks[THUMB_TIP][2]
        right_index_x, right_index_y = right_landmarks[INDEX_TIP][1], right_landmarks[INDEX_TIP][2]

        left_mid_x = (left_thumb_x + left_index_x) // 2
        left_mid_y = (left_thumb_y + left_index_y) // 2
        right_mid_x = (right_thumb_x + right_index_x) // 2
        right_mid_y = (right_thumb_y + right_index_y) // 2

        distance = math.hypot(right_mid_x - left_mid_x, right_mid_y - left_mid_y)
        volume = float(np.clip(
            np.interp(distance, [VOLUME_DISTANCE_MIN, VOLUME_DISTANCE_MAX], [VOLUME_RANGE_MIN, VOLUME_RANGE_MAX]),
            VOLUME_RANGE_MIN, VOLUME_RANGE_MAX
        ))

        cv2.line(image, (left_thumb_x, left_thumb_y), (left_index_x, left_index_y), (255, 255, 255), 2)
        cv2.line(image, (right_thumb_x, right_thumb_y), (right_index_x, right_index_y), (255, 255, 255), 2)
        cv2.circle(image, (left_mid_x, left_mid_y), 10, (0, 255, 0), cv2.FILLED)
        cv2.circle(image, (right_mid_x, right_mid_y), 10, (0, 255, 0), cv2.FILLED)
        cv2.line(image, (left_mid_x, left_mid_y), (right_mid_x, right_mid_y), (0, 255, 0), 3)

        display_x = (left_mid_x + right_mid_x) // 2
        display_y = (left_mid_y + right_mid_y) // 2
        cv2.putText(image, f"Volume: {volume:.2f}", (display_x - 50, display_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        return volume
