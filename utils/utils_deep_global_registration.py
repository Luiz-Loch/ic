import os
import boto3
from enum import Enum
from tqdm import tqdm
from urllib.request import urlretrieve


class DeepGlobalRegistrationModels(Enum):
    """
    Enum class representing the models for Deep Global Registration.
    Each model contains URLs for external and S3 sources, and a local path.
    """
    DGR_3DMATCH = (
        "http://node2.chrischoy.org/data/projects/DGR/ResUNetBN2C-feat32-3dmatch-v0.05.pth",
        "https://benchmarks-ic.s3.us-east-1.amazonaws.com/deep_global_registration/models/ResUNetBN2C-feat32-3dmatch-v0.05.pth",
        "./ResUNetBN2C-feat32-3dmatch-v0.05.pth"
    )

    DGR_KITTI = (
        "http://node2.chrischoy.org/data/projects/DGR/ResUNetBN2C-feat32-kitti-v0.3.pth",
        "https://benchmarks-ic.s3.us-east-1.amazonaws.com/deep_global_registration/models/ResUNetBN2C-feat32-kitti-v0.3.pth",
        "./ResUNetBN2C-feat32-kitti-v0.3.pth"
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


def download_progress_hook_s3(t) -> callable:
    """
    Create a hook to update the progress bar for S3 downloads.

    :param t: tqdm progress bar instance
    :return: Callback function for boto3
    """

    def inner(bytes_transferred) -> None:
        t.update(bytes_transferred)

    return inner


def download_progress_hook_urllib(t) -> callable:
    """
    Create a hook to update the progress bar during urlretrieve download.

    :param t: tqdm progress bar instance
    :return: Inner function to update progress
    """

    def inner(blocks_transferred, block_size, total_size) -> None:
        if total_size > 0:
            t.total = total_size
            t.update(blocks_transferred * block_size - t.n)

    return inner


def download_model(model: DeepGlobalRegistrationModels, t) -> None:
    """
    Download a model from a given URL and save it to the specified path.

    :param model:
    :param t: tqdm progress bar instance
    """
    bucket_name: str = "benchmarks-ic"
    s3 = boto3.client('s3')

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
    for model in DeepGlobalRegistrationModels:
        if not os.path.exists(model.path):
            print(f"Model {model.name} not found locally. Starting download...")
            with tqdm(unit='B', unit_scale=True, desc=model.name) as t:
                download_model(model, t)
        else:
            print(f"Model {model.name} already exists.")
