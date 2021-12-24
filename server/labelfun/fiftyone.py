import json
import math
import os

import fiftyone as fo
import requests
from flask import current_app

from labelfun.models import TaskType
from labelfun.models.task import Task


def export_task(task: Task, export_type: str):
    # save entities to temp
    export_dir = current_app.config['EXPORT_DIRECTORY']
    export_zip = os.path.join(export_dir,
                              str(task.id) + '_' + export_type + '.zip')
    if os.path.isfile(export_zip):
        return export_zip

    types = {
        TaskType.IMAGE_CLS: {
            'fiftyone': fo.types.FiftyOneImageClassificationDataset
        },
        TaskType.IMAGE_SEG: {
            'cvat': fo.types.CVATImageDataset,
            'coco': fo.types.COCODetectionDataset,
            'voc': fo.types.VOCDetectionDataset,
            'kitti': fo.types.KITTIDetectionDataset
        },
        TaskType.VIDEO_SEG: {
            'cvat': fo.types.CVATVideoDataset
        }
    }
    if export_type not in types[task.type].keys():
        return None

    temp_dir = os.path.join(export_dir, 'temp')
    if not os.path.isdir(export_dir):
        os.mkdir(export_dir)
    if not os.path.isdir(temp_dir):
        os.mkdir(temp_dir)
    domain = current_app.config['QINIU_BUCKET_DOMAIN']
    for entity in task.entities:
        url = domain + entity.key
        r = requests.get(url, allow_redirects=True)
        pathname = os.path.join(temp_dir, entity.path)
        open(pathname, 'wb').write(r.content)

    if fo.dataset_exists(task.name):
        dataset = fo.load_dataset(task.name)
        dataset.delete()
    dataset = fo.Dataset(task.name)

    if task.type == TaskType.IMAGE_CLS:
        for entity in task.entities:
            sample = fo.Sample(os.path.join(temp_dir, entity.path))
            labels = json.loads(entity.annotation)
            sample['ground_truth'] = fo.Classifications(classifications=[
                fo.Classification(label=label) for label in labels
            ])
            dataset.add_sample(sample)

    elif task.type == TaskType.IMAGE_SEG:
        for entity in task.entities:
            sample = fo.Sample(os.path.join(temp_dir, entity.path))
            boxes = json.loads(entity.annotation)
            sample['ground_truth'] = fo.Detections(detections=[
                fo.Detection(label=box['label'],
                             bounding_box=box['bbox']) for box in boxes
            ])
            dataset.add_sample(sample)

    else:  # VIDEO_SEG
        for entity in task.entities:
            sample = fo.Sample(os.path.join(temp_dir, entity.path))
            objects = json.loads(entity.annotation)
            for index, obj in enumerate(objects):
                def add_ground_truth(frame_number, bbox):
                    frame = sample[frame_number]
                    if not frame.has_field('ground_truth'):
                        frame['ground_truth'] = fo.Detections(
                            detections=[])
                    frame['ground_truth'].detections.append(
                        fo.Detection(label=obj['label'], bounding_box=bbox)
                    )

                trajectory = obj['trajectory']
                # real frame count
                real_fc = json.loads(entity.meta_data)['total_frame_count']
                # real frame numbers of each snapshot
                real_fns = [min(math.ceil((snapshot['frame_number'] - 1) *
                                          real_fc / entity.frame_count) + 1,
                                real_fc) for snapshot in trajectory]
                # frame numbers of each snapshot
                fns = [snapshot['frame_number'] for snapshot in trajectory]

                for j, snapshot in enumerate(trajectory):
                    # If this and next snapshots are adjacent
                    if j < len(trajectory) - 1 and fns[j + 1] - fns[j] == 1:
                        bbox_prev = trajectory[j]['bbox']
                        bbox_next = trajectory[j + 1]['bbox']
                        for real_fn in range(real_fns[j], real_fns[j + 1]):
                            bbox_this = [(real_fn - real_fns[j]) * (n - m) / (
                                    real_fns[j + 1] - real_fns[j]) + m for
                                         m, n in zip(bbox_prev, bbox_next)]
                            print(f"bbox for frame #{real_fn}:", bbox_this)
                            add_ground_truth(real_fn, bbox_this)
                    else:
                        add_ground_truth(real_fns[j], snapshot['bbox'])

            dataset.add_sample(sample)

    dataset_type = types[task.type][export_type]
    field = 'ground_truth'
    if task.type != TaskType.VIDEO_SEG:
        dataset.export(export_dir=export_zip, dataset_type=dataset_type,
                       label_field=field, export_media=True)
    else:
        dataset.export(export_dir=export_zip, dataset_type=dataset_type,
                       frame_labels_field=field, export_media=True)

    dataset.delete()
    for entity in task.entities:
        pathname = os.path.join(temp_dir, entity.path)
        os.remove(pathname)

    return export_zip
