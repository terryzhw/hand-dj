
import cv2
import time
import os
import pygame
import threading
import numpy as np
from tracking.hand_tracker import HandTracker
from audio.audio_controller import AudioController
from tracking.visualizer import Visualizer
from modules.constants import *


class DJController:
    def __init__(self, audio_file="audio.wav"):
        self.camera_width = DEFAULT_CAMERA_WIDTH
        self.camera_height = DEFAULT_CAMERA_HEIGHT

        self.visualizer = Visualizer(camera_width=self.camera_width, camera_height=self.camera_height)
        self.audio_controller = AudioController(sample_rate=DEFAULT_SAMPLE_RATE)

        self.hand_tracker = None
        self.camera = None
        self.initialization_complete = False

        self.previous_time = 0
        self.previous_landmarks = {'left': None, 'right': None}

        self.controls_enabled = {'pitch': True, 'reverb': True, 'volume': True}

        self.pending_audio_file = audio_file if audio_file and os.path.exists(audio_file) else None

        # mediapipe and camera take a while to load, so do it in the background
        self.init_thread = threading.Thread(target=self.initialize, daemon=True)
        self.init_thread.start()

    def initialize(self):
        self.hand_tracker = HandTracker(
            detection_confidence=DEFAULT_DETECTION_CONFIDENCE,
            max_hands=DEFAULT_MAX_HANDS
        )

        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)
        self.camera.set(cv2.CAP_PROP_FPS, 30)
        # buffer of 1 so we always get the latest frame, not a stale one
        self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if self.pending_audio_file:
            self.audio_controller.load_audio(self.pending_audio_file)

        self.initialization_complete = True

    def is_ready(self):
        return self.initialization_complete and self.camera is not None and self.hand_tracker is not None

    def run(self):
        while True:
            if not self.is_ready():
                frame = np.zeros((self.camera_height, self.camera_width, 3), dtype=np.uint8)
                text_size = cv2.getTextSize("Loading HandDJ...", cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
                text_x = (self.camera_width - text_size[0]) // 2
                text_y = (self.camera_height - text_size[1]) // 2
                cv2.putText(frame, "Loading HandDJ...", (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.imshow("HandDJ", frame)
                cv2.waitKey(100)
                continue

            success, frame = self.camera.read()
            if not success:
                time.sleep(0.1)
                continue

            frame = cv2.flip(frame, 1)
            frame = self.hand_tracker.process_hands(frame)
            self.update_controls(frame)

            current_time = time.time()
            if self.previous_time > 0:
                fps = 1 / (current_time - self.previous_time)
                cv2.putText(frame, f"FPS: {int(fps)}", (10, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            self.previous_time = current_time

            cv2.imshow("HandDJ", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cleanup()

    def smooth_landmarks(self, current, previous, factor=0.3):
        # blend with previous frame's landmarks so the hand doesn't jitter
        if previous is None:
            return current
        smoothed = []
        for curr, prev in zip(current, previous):
            sx = int(prev[1] * (1 - factor) + curr[1] * factor)
            sy = int(prev[2] * (1 - factor) + curr[2] * factor)
            smoothed.append([curr[0], sx, sy])
        return smoothed

    def update_controls(self, frame):
        if self.hand_tracker.left_hand_present and self.hand_tracker.left_hand_landmarks:
            smoothed = self.smooth_landmarks(
                self.hand_tracker.left_hand_landmarks,
                self.previous_landmarks['left']
            )
            self.previous_landmarks['left'] = smoothed

            if self.controls_enabled['pitch']:
                pitch = self.visualizer.draw_pitch_control(frame, smoothed)
                self.audio_controller.smooth_pitch(pitch)
        else:
            # reset so smoothing starts fresh when the hand comes back
            self.previous_landmarks['left'] = None

        if self.hand_tracker.right_hand_present and self.hand_tracker.right_hand_landmarks:
            smoothed = self.smooth_landmarks(
                self.hand_tracker.right_hand_landmarks,
                self.previous_landmarks['right']
            )
            self.previous_landmarks['right'] = smoothed

            if self.controls_enabled['reverb']:
                reverb = self.visualizer.draw_reverb_control(frame, smoothed)
                self.audio_controller.smooth_reverb(reverb)
        else:
            self.previous_landmarks['right'] = None

        if (self.hand_tracker.left_hand_present and self.hand_tracker.right_hand_present
                and self.previous_landmarks['left'] and self.previous_landmarks['right']):
            if self.controls_enabled['volume']:
                volume = self.visualizer.draw_volume_control(
                    frame, self.previous_landmarks['left'], self.previous_landmarks['right']
                )
                self.audio_controller.smooth_volume(volume)

    def get_stats(self):
        return self.audio_controller.get_stats()

    def toggle_control(self, name):
        if name in self.controls_enabled:
            self.controls_enabled[name] = not self.controls_enabled[name]

    def is_control_enabled(self, name):
        return self.controls_enabled.get(name, False)

    def cleanup(self):
        if self.camera is not None:
            self.camera.release()
        cv2.destroyAllWindows()
        self.audio_controller.cleanup()
        if self.hand_tracker is not None:
            self.hand_tracker.cleanup()
        pygame.quit()
