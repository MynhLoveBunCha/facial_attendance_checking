import cv2
import mediapipe as mp


class FaceDetector:
    def __init__(self, model=0, minDetectionCon=0.5):
        self.model = model
        self.minDetectionCon = minDetectionCon
        self.mpFaceDetection = mp.solutions.face_detection
        self.mpDraw = mp.solutions.drawing_utils
        self.faceDetection = self.mpFaceDetection.FaceDetection(model_selection=model, min_detection_confidence=self.minDetectionCon)

    def findFaces(self, img):
        frame_RGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.faceDetection.process(frame_RGB)
        faces = []
        if results.detections:
            for id, detection in enumerate(results.detections):
                bbox_class = detection.location_data.relative_bounding_box
                frame_h, frame_w, color_channel = img.shape
                bbox = int(bbox_class.xmin * frame_w), int(bbox_class.ymin * frame_h), \
                        int(bbox_class.width * frame_w), int(bbox_class.height * frame_h)
                faces.append([id, bbox, detection.score])
        return faces

    def drawBoundingBox(self, img, faces, color=(0, 255, 0), line_thickness=7, text_thickness=2):
        for face in faces:
            x, y, w, h = face[1]
            linelen = w // 6
            confidence = face[2][0]
            cv2.line(img, (x, y), (x + linelen, y), color, thickness=line_thickness)
            cv2.line(img, (x, y), (x, y + linelen), color, thickness=line_thickness)
            cv2.line(img, (x, y + h), (x + linelen, y + h), color, thickness=line_thickness)
            cv2.line(img, (x, y + h), (x, y + h - linelen), color, thickness=line_thickness)
            cv2.line(img, (x + w, y), (x + w - linelen, y), color, thickness=line_thickness)
            cv2.line(img, (x + w, y), (x + w, y + linelen), color, thickness=line_thickness)
            cv2.line(img, (x + w, y + h), (x + w - linelen, y + h), color, thickness=line_thickness)
            cv2.line(img, (x + w, y + h), (x + w, y + h - linelen), color, thickness=line_thickness)
            cv2.putText(img, f'{int(confidence * 100)}%', (x, y - 20), cv2.FONT_HERSHEY_PLAIN, 1.5, color, thickness=text_thickness)
        return img
