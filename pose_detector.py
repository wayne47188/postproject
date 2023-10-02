import cv2
import mediapipe as mp
import cv2
import mediapipe as mp

class PoseDetector:
    def __init__(self, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=min_detection_confidence, min_tracking_confidence=min_tracking_confidence)
        self.stage1_threshold = 0.15
        self.stage2_threshold = 0.3

    def check_keypoints_captured(self, pose_landmarks, side):
        keypoints = self._get_keypoints(pose_landmarks)
        print(keypoints)
        if keypoints is None:
            return False
        if side == 'left':
            return 'LEFT_SHOULDER' in keypoints and 'LEFT_HIP' in keypoints and 'LEFT_KNEE' in keypoints and 'LEFT_ANKLE' in keypoints
        elif side == 'right':
            return 'RIGHT_SHOULDER' in keypoints and 'RIGHT_HIP' in keypoints and 'RIGHT_KNEE' in keypoints and 'RIGHT_ANKLE' in keypoints
        else:
            return False

    def detect_bridge_stage(self, pose_landmarks, image_width, image_height):
        height_diff = self.get_bridge_height(pose_landmarks, image_width, image_height)
        if height_diff is None:
            return None
        if height_diff < self.stage1_threshold * image_height:
            return "阶段1"
        elif height_diff < self.stage2_threshold * image_height:
            return "阶段2"
        else:
            return "阶段3"

    def detect(self, image):
        results = self.pose.process(image)
        if results.pose_landmarks is not None:
            return results.pose_landmarks
        else:
            return None

    def get_bridge_height(self, pose_landmarks, image_width, image_height):
        keypoints = self._get_keypoints(pose_landmarks)
        if keypoints is None:
            return None
        bridge_height = keypoints['LEFT_SHOULDER'][1] * image_height - keypoints['NOSE'][1] * image_height
        return bridge_height

    def _get_keypoints(self, pose_landmarks):
        keypoints = {}
        for id, lm in enumerate(pose_landmarks.landmark):
            keypoints[self.mp_pose.PoseLandmark(id).name] = (lm.x, lm.y, lm.z)
        return keypoints


    def draw(self, image, pose_landmarks):
        if pose_landmarks is None:
            return image
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing.draw_landmarks(
            image=image,
            landmark_list=pose_landmarks,
            connections=self.mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing.DrawingSpec(color=(255,255,255), thickness=2, circle_radius=2),
            connection_drawing_spec=mp_drawing.DrawingSpec(color=(255,255,255), thickness=2, circle_radius=2)
        )
        return image