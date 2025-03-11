import os
import sys

# Caminho absoluto para o repositório DeepGlobalRegistration
DGR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../external/DeepGlobalRegistration"))

# Adiciona o caminho ao sys.path
if DGR_PATH not in sys.path:
    sys.path.append(DGR_PATH)

from enum import Enum
import open3d as o3d
import numpy as np
from urllib.request import urlretrieve
from utils.decorators import measure_time
from external.DeepGlobalRegistration.core.deep_global_registration import DeepGlobalRegistration
from external.DeepGlobalRegistration.config import get_config


class Models(Enum):
    DGR_3DMATCH = (
        "http://node2.chrischoy.org/data/projects/DGR/ResUNetBN2C-feat32-3dmatch-v0.05.pth",
        "./ResUNetBN2C-feat32-3dmatch-v0.05.pth"
    )
    DGR_KITTI = (
        "http://node2.chrischoy.org/data/projects/DGR/ResUNetBN2C-feat32-kitti-v0.3.pth",
        "./ResUNetBN2C-feat32-kitti-v0.3.pth"
    )

    def __init__(self, url, path):
        self.url = url
        self.path = path


def download_models() -> None:
    """"
    """
    for model in Models:
        if not os.path.exists(model.path):
            print(f"Baixando {model.name}...")
            urlretrieve(model.url, model.path)
            print(f"Download concluído: {model.path}")
        else:
            print(f"{model.name} já está presente.")


@measure_time
def deep_global_registration(source_cloud: o3d.geometry.PointCloud,
                             target_cloud: o3d.geometry.PointCloud,
                             voxel_size: float,
                             verbose: bool = False,
                             model: Models = Models.DGR_3DMATCH) -> np.ndarray:
    """
    São informadas as nuvens completas
    As features são processadas internamente (FCGF)
    """
    config = get_config()  # Falta baixar o modelo
    if config.weights is None:
        config.weights = model.path
    dgr: DeepGlobalRegistration = DeepGlobalRegistration(config)
    dgr.use_icp = False
    dgr.voxel_size = voxel_size

    return dgr.register(source_cloud, target_cloud)
