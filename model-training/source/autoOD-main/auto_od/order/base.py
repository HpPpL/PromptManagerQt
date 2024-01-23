from abc import ABC

from mmdet.apis import DetInferencer


class Base:
    def __init__(self, model_config: str, checkpoint: str, device: str = "cpu"):
        self.model_config = model_config
        self.checkpoint = checkpoint
        self.device = device

    def load_model(self):
        return DetInferencer(model=self.model_config,
                             weights=self.checkpoint,
                             device=self.device)
        # maybe to hepler.py


