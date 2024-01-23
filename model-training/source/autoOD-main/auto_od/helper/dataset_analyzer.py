import torch
from mmdet.apis import init_detector


def calculate_feature_map_scale(config_file: str, img_w: int, img_h: int, checkpoint_file: str = None) -> list:
    """
    Calculates the scale of the feature map.

    Args:
        config_file (str): Path to the configuration file of the model.
        img_w (int): Width of the input image.
        img_h (int): Height of the input image.
        checkpoint_file (str, optional): Path to the checkpoint file for model weights. Defaults to None.

    Returns:
        list: A list of scales for each feature map layer.
    """

    device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
    model = init_detector(config_file, checkpoint_file, device=device)
    dummy_img = torch.rand(1, 3, img_h, img_w).to(device)

    with torch.no_grad():
        if hasattr(model, 'extract_feat'):
            feature_maps = model.extract_feat(dummy_img)
        else:
            feature_maps = [model(dummy_img)]
    scales = [dummy_img.shape[-1] / feature_map.shape[-1] for feature_map in feature_maps]
    return scales

