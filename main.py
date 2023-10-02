import cv2
import mediapipe as mp
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
import pose_detector
import action_counter
from action_counter import ActionCounter

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose_detector = pose_detector.PoseDetector(min_detection_confidence=0.6, min_tracking_confidence=0.6)
action_counter = action_counter.ActionCounter(threshold=5)

high_prompt = "動作太高了"
low_prompt = "動作太低了"

class VideoFrame(QLabel):
    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.capture_frame)
        self.timer.start(50)
        self.completion_label = QLabel()
        self.completion_label.setStyleSheet("QLabel { background-color : white; color : black; font-size: 40px; }")
        self.bridge_stage_label = QLabel("超人階段：", self)
        self.bridge_stage_label.setGeometry(10, 60, 200, 30)

    def capture_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(cv2.resize(frame, (int(frame.shape[1] * (640 / frame.shape[0])), 640)), 1)
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose_detector.detect(image)
            pose_landmarks = results if results is not None else None

            if pose_landmarks is not None:
                # Add these lines before calling get_bridge_height and detect_bridge_stage:
                image_width = image.shape[1]
                image_height = image.shape[0]

                # 印出height_diff
                height_diff = pose_detector.get_bridge_height(pose_landmarks, image_width, image_height)
                print("height_diff: ", height_diff)

                keypoints = pose_detector._get_keypoints(pose_landmarks)
                print(keypoints)


                # Modify the detect_bridge_stage method call to include the image dimensions:
                bridge_stage = pose_detector.detect_bridge_stage(pose_landmarks, image_width, image_height)

                height = pose_detector.get_bridge_height(pose_landmarks, image_width, image_height)
                qimage = self.convert_cvimage_to_qimage(pose_detector.draw(image, results))
                self.setPixmap(QPixmap.fromImage(qimage))

                self.bridge_stage_label.setText("超人階段：{}".format(bridge_stage))

                action_counter.update(height)
                completion_percentage = action_counter.get_completion()
                if action_counter.is_completed():
                    self.completion_label.setText("恭喜你完成超人式運動")
                    action_counter.play_audio(high_prompt)
                    action_counter.reset()
                elif height > action_counter.high_threshold:
                    self.completion_label.setText("動作太高了")
                    action_counter.play_audio(high_prompt)
                    action_counter.reset()
                elif height < action_counter.low_threshold:
                    self.completion_label.setText("動作太低了")
                    action_counter.play_audio(low_prompt)
                    action_counter.reset()
                else:
                    self.completion_label.setText("請繼續完成運動")
                    self.completion_label.setText("超人式運動進度: {:.2f}%".format(completion_percentage))

    def convert_cvimage_to_qimage(self, cvimage):
            height, width, channel = cvimage.shape
            bytes_per_line = channel * width
            qimage = QImage(cvimage.data, width, height, bytes_per_line, QImage.Format_RGB888)
            return qimage


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("超人式 運動")
        self.resize(800,600)
        # 初始化视频标签和提示文字标签
        self.video_label = VideoFrame()

        # 将视频标签和提示文字标签加入垂直布局
        vbox = QVBoxLayout()
        vbox.addWidget(self.video_label)
        vbox.addWidget(self.video_label.completion_label)
        vbox.addWidget(self.video_label.bridge_stage_label)

        # 设置主窗口的布局
        self.setLayout(vbox)

    def closeEvent(self, event):
        self.cap.release()
        event.accept()


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
