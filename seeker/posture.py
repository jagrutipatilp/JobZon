import cv2
import mediapipe as mp
import numpy as np
import json
import os
from django.conf import settings
class VideoAnalyzer:
    def __init__(self, video_path):
        self.video_path = video_path
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh()
        self.mp_drawing = mp.solutions.drawing_utils

    def detect_expression(self, face_landmarks):
        if face_landmarks is None:
            return "Neutral"
        try:
            upper_lip = face_landmarks.landmark[13].y
            lower_lip = face_landmarks.landmark[14].y
            mouth_gap = lower_lip - upper_lip
            if mouth_gap > 0.05:
                return "Smiling"
            else:
                return "Neutral"
        except:
            return "Neutral"

    def analyze_video(self):
        cap = cv2.VideoCapture(self.video_path)

        stability_values = []
        distance_values = []
        expression_changes = []

        last_expression = None

        frame_count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pose_results = self.pose.process(image)
            face_results = self.mp_face_mesh.process(image)

            if pose_results.pose_landmarks and face_results.multi_face_landmarks:
                nose = pose_results.pose_landmarks.landmark[self.mp_pose.PoseLandmark.NOSE]
                stability_value = np.abs(nose.x - 0.5) * 100
                stability_values.append(stability_value)
                distance_value = max(0, nose.z * -100)
                distance_values.append(distance_value)

                face_landmarks = face_results.multi_face_landmarks[0] if face_results.multi_face_landmarks else None
                expression = self.detect_expression(face_landmarks)

                if last_expression is not None and expression != last_expression:
                    expression_changes.append(1)
                else:
                    expression_changes.append(0)

                last_expression = expression

        cap.release()

        avg_stability = np.mean(stability_values)
        avg_distance = np.mean(distance_values)
        expression_stability_ratio = sum(expression_changes) / len(expression_changes) if expression_changes else 0

        stability_percentage = 100 - avg_stability if avg_stability <= 100 else 0
        distance_percentage = max(0, min(100, (avg_distance - 20) / (100 - 20) * 100))

        stability_description = "Stable" if stability_percentage > 80 else "Unstable"
        distance_description = "Good" if 40 <= distance_percentage <= 60 else ("Too Close" if distance_percentage < 40 else "Too Far")
        expression_description = "Facial expressions were mostly stable." if expression_stability_ratio > 0.8 else "Facial expressions changed frequently."

        results = {
            'stability_values': stability_values,
            'distance_values': distance_values,
            'expression_changes': expression_changes,
            'stability_description': stability_description,
            'avg_stability': stability_percentage,
            'distance_description': distance_description,
            'avg_distance': avg_distance,
            'expression_description': expression_description
        }

        with open('analysis_results.json', 'w') as f:
            json.dump(results, f)

        return results
