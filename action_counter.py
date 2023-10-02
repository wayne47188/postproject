import pyttsx3
from PyQt5.QtCore import QThread, pyqtSignal
import threading

class AudioThread(QThread):
    message = pyqtSignal(str)

    def __init__(self, high_threshold=200, low_threshold=50):
        self.high_threshold = high_threshold
        self.low_threshold = low_threshold
        self.count = 0
        self.is_started = False
        self.is_completed_flag = False
        self.engine = pyttsx3.init()
        self.is_playing = False
        super().__init__()

    def play_audio(self, text):
        if self.is_playing:
            return

        def run_speech():
            self.is_playing = True
            self.engine.say(text)
            self.engine.runAndWait()
            self.is_playing = False

        # 使用新的執行緒來播放語音
        speech_thread = threading.Thread(target=run_speech)
        speech_thread.start()

    def run(self):
        self.message.connect(self.play_audio)

class ActionCounter:
    def __init__(self, threshold=10, high_threshold=200, low_threshold=50):
        self.count = 0
        self.threshold = threshold
        self.high_threshold = high_threshold
        self.low_threshold = low_threshold
        self.is_started = False
        self.audio_thread = AudioThread(high_threshold=self.high_threshold, low_threshold=self.low_threshold)
        self.audio_thread.start()

    def increment(self):
        self.count += 1

    def reset(self):
        self.count = 0

    def get_count(self):
        return self.count

    def play_audio(self, message):
        self.audio_thread.message.emit(message)

    def update(self, height_diff):
        if not self.is_started and height_diff > self.low_threshold:
            self.is_started = True
        elif self.is_started and height_diff < self.low_threshold:
            self.count += 1
            self.is_started = False
            self.check_completion()

    def check_completion(self):
        if self.count >= self.threshold:
            self.count = self.threshold

    def get_completion(self):
        return self.count / self.threshold if self.count >= self.threshold else self.count / self.threshold * 100

    def is_completed(self):
        return self.count >= self.threshold
    
    def get_bridge_height(self, pose_landmarks):
        if pose_landmarks is None:
            return 0
        keypoints = self._get_keypoints(pose_landmarks)
        if 'left_hip' not in keypoints or 'right_hip' not in keypoints or 'left_shoulder' not in keypoints or 'right_shoulder' not in keypoints:
            return 0
        shoulder_height = (keypoints['left_shoulder'][1] + keypoints['right_shoulder'][1]) / 2
        hip_height = (keypoints['left_hip'][1] + keypoints['right_hip'][1]) / 2
        return hip_height - shoulder_height
