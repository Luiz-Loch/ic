import boto3
import numpy as np
import os
import open3d as o3d
import sys
import torch
from enum import Enum
from tqdm import tqdm
from urllib.request import urlretrieve

# Add FCGF path to sys.path
FCGF_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../external/FCGF"))
if FCGF_PATH not in sys.path:
    sys.path.append(FCGF_PATH)

from external.FCGF.model.resunet import ResUNetBN2C
from external.FCGF.util.misc import extract_features


class DGRModels(Enum):
    """
    Enum class representing the models for Deep Global Registration.
    Each model contains URLs for external and S3 sources, and a local path.
    """
    DGR_3DMATCH = (
        "http://node2.chrischoy.org/data/projects/DGR/ResUNetBN2C-feat32-3dmatch-v0.05.pth",
        "https://benchmarks-ic.s3.us-east-1.amazonaws.com/models/DGR/ResUNetBN2C-feat32-3dmatch-v0.05.pth",
        "./models/DGR/ResUNetBN2C-feat32-3dmatch-v0.05.pth"
    )

    DGR_KITTI = (
        "http://node2.chrischoy.org/data/projects/DGR/ResUNetBN2C-feat32-kitti-v0.3.pth",
        "https://benchmarks-ic.s3.us-east-1.amazonaws.com/models/DGR/ResUNetBN2C-feat32-kitti-v0.3.pth",
        "./models/DGR/ResUNetBN2C-feat32-kitti-v0.3.pth"
    )

    def __init__(self, url_external: str, url_s3: str, path: str) -> None:
        """
        Initialize the model with URLs and local path.

        :param url_external: URL for external download
        :param url_s3: URL for S3 download
        :param path: Local path to save the model
        """
        self.url_external: str = url_external
        self.url_s3: str = url_s3
        self.path: str = path


class FCGFModels(Enum):
    """
    Enum class representing the models for FCGF.
    Each model contains URLs for external and S3 sources, and a local path.
    """
    FCGF_3DMATCH = (
        "https://node1.chrischoy.org/data/publications/fcgf/2019-08-16_19-21-47.pth",
        "https://benchmarks-ic.s3.us-east-1.amazonaws.com/models/FCGF/2019-08-16_19-21-47.pth",
        "./models/FCGF/2019-08-16_19-21-47.pth"
    )

    FCGF_KITTI = (
        "https://node1.chrischoy.org/data/publications/fcgf/KITTI-v0.3-ResUNetBN2C-conv1-5-nout32.pth",
        "https://benchmarks-ic.s3.us-east-1.amazonaws.com/models/FCGF/KITTI-v0.3-ResUNetBN2C-conv1-5-nout32.pth",
        "./models/FCGF/KITTI-v0.3-ResUNetBN2C-conv1-5-nout32.pth"
    )

    def __init__(self, url_external: str, url_s3: str, path: str) -> None:
        """
        Initialize the model with URLs and local path.

        :param url_external: URL for external download
        :param url_s3: URL for S3 download
        :param path: Local path to save the model
        """
        self.url_external: str = url_external
        self.url_s3: str = url_s3
        self.path: str = path


def compute_fcgf_feature(point_cloud: o3d.geometry.PointCloud,
                         voxel_size: float,
                         model: FCGFModels) -> tuple[np.ndarray, np.ndarray]:
    """
        https://github.com/chrischoy/FCGF/tree/master
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    checkpoint = torch.load(model.path)
    model = ResUNetBN2C(1, 16, normalize_feature=True, conv1_kernel_size=3, D=3)
    model.load_state_dict(checkpoint['state_dict'])
    model.eval()

    model = model.to(device)

    xyz_down, features = extract_features(
        model,
        xyz=np.array(point_cloud.points),
        voxel_size=voxel_size,
        device=device,
        skip_check=True)

    return xyz_down.astype(np.float32), features.detach().cpu().numpy()


def download_progress_hook_s3(t) -> callable:
    """
    create a hook to update the progress bar for S3 downloads.

    :param t: tqdm progress bar instance
    :return: Callback function for boto3
    """

    def inner(bytes_transferred) -> None:
        t.update(bytes_transferred)

    return inner


def download_progress_hook_urllib(t) -> callable:
    """
    create a hook to update the progress bar during urlretrieve download.

    :param t: tqdm progress bar instance
    :return: Inner function to update progress
    """

    def inner(blocks_transferred, block_size, total_size) -> None:
        if total_size > 0:
            t.total = total_size
            t.update(blocks_transferred * block_size - t.n)

    return inner


def download_model(model: DGRModels | FCGFModels, t) -> None:
    """
    download a model from a given URL and save it to the specified path.

    :param model:
    :param t: tqdm progress bar instance
    """
    bucket_name: str = "benchmarks-ic"
    s3 = boto3.client('s3')

    # Create the directory if it does not exist
    os.makedirs(os.path.dirname(model.path), exist_ok=True)

    print(f"Downloading model {model.name}...")
    key: str = '/'.join(model.url_s3.split('/')[3:])
    print(f"Downloading from S3 bucket `{bucket_name}` file `{key}`...")
    try:
        s3.download_file(bucket_name, key, model.path, Callback=download_progress_hook_s3(t))
        print(f"\nDownload complete: {model.path}")
        return
    except Exception as e:
        print(f"\nFailed to download from {model.url_s3}: {e}")

    print(f"Downloading from {model.url_external}...")
    try:
        urlretrieve(model.url_external, model.path, reporthook=download_progress_hook_urllib(t))
        print(f"\nDownload complete: {model.path}")
        return
    except Exception as e:
        print(f"\nFailed to download from {model.url_external}: {e}")


def download_models() -> None:
    """
    """
    print("Downloading models...")
    # for model in DeepGlobalRegistrationModels:
    for model in list(DGRModels) + list(FCGFModels):
        if not os.path.exists(model.path):
            print(f"Model {model.name} not found locally. Starting download...")
            with tqdm(unit='B', unit_scale=True, desc=model.name) as t:
                download_model(model, t)
        else:
            print(f"Model {model.name} already exists.")
