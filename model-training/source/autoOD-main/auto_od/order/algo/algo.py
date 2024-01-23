# # testing module
# import mmcv
# from mmdet.apis import inference_detector, init_detector
#
#
# def verify_order_and_visualize(video_path, config_file, checkpoint_file, desired_order):
#     model = init_detector(config_file, checkpoint_file, device='cuda:0')
#
#     video = mmcv.VideoReader(video_path)
#     first_appearances = {}
#     appearance_order = []
#
#     for frame_id, frame in enumerate(video):
#         result = inference_detector(model, frame)
#         draw_frame = frame.copy()
#
#         for bbox, label in zip(*result[0]):
#             object_type = model.CLASSES[label]
#             bbox_int = bbox.astype(int)
#
#             if object_type not in first_appearances:
#                 first_appearances[object_type] = frame_id
#                 appearance_order.append(object_type)
#                 print(f"Object '{object_type}' first appeared in frame {frame_id}")
#
#             color = (0, 255, 0) if appearance_order.index(object_type) == desired_order.index(object_type) else (255, 0, 0)
#             draw_frame = mmcv.imshow_bboxes(draw_frame, [bbox_int], colors=[color], top_k=1, thickness=2, show=False)
#
#         mmcv.imshow(draw_frame, wait_time=1)
#
#     mmcv.destroyAllWindows()
#     return first_appearances, appearance_order
#
#
# video_path = 'path/to/video.mp4'
# config_file = 'path/to/config.py'
# checkpoint_file = 'path/to/checkpoint.pth'
#
# desired_order = ["cat", "apple", "banana"]
#
# first_appearances, appearance_order = verify_order_and_visualize(video_path, config_file, checkpoint_file, desired_order)
# print("First appearances of objects:", first_appearances)
# print("Order of appearance:", appearance_order)
