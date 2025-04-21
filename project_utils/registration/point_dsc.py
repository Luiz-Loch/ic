import json
import numpy as np
import open3d as o3d
import os
import sys
import torch
from easydict import EasyDict
from project_utils.decorators import measure_time
from project_utils.utils_point_dsc import Snapshot

# Add PointDSC path to sys.path
POINT_DSC = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../external/PointDSC"))
if POINT_DSC not in sys.path:
    sys.path.append(POINT_DSC)

from external.PointDSC.models.PointDSC import PointDSC


@measure_time
def point_dsc(source_cloud: np.ndarray,
              target_cloud: np.ndarray,
              source_features: o3d.pipelines.registration.Feature,
              target_features: o3d.pipelines.registration.Feature,
              verbose: bool = False,
              snapshot: Snapshot = Snapshot.SNAPSHOT_3DMATCH) -> np.ndarray:
    """
    https://github.com/XuyangBai/PointDSC
    Não utilizou o voxel_size
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

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

    # feature ajustment
    _source_features = np.array(source_features.data).T
    _source_features = _source_features / (np.linalg.norm(_source_features, axis=1, keepdims=True) + 1e-6)

    _target_features = np.array(target_features.data).T
    _target_features = _target_features / (np.linalg.norm(_target_features, axis=1, keepdims=True) + 1e-6)

    # matching
    distance = np.sqrt(2 - 2 * (_source_features @ _target_features.T) + 1e-6)
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
