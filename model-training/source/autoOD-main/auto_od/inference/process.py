import cv2
import torch

from auto_od.inference.detect_objects import Inference


class VideoObjectDetector:
    """
    A class to perform object detection on video streams using models from the mmdetection library.

    This class uses a model initialized with a configuration file and a checkpoint file to detect objects
    in each frame of a video stream.

    Attributes:
        config_file (str): Path to the model's configuration file.
        checkpoint_file (str): Path to the model's checkpoint file.
        device (str): The device to run the model on (e.g., 'cuda:0').
    """

    def __init__(self, config_file: str, checkpoint_file: str, device: str = 'cuda:0'):
        """
        Initializes the VideoObjectDetector class with the model's configuration and checkpoint files.

        Args:
            config_file (str): Path to the model's configuration file.
            checkpoint_file (str): Path to the model's checkpoint file.
            device (str, optional): The device to run the model on. Defaults to 'cuda:0'.
        """
        if device is not None and "cuda" in device and not torch.cuda.is_available():
            raise Exception("Selected device='{0}', but cuda is not available to Pytorch.".format(device))
        elif device is None:
            device = "cuda:0" if torch.cuda.is_available() else "cpu"

        self.device = device
        self.model = Inference(config_file=config_file, checkpoint_file=checkpoint_file)

    def process_frame(self, frame):
        """
        Processes a single frame using the model and returns the frame with detected objects.

        Args:
            frame (np.array): An image frame from a video stream.

        Returns:
            np.array: The input frame with detected objects visualized.
        """
        result = self.model.process(frame=frame, return_vis=True)
        return result['visualization'][0]

    def start_video_stream(self, source=0):
        """
        Starts a video stream and performs object detection on each frame.
        Args:
            source (int, str): Source to perform object detection. 0 for Webcam
        """
        cap = cv2.VideoCapture(source)  # Use 0 for webcam

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            processed_frame = self.process_frame(frame)
            cv2.imshow('Video', processed_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

