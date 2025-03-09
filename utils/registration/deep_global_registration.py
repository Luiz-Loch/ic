import open3d as o3d
import numpy as np
from utils.decorators import measure_time
from external.DeepGlobalRegistration.core.deep_global_registration import DeepGlobalRegistration
from external.DeepGlobalRegistration.config import get_config


@measure_time
def deep_global_registration(source_cloud: o3d.geometry.PointCloud,
                             target_cloud: o3d.geometry.PointCloud,
                             voxel_size: float,
                             verbose: bool = False) -> np.ndarray:
    """
    As features são processadas internamente (FCGF)
    """
    config = get_config()  # Falta baixar o modelo
    dgr: DeepGlobalRegistration = DeepGlobalRegistration(config)
    dgr.use_icp = False
    dgr.voxel_size = voxel_size

    return dgr.register(source_cloud, target_cloud)
