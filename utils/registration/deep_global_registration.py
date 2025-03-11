import os
import sys
# Caminho absoluto para o repositório DeepGlobalRegistration
DGR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../external/DeepGlobalRegistration"))

# Adiciona o caminho ao sys.path
if DGR_PATH not in sys.path:
    sys.path.append(DGR_PATH)

import open3d as o3d
import numpy as np
from urllib.request import urlretrieve
from utils.decorators import measure_time
from external.DeepGlobalRegistration.core.deep_global_registration import DeepGlobalRegistration
from external.DeepGlobalRegistration.config import get_config

MODEL_URL: str = "http://node2.chrischoy.org/data/projects/DGR/ResUNetBN2C-feat32-3dmatch-v0.05.pth"
MODEL_PATH: str = "./ResUNetBN2C-feat32-3dmatch-v0.05.pth"

def download_model(model_url: str = MODEL_URL, model_path: str = MODEL_PATH) -> None:
    if not os.path.exists(MODEL_PATH):
        print("Baixando modelo...")
        urlretrieve(model_url, model_path)
        print("Download concluído!")
    return


@measure_time
def deep_global_registration(source_cloud: o3d.geometry.PointCloud,
                             target_cloud: o3d.geometry.PointCloud,
                             voxel_size: float,
                             verbose: bool = False) -> np.ndarray:
    """
    As features são processadas internamente (FCGF)
    """
    config = get_config()  # Falta baixar o modelo
    if config.weights is None:
        config.weights = MODEL_PATH
    dgr: DeepGlobalRegistration = DeepGlobalRegistration(config)
    dgr.use_icp = False
    dgr.voxel_size = voxel_size

    return dgr.register(source_cloud, target_cloud)
