from typing import Tuple

import onnx
import onnxruntime as ort
import torch
from mmdet.apis import init_detector

DEVICE = 'cuda:0' if torch.cuda.is_available() else 'cpu'


class ONNXExporter:
    def __init__(self,
                 config_file: str,
                 checkpoint_file: str,
                 input_shape: Tuple = (1, 3, 640, 640),
                 device=DEVICE):
        """
        Initialize the ONNXExporter.

        Args:
            config_file (str): Path to the configuration file.
            checkpoint_file (str): Path to the checkpoint file.
            input_shape (tuple): Shape of the input tensor. Default is (1, 3, 640, 640).
            device (str): Device to use for inference ('cuda:0' for GPU, 'cpu' for CPU).
        """
        self.config_file = config_file
        self.checkpoint_file = checkpoint_file
        self.input_shape = input_shape
        self.device = device
        self.model = self.load_model()

    def load_model(self):
        """
        Load the model from the given configuration and checkpoint.

        Returns:
            model: The loaded PyTorch model.
        """
        model = init_detector(self.config_file, self.checkpoint_file, device=self.device)
        model.eval()
        return model

    def export_to_onnx(self, onnx_file):
        """
        Export the PyTorch model to ONNX format.

        Args:
            onnx_file (str): Path to save the ONNX model.
        """
        dummy_input = torch.randn(self.input_shape).to(self.device)
        torch.onnx.export(self.model,
                          dummy_input,
                          onnx_file,
                          input_names=['input'],
                          output_names=['output'],
                          opset_version=11,
                          dynamic_axes={'input': {0: 'batch_size'},
                                        'output': {0: 'batch_size'}})
        print(f"Model exported to {onnx_file}")

    @staticmethod
    def run_inference(onnx_file, input_tensor):
        """
        Run inference using the ONNX model.

        Args:
            onnx_file (str): Path to the ONNX model.
            input_tensor (torch.Tensor): Input tensor for the model.

        Returns:
            outputs (numpy.ndarray): Model outputs.
        """
        ort_session = ort.InferenceSession(onnx_file)

        def to_numpy(tensor):
            return tensor.detach().cpu().numpy() if tensor.requires_grad else tensor.cpu().numpy()

        ort_inputs = {ort_session.get_inputs()[0].name: to_numpy(input_tensor)}
        ort_outs = ort_session.run(None, ort_inputs)

        return ort_outs

    @staticmethod
    def check_onnx_model(onnx_file):
        """
        Check the ONNX model for validity.

        Args:
            onnx_file (str): Path to the ONNX model.
        """
        onnx.checker.check_model(onnx_file)
        print(f"{onnx_file} is a valid ONNX model")


