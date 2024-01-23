
## Installation

```angular2html
Python Version 3.9
```

#### For mim installation
```commandline
pip install -U openmim
mim install "mmengine>=0.7.0"
```
#### MMCV (Ex. for MacOS)
Different OS installation for MMCV: https://mmcv.readthedocs.io/en/1.x/get_started/build.html.
Error -> pip install future tensorboard.
```commandline
git clone https://github.com/open-mmlab/mmcv.git
cd mmcv

pip install -r requirements/optional.txt
MMCV_WITH_OPS=1 pip install -e .
python .dev_scripts/check_installation.py
```
#### MMDetection
```commandline
rm -rf mmdetection
git clone https://github.com/open-mmlab/mmdetection.git
cd mmdetection
pip install -e .
```

## Test Environment
```python
from auto_od.check.env import EnvironmentCollector


env_collector = EnvironmentCollector()
env_collector.display_env_info()
```

## Dataset Preprocessing
### Convert PascalVoc to COCO



#### Ex. initial structure 1
- **/root**
  - **/src**
    - **/cats_dogs**
      - `1.jpg`
      - `1.xml`
      - `2.jpg`
      - `2.xml`
      - ...

```python
# convert
from auto_od.data_preprocess.converter.xml_to_coco import XMLToCocoConverter

dataset_dir = "/root/src/cats_dogs"
new_dataset_dir = "/root/src/cats_dogs_coco/data"
new_annotation_file = "/root/src/cats_dogs_coco/cats_dogs.json"
xml_to_coco = XMLToCocoConverter(dataset_dir,
                                 new_dataset_dir)
xml_to_coco.convert(new_annotation_file)                                 

# dataset info
xml_to_coco.stats_info("train.json",
                       "test.json")
```

#### Result structure after convertation
- **/root**
  - **/src**
    - **/cats_dogs**
      - `1.jpg`
      - `1.xml`
      - `2.jpg`
      - `2.xml`
      - ...
    - **/cats_dogs_coco**
      - **/data**
        - 1.jpg
        - 2.jpg
        - ...
      - `cats_dogs.json`

### Balance Dataset into test and train with classes
```python
# split dataset accordingly classes distribution from "Result structure"
from auto_od.data_preprocess.split.coco import BalancedCOCOSplitter
import os

annotations_file_path = "/root/src/cats_dogs_coco/cats_dogs.json"
curr_dataset_dir = "/root/src/cats_dogs_coco/data"
future_dataset_dir = "/root/src/cat_dog_data"
output_train_json = os.path.join(future_dataset_dir, "train.json")
output_test_json = os.path.join(future_dataset_dir, "test.json")

output_train_dir = os.path.join(future_dataset_dir, "train")
output_test_dir = os.path.join(future_dataset_dir, "test")


splitter = BalancedCOCOSplitter(
    coco_file=annotations_file_path,
    image_dir=curr_dataset_dir)

splitter(output_train_dir=output_train_dir,
         output_train_json=output_train_json,
         output_test_dir=output_test_dir,
         output_test_json=output_test_json)
```
Structure after splitting (*)
- **/root**
  - **/src**

    - **/cat_dog**
      - **/test**
        - 1.jpg
        - 3.jpg
        - ...
      - **/train**
        - 2.jpg
        - 4.jpg
        - ...
      - `test.json`
      - `train.json`

In case initial (*) structure splitting will be:
```python
from auto_od.data_preprocess.split.coco import BalancedCOCOSplitter, join_coco_annotations
import os


join_coco_annotations('/root/src/cat_dog/train.json',
                      '/root/src/cat_dog/test.json',
                      '/root/src/cat_dog/output_file.json')

annotations_file_path = "/root/src/cat_dog/output_file.json"
curr_dataset_dir = "/root/src/cat_dog/images"
future_dataset_dir = "/root/src/cat_dog_result_data"
output_train_json = os.path.join(future_dataset_dir, "train.json")
output_test_json = os.path.join(future_dataset_dir, "test.json")

output_train_dir = os.path.join(future_dataset_dir, "train")
output_test_dir = os.path.join(future_dataset_dir, "test")


splitter = BalancedCOCOSplitter(
    coco_file=annotations_file_path,
    image_dir=curr_dataset_dir)

splitter(output_train_dir=output_train_dir,
         output_train_json=output_train_json,
         output_test_dir=output_test_dir,
         output_test_json=output_test_json)

# check dataset with annotations
from auto_od.check.dataset import ImageAnnotationViewer
image_folder = '/root/src/dataset_cd/train'
json_file = '/root/src/dataset_cd/train.json'
viewer = ImageAnnotationViewer(image_folder, json_file)
```


## Environment preparation
1. Fill in settings.yaml file. Ex. 
```puml
mmdet_dir: "/Users/elinachertova/PycharmProjects/autoODv2/mmdetection"
dataset_type: "CocoDataset"
task: "Object Detection"
dataset_dir: "/Users/elinachertova/PycharmProjects/autoODv2/data/dataset_cd"
base_dir: "/Users/elinachertova/PycharmProjects/autoODv2"
epoch_number: 100
```
2. Prepare training environment
```python 
# generate training folder with weights, base config
from auto_od.metafetch.downloader import MetaFileDownloader


downloader = MetaFileDownloader(settings_path="/root/src/settings.yaml")
downloader(model_name="rtmdet_s_8xb32-300e_coco")
```
3. Generate prepared config.py file to train model
```python
from auto_od.config.builder import ModelConfig


model_conf = ModelConfig(settings_path="/root/src/settings.yaml")
model_conf.set_custom_params()
```
4. (Optional) Find the best aspect ratios and anchor sizes 
```python
from auto_od.data_preprocess.analyze.dataset.analyzer import Analyzer


config_file = '/Users/elinachertova/PycharmProjects/autoODv2/runs_archive/train5/configs/rtmdet_s_8xb32-300e_coco_custom.py'  # Replace with your config file path

analyser = Analyzer(settings_path="/root/src/settings.yaml",
                    annotation_path='/root/src/data/dataset_cd/train.json',
                    dataset_dir='/root/src/data/dataset_cd')

# ex
img_dim = 640
anchor_size_suggestions = analyser.suggest_config(img_dim, feature_map_scales)
print("Anchor size suggestions:", anchor_size_suggestions)

# feature_map_scales is taken from the config or this way
from auto_od.helper.dataset_analyzer import calculate_feature_map_scale
feature_map_scales = calculate_feature_map_scale(config_file=config_file, img_w=640, img_h=640)
print("Feature map scales:", feature_map_scales)
```
5. Train model
```python
from auto_od.train.trainer import DetectorTrainer


detector_trainer = DetectorTrainer(
        set_random_seed=0,
        config_path='/root/src/runs_archive/train5/configs/rtmdet_s_8xb32-300e_coco_custom.py',
        settings_path="/root/src/settings.yaml"
    )
detector_trainer.train()
```
7. Inference
```python
# On dataset
from auto_od.inference.detect_objects import Inference
import os


config = '/root/src/runs_archive/train1/configs/rtmdet_l_8xb32-300e_coco_custom.py'
checkpoint = '/root/src/runs_archive/train1/models/best_coco_bbox_mAP_epoch_250.pth'

list_images = ['1.jpg', '2.jpg', '3.jpg', '4.jpg']

inf = Inference(config_file=config, checkpoint_file=checkpoint)

base_path = "/root/src/data"

for i in list_images:
    img = os.path.join(base_path, i)
    inf.save(img, out_dir="/root/src/data/output")

# Video Stream
from auto_od.inference.process import VideoObjectDetector


config = '/root/src/runs_archive/train1/configs/rtmdet_l_8xb32-300e_coco_custom.py'
checkpoint = '/root/src/runs_archive/train1/models/best_coco_bbox_mAP_epoch_250.pth'

detector = VideoObjectDetector(config, checkpoint)
detector.start_video_stream(source=0)

```

8. Tracker

```python
from auto_od.track.tracker import ObjectTracker


tracker = ObjectTracker(
    model_path='/.../best_coco_bbox_mAP_epoch_150.pth',
    config_path='/.../rtmdet_m_8xb32-300e_coco_custom.py',
    device='cpu',
    track_points='bbox',
    max_track_distance=30,
    conf_thresh=0.35
)
tracker.process_video(input_path='/.../video.mp4')
```

9. Check objects' order

```python
from auto_od.track.tracker import ObjectTracker
from auto_od.order.tracker_analyzer import ObjectOrderAnalyzer

tracker = ObjectTracker(
    model_path='/.../best_coco_bbox_mAP_epoch_150.pth',
    config_path='/.../rtmdet_m_8xb32-300e_coco_custom.py',device='cpu',
    track_points='bbox',
    max_track_distance=30,
    conf_thresh=0.5,
    past_detections_length=30,
    hit_counter_max=20
)

order_analyzer = ObjectOrderAnalyzer(tracker, expected_order=["cup", "apple", "orange"])
order_analyzer.process_video("/.../order.mp4",
                             output_path="/.../order_out.mp4",
                             csv_file_path="/../order.csv")


```

10. (Optional) Export to ONNX
```python
from auto_od.convert.export_to_onnx import ONNXExporter
import torch


config_file = '/root/src/runs_archive/train5/configs/rtmdet_s_8xb32-300e_coco_custom.py'  # Replace with your config file
checkpoint_file = '/root/src/runs_archive/train5/models/epoch_98.pth'  # Replace with your checkpoint file
onnx_file = 'output_model.onnx'
input_shape = (1, 3, 640, 640)

exporter = ONNXExporter(config_file=config_file, checkpoint_file=checkpoint_file, input_shape=input_shape)
exporter.export_to_onnx(onnx_file)
exporter.check_onnx_model(onnx_file)

dummy_input = torch.randn(input_shape)
outputs = exporter.run_inference(onnx_file, dummy_input)
print(outputs)
```

11. (In development) Grid Search
```python

from auto_od.select.hyperparams.grid_search import GridSearch


search_space = {
    'optim_wrapper.optimizer.lr': [0.01, 0.001],
    'optim_wrapper.optimizer.type': ['SGD', 'AdamW'],
    'train_dataloader.batch_size': [8, 16, 32]
}


base_config_path = '/root/src/run_archive/train2/configs/rtmdet_s_8xb32-300e_coco_custom.py'
checkpoint_dir = '/root/src/run_archive/train2/checkpoints'
settings_path = "/root/src/settings.yaml"
grid_searcher = GridSearch(base_config_path=base_config_path, search_space=search_space, settings_path=settings_path)
best_cfg_options, best_performance = grid_searcher.grid_search(checkpoint_dir)
print("Best configuration options:", best_cfg_options)
print("Best performance:", best_performance)
```