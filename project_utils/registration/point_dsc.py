import json
import os
import sys

import numpy as np
import open3d as o3d
import torch
from easydict import EasyDict

from project_utils.point_cloud import FeatureMethod
from project_utils.utils_point_dsc import Snapshot

# Add PointDSC path to sys.path
POINT_DSC = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../external/PointDSC"))
if POINT_DSC not in sys.path:
    sys.path.append(POINT_DSC)

from external.PointDSC.models.PointDSC import PointDSC


def point_dsc(source_cloud: o3d.geometry.PointCloud,
              target_cloud: o3d.geometry.PointCloud,
              source_features: o3d.pipelines.registration.Feature,
              target_features: o3d.pipelines.registration.Feature,
              voxel_size: int | float,
              feature_method: FeatureMethod = FeatureMethod.FPFH,
              snapshot: Snapshot = Snapshot.SNAPSHOT_3DMATCH,
              verbose: bool = False,
              **kwargs) -> np.ndarray:
    """
    https://github.com/XuyangBai/PointDSC
    Não utilizou o voxel_size
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    if feature_method == FeatureMethod.FPFH:
        source_cloud = np.asarray(source_cloud.points)
        target_cloud = np.asarray(target_cloud.points)

        # feature ajustment
        source_features = np.array(source_features.data).T
        source_features = source_features / (np.linalg.norm(source_features, axis=1, keepdims=True) + 1e-6)

        target_features = np.array(target_features.data).T
        target_features = target_features / (np.linalg.norm(target_features, axis=1, keepdims=True) + 1e-6)
    elif feature_method == FeatureMethod.FCGF:
        pass
    else:
        raise ValueError(f"Invalid feature method: {feature_method}")

    config_path = f'./external/PointDSC/snapshot/{snapshot.value}/config.json'
    config = json.load(open(config_path, 'r'))
    config = EasyDict(config)

    model = PointDSC(
        in_dim=config.in_dim,
        num_layers=config.num_layers,
        num_channels=config.num_channels,
        num_iterations=config.num_iterations,
        ratio=config.ratio,
        sigma_d=config.sigma_d,
        k=config.k,
        nms_radius=config.inlier_threshold,
    ).to(device)
    miss = model.load_state_dict(
        torch.load(f'./external/PointDSC/snapshot/{snapshot.value}/models/model_best.pkl', map_location=device),
        strict=False)

    if verbose:
        print(miss)

    model.eval()

    # matching
    distance = np.sqrt(2 - 2 * (source_features @ target_features.T) + 1e-6)
    source_idx = np.argmin(distance, axis=1)
    source_dis = np.min(distance, axis=1)
    corr = np.concatenate([np.arange(source_idx.shape[0])[:, None], source_idx[:, None]], axis=-1)
    src_keypts = source_cloud[corr[:, 0]]
    tgt_keypts = target_cloud[corr[:, 1]]
    corr_pos = np.concatenate([src_keypts, tgt_keypts], axis=-1)
    corr_pos = corr_pos - corr_pos.mean(0)

    # outlier rejection
    data = {
        'corr_pos': torch.from_numpy(corr_pos)[None].to(device).float(),
        'src_keypts': torch.from_numpy(src_keypts)[None].to(device).float(),
        'tgt_keypts': torch.from_numpy(tgt_keypts)[None].to(device).float(),
        'testing': True,
    }
    res = model(data)

    return res['final_trans'][0].detach().cpu().numpy()
