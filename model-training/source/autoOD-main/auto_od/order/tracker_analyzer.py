import cv2
import norfair
import numpy as np
from norfair import Video
from typing import Optional


class ObjectOrderAnalyzer:
    """
    Analyzes the order of detected objects in video frames and marks them based on the correctness of the sequence.

    Attributes:
        tracker (ObjectTracker): An instance of ObjectTracker for tracking objects in video frames.
        expected_order (list): The expected sequence of object labels in the correct order.
        color_incorrect_order (tuple): RGB color code for drawing boxes of objects in incorrect order.
        color_correct_order (tuple): RGB color code for drawing boxes of objects in correct order.
        current_index (int): Tracks the current index of the object being processed in the expected sequence.
        object_id_to_last_label (dict): Maps object IDs to their last known labels.
        correct_order_so_far (bool): Indicates whether the sequence of objects has been correct so far.
        past_to_pass (int): Counter to allow some margin for tracking errors.
        order_correctness (dict): Stores the correctness of the order for each tracked object.
    """
    def __init__(self,
                 tracker,
                 expected_order: list[str],
                 color_incorrect_order: tuple = (39, 8, 191),
                 color_correct_order: tuple = (12, 118, 61)):
        """
        Initializes the ObjectOrderAnalyzer.

        Args:
            tracker (ObjectTracker): An instance of ObjectTracker.
            expected_order (list): A list of expected object labels in the correct order.
            color_incorrect_order (tuple): Color for the box around objects in the incorrect order.
            color_correct_order (tuple): Color for the box around objects in the correct order.
        """
        self.tracker = tracker
        self.expected_order = expected_order
        self.current_index = 0
        self.object_id_to_last_label = {}
        self.correct_order_so_far = True
        self.past_to_pass = 0
        self.order_correctness = {}
        self.color_incorrect_order = color_incorrect_order
        self.color_correct_order = color_correct_order

    def analyze_order(self,
                      tracked_objects: list[norfair.tracker.TrackedObject],
                      frame: np.ndarray,
                      detections: list[norfair.Detection]):
        """
        Analyzes the current order of objects and updates the frame with color-coded boxes.

        Args:
            tracked_objects (list of norfair.TrackedObject): List of tracked objects in the current frame.
            frame (numpy.ndarray): The current video frame.
            detections (list of norfair.Detection): List of detections in the current frame.

        Returns:
            numpy.ndarray: Whether the order of objects is correct up to the current frame.
        """
        tracked_labels = [obj.label for obj in tracked_objects]
        ids = [obj.id for obj in tracked_objects]

        for label, id_ in zip(tracked_labels, ids):
            if id_ == max(ids):
                try:
                    expected_label = self.expected_order[id_ - 1]
                    current_label = label
                    if self.order_correctness.get(id_) is None:
                        self.order_correctness[id_] = True

                    try:
                        if not self.order_correctness[id_ - 1]:
                            self.order_correctness[id_] = False
                    except KeyError:
                        pass

                    if current_label != expected_label:
                        self.order_correctness[id_] = False
                        self.past_to_pass += 1
                        if self.past_to_pass > int(self.tracker.hit_counter_max / 2):
                            self.correct_order_so_far = False
                except IndexError:
                    self.order_correctness[id_] = False

        order_status = "" if self.correct_order_so_far else ""
        frame = cv2.putText(frame, order_status, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (191, 8, 39), 2)

        frame = self.draw_boxes_with_labels(frame, detections, list(self.order_correctness.values()), ids)

        return frame

    def draw_boxes_with_labels(self,
                               frame: np.ndarray,
                               detections: list[norfair.Detection],
                               is_correct: list[bool], ids: list):
        """
        Draws bounding boxes with labels on the frame, color-coded based on the correctness of the object order.

        Args:
            frame (numpy.ndarray): The current video frame.
            detections (list of norfair.Detection): List of detections in the current frame.
            is_correct (list of bool): List indicating the correctness of order for each object.
            ids

        Returns:
            numpy.ndarray: The updated video frame with color-coded bounding boxes and labels.

        """
        for k, detection in enumerate(detections):
            x1, y1 = detection.points[0]
            x2, y2 = detection.points[1]
            class_name = detection.label
            try:
                box_color = self.color_correct_order if is_correct[ids[k] - 1] is True else self.color_incorrect_order
            except IndexError:
                box_color = (71, 178, 245)

            frame = cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), box_color, 2)
            cv2.putText(frame, class_name, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, box_color, 2)
        return frame

    def process_video(self,
                      camera: Optional[int] = None,
                      input_path: Optional[str] = None,
                      output_path: str = "",
                      classes_to_detect: list = None,
                      csv_file_path: str = ""):
        """
        Processes a video, analyzing the order of detected objects and marking them accordingly.

        Args:
            camera (int, optional): The device id of the camera to be used as the video source.
            input_path (str, optional): Path to the input video file.
            output_path (str, optional): Path to save the output video. If empty, the video is not saved.
            classes_to_detect (list, optional): List of class labels to detect and analyze. If None, all classes are considered.
            csv_file_path (str, optional): CSV path to save tracked info.
        """
        if camera is not None:
            video = Video(camera=camera, output_path=output_path)
        else:
            video = Video(input_path=input_path, output_path=output_path)

        for frame in video:
            self.tracker.current_frame_index += 1
            detections = self.tracker.process_frame(frame, classes_to_detect=classes_to_detect)
            tracked_objects = self.tracker.tracker.update(detections=detections)
            self.tracker.store_tracked_objects(tracked_objects)
            frame = self.analyze_order(tracked_objects, frame, detections)

            norfair.draw_tracked_objects(frame, tracked_objects, draw_labels=True)
            video.write(frame)

            cv2.imshow('Video', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        if csv_file_path:
            self.tracker.export_tracking_data_to_csv(csv_file_path)

        cv2.destroyAllWindows()
