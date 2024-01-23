import csv
from pathlib import Path
from typing import Optional

import cv2
import norfair
import numpy as np
import torch
from mmdet.apis import inference_detector, init_detector
from norfair import Tracker, Video

from auto_od.helper.tracker import euclidean_distance


class ObjectTracker:
    """
    Object tracker that integrates object detection and tracking functionality.

    Attributes:
        model_path (str): Path to the model checkpoint file.
        config_path (str): Path to the model configuration file.
        device (str): Device to run the model on (e.g., 'cuda:0', 'cpu').
        track_points (str): Specifies the tracking points, either 'centroid' or 'bbox'.
        max_track_distance (int): Maximum distance for tracking objects between frames.
        conf_thresh (float): Confidence threshold for object detection.
        hit_counter_max (int): Maximum number of frames an object can be tracked without detection.
        initialization_delay (int): Delay before initializing tracking for a new object.
        pointwise_hit_counter_max (int): Maximum counter for individual points within an object.
        detection_threshold (float): Threshold for the detection of objects.
        past_detections_length (int): Number of past detections to consider for tracking.
        distance_function (function): Distance function for tracking objects.
        tracker (norfair.Tracker): Norfair tracker instance.
        last_detections (list): List of last detected objects.
        current_frame_index (int): Index of the current frame being processed.
        model (object): Loaded object detection model.
        tracked_objects_history (list): History of tracked objects.
        detection_id_to_tracked_id (dict): Mapping of detection IDs to tracked object IDs.
    """
    def __init__(self, model_path: str, config_path: str, device: Optional[str] = None, track_points: str = "bbox",
                 max_track_distance: int = 30, conf_thresh: float = 0.35, hit_counter_max: int = 15,
                 initialization_delay: Optional[int] = None, pointwise_hit_counter_max: int = 4,
                 detection_threshold: float = 0.1, past_detections_length: int = 4,
                 distance_function: any = euclidean_distance):

        self.model_path = model_path
        self.config_path = config_path
        self.device = device or ("cuda:0" if torch.cuda.is_available() else "cpu")
        self.track_points = track_points
        self.max_track_distance = max_track_distance
        self.conf_thresh = conf_thresh
        self.hit_counter_max = hit_counter_max
        self.initialization_delay = initialization_delay
        self.pointwise_hit_counter_max = pointwise_hit_counter_max
        self.detection_threshold = detection_threshold
        self.past_detections_length = past_detections_length
        self.distance_function = distance_function

        self.tracker = Tracker(
            distance_function=self.distance_function,
            distance_threshold=self.max_track_distance,
            hit_counter_max=self.hit_counter_max,
            initialization_delay=self.initialization_delay,
            pointwise_hit_counter_max=self.pointwise_hit_counter_max,
            detection_threshold=self.detection_threshold,
            past_detections_length=self.past_detections_length,
        )
        self.last_detections = None
        self.current_frame_index = 0
        self.model = self._load_model()
        self.tracked_objects_history = []
        self.detection_id_to_tracked_id = None

    def _load_model(self):
        """
        Loads the object detection model from the specified checkpoint and configuration.

        Returns:
            Module: Loaded object detection model.
        """
        assert Path(self.model_path).is_file(), f"{self.model_path} should be a checkpoint file."
        assert Path(self.config_path).is_file(), f"{self.config_path} should be a config file."
        if not Path(self.model_path).exists():
            raise FileNotFoundError(f"{self.model_path} is not present.")

        model = init_detector(config=self.config_path, checkpoint=self.model_path, device=self.device)
        self.classes = model.dataset_meta["classes"]

        return model

    def export_tracking_data_to_csv(self, csv_file_path):
        """
        Exports tracked objects history to a CSV file.

        Args:
            csv_file_path (str): Path to the CSV file where tracking data will be saved.
        """
        fieldnames = ['id', 'points', 'frame', 'label']
        with open(csv_file_path, mode='w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for obj_data in self.tracked_objects_history:
                writer.writerow(obj_data)

    def _transform_detection_format(self, result, classes_to_detect: list = None):
        """
        Transforms the detection result format to be compatible with the tracking algorithm.

        Args:
            result (any): Object detection result.
            classes_to_detect (list, optional): List of classes to detect.

        Returns:
            list: List of transformed detections.
        """
        pred_instances = result.pred_instances
        bboxes = pred_instances.bboxes
        scores = pred_instances.scores
        labels = pred_instances.labels
        norfair_detections = []
        for bbox, score, label in zip(bboxes, scores, labels):
            if score > self.conf_thresh:
                x1, y1, x2, y2 = bbox
                if self.track_points == "centroid":
                    centroid = np.array([(x1 + x2) / 2, (y1 + y2) / 2])
                    norfair_detection = norfair.Detection(points=centroid, scores=np.array([score]))
                elif self.track_points == "bbox":
                    bbox = np.array([[x1, y1], [x2, y2]])
                    scores = np.array([score, score])

                    class_name = self.classes[int(label)] if self.classes else "Class {}".format(label)
                    if classes_to_detect is not None and class_name not in classes_to_detect:
                        continue

                    detection = norfair.Detection(points=bbox, scores=np.array([score, score]), label=class_name)

                    norfair_detections.append(detection)
        return norfair_detections

    def store_tracked_objects(self, tracked_objects):
        """
        Stores the history of tracked objects.

        Args:
            tracked_objects (list): List of tracked objects to store.
        """
        for obj in tracked_objects:
            self.tracked_objects_history.append({
                'id': obj.id,
                'points': obj.estimate,
                'frame': self.current_frame_index,
                'label': obj.label
            })

    def get_tracked_objects_history(self):
        """
        Retrieves the history of tracked objects.

        Returns:
            list: History of tracked objects.
        """
        return self.tracked_objects_history

    def process_frame(self, frame, classes_to_detect: list = None):
        """
        Processes a single frame for object detection and transforms the detection format.

        Args:
            frame (numpy.ndarray): The frame to process.
            classes_to_detect (list, optional): List of classes to detect.

        Returns:
            list: List of detections in the processed frame.
        """
        result = inference_detector(self.model, frame)
        detections = self._transform_detection_format(result=result, classes_to_detect=classes_to_detect)

        self.last_detections = detections
        return detections

    def process_video(self,
                      camera: Optional[int] = None,
                      input_path: Optional[str] = None,
                      output_path: str = "",
                      classes_to_detect: list = None,
                      csv_file_path: str = ""):
        """
        Processes a video for object detection and tracking.

        Args:
            camera (int, optional): The device id of the camera to be used as the video source.
            input_path (str): Path to the input video file.
            output_path (str, optional): Path to save the output video. If empty, video is not saved.
            classes_to_detect (list, optional): List of classes to detect and track.
            csv_file_path (str, optional): CSV path to save tracked info.
        """
        if camera is not None:
            video = Video(camera=camera, output_path=output_path)
        else:
            video = Video(input_path=input_path, output_path=output_path)

        for frame in video:
            self.current_frame_index += 1
            detections = self.process_frame(frame=frame, classes_to_detect=classes_to_detect)
            tracked_objects = self.tracker.update(detections=detections)
            if self.track_points == "centroid":
                norfair.draw_points(frame, detections)
            elif self.track_points == "bbox":
                norfair.draw_boxes(frame, detections)
            norfair.draw_tracked_objects(frame, tracked_objects, draw_labels=True)
            video.write(frame)

            cv2.imshow('Video', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        if csv_file_path:
            self.export_tracking_data_to_csv(csv_file_path)

        cv2.destroyAllWindows()

