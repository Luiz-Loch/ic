from enum import Enum

import numpy as np
import open3d as o3d

from .data_loader import get_datasets, kitti_read_gt_log


def load_dataset(dataset_type, verbose: bool = False) -> list[tuple[str, str, np.ndarray]]:
    if dataset_type == DataSetType.KITTI:
        return kitti_read_gt_log("./data/KITTI", verbose=verbose)

    elif dataset_type == DataSetType.DEMO:
        point_clouds = o3d.data.DemoICPPointClouds("./data/demo")
        return [(point_clouds.paths[0], point_clouds.paths[1], None)]

    elif dataset_type == DataSetType.ALL:
        datasets = []
        for ds_type in [DataSetType._3DMATCH, DataSetType.ETH, DataSetType.KITTI]:
            datasets.extend(load_dataset(ds_type))
        return datasets

    else:
        return get_datasets(f"./data/{dataset_type.value}", verbose=verbose)


class DataSetType(Enum):
    _3DMATCH = '3DMatch'
    ETH = 'ETH'
    KITTI = 'KITTI'
    DEMO = 'demo'
    ALL = 'all'

    @property
    def datasets(self):
        return load_dataset(self)


def get_dataset_info(ply_path: str, verbose: bool = False) -> tuple[str, str, str]:
    """
    Extracts dataset, scene, and frame information from the file path.

    Parameters:
    ply_path (str): The path to the point cloud file.

    Returns:
    tuple[str, str, str]: A tuple containing dataset name, scene name, and frame number.
    """
    parts = ply_path.split('/')
    if verbose:
        print(parts)

    if '3DMatch' or 'ETH' in parts:
        dataset: str = parts[2]
        scene: str = parts[3]
        frame: str = parts[-1]
    elif 'KITTI' in parts:
        dataset: str = parts[2]
        scene: str = parts[3]
        frame: str = parts[-1]
    return dataset, scene, frame
