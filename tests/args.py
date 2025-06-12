import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from project_config import get_config
import project_utils

if __name__ == '__main__':
    config = get_config()

    verbose: bool = config.verbose
    num_of_exec: int = config.num_of_exec
    voxel_sizes: list[float] = config.voxel_sizes
    dataset: project_utils.DataSetType = config.dataset
    feature_method: project_utils.FeatureMethod = config.feature_method
    registration_method:project_utils.RegistrationMethod = config.registration_method
    do_icp: bool = config.do_icp
    results_file: str = config.results_file

    print(f"{verbose=}")
    print(f"{num_of_exec=}")
    print(f"{voxel_sizes=}")
    print(f"{dataset=}")
    print(f"{feature_method=}")
    print(f"{registration_method=}")
    print(f"{do_icp=}")
    print(f"{results_file=}")
