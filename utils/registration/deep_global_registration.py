import os
import sys
import open3d as o3d
import numpy as np
from utils.decorators import measure_time
from utils.utils_deep_global_registration import DeepGlobalRegistrationModels

# Add DeepGlobalRegistration path to sys.path
DGR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../external/DeepGlobalRegistration"))
if DGR_PATH not in sys.path:
    sys.path.append(DGR_PATH)

from external.DeepGlobalRegistration.core.deep_global_registration import DeepGlobalRegistration
from external.DeepGlobalRegistration.config import get_config


@measure_time
def deep_global_registration(source_cloud: o3d.geometry.PointCloud,
                             target_cloud: o3d.geometry.PointCloud,
                             voxel_size: float,
                             verbose: bool = False,
                             model: DeepGlobalRegistrationModels = DeepGlobalRegistrationModels.DGR_3DMATCH) -> np.ndarray:
    """
    São informadas as nuvens completas
    As features são processadas internamente (FCGF)
    """
    config = get_config()
    if config.weights is None:
        config.weights = model.path
    dgr: DeepGlobalRegistration = DeepGlobalRegistration(config)
    dgr.use_icp = False
    dgr.voxel_size = voxel_size

    return dgr.register(source_cloud, target_cloud)
