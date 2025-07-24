import argparse
from datetime import datetime

from project_utils import (DataSetType, DGRModels, FCGFModels, FeatureMethod,
                           RegistrationMethod, Snapshot)

CURRENT_DATE: str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')


def str2bool(v) -> bool:
    return v.lower() in ('true', '1', 'yes')


def str2dataset_type(v) -> DataSetType:
    try:
        return DataSetType[v.upper()]
    except KeyError:
        raise argparse.ArgumentTypeError(f"Invalid dataset type: {v}. Must be one of {list(DataSetType)}.")


def str2feature_method(v) -> FeatureMethod:
    try:
        return FeatureMethod[v.upper()]
    except KeyError:
        raise argparse.ArgumentTypeError(f"Invalid feature method: {v}. Must be one of {list(FeatureMethod)}.")


def str2fcgf_model(v) -> FCGFModels:
    try:
        return FCGFModels[v.upper()]
    except KeyError:
        raise argparse.ArgumentTypeError(f"Invalid FCGF model: {v}. Must be one of {list(FCGFModels)}.")


def str2registration_method(v) -> RegistrationMethod:
    try:
        return RegistrationMethod[v.upper()]
    except KeyError:
        raise argparse.ArgumentTypeError(
            f"Invalid registration method: {v}. Must be one of {list(RegistrationMethod)}.")


def str2dgr_model(v) -> DGRModels:
    try:
        return DGRModels[v.upper()]
    except KeyError:
        raise argparse.ArgumentTypeError(f"Invalid DGR model: {v}. Must be one of {list(DGRModels)}.")

def str2snapshot(v) -> Snapshot:
    try:
        return Snapshot[v.upper()]
    except KeyError:
        raise argparse.ArgumentTypeError(f"Invalid snapshot: {v}. Must be one of {list(Snapshot)}.")


def print_config_summary(config: argparse.Namespace) -> None:
    print("📋 Execution started with the following configuration:\n")
    print(f"  🔁 Number of executions per pair: {config.num_of_exec}")
    print(f"  📏 Voxel sizes: {', '.join(str(v) for v in config.voxel_sizes)}")
    print(f"  📚 Dataset: {config.dataset.name}")
    print(f"  🧩 Feature method: {config.feature_method.name}" +
          f" ({config.feature_method.model(config.fcgf_model)})")
          # "")
    print(f"  🧭 Registration method: {config.registration_method.name}" +
          f" ({config.registration_method.model(config.dgr_model, config.point_dsc_snapshot)})")
          # "")
    print(f"  🛠️ ICP enabled: {'Yes' if config.do_icp else 'No'}")
    print(f"  💾 Output file: {config.results_file}")
    print("")  # Blank line


def get_config() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark CLI")

    parser.add_argument('--verbose', type=str2bool, default=False)
    parser.add_argument('--num_of_exec', type=int, default=3)
    parser.add_argument('--voxel_sizes', type=float, nargs='+', default=[0.05])
    parser.add_argument('--dataset', type=str2dataset_type, default=DataSetType.ALL)
    parser.add_argument('--feature_method', type=str2feature_method, default=FeatureMethod.FPFH)
    parser.add_argument('--fcgf_model', type=str2fcgf_model, default=FCGFModels.FCGF_3DMATCH)
    parser.add_argument('--registration_method', type=str2registration_method, default=RegistrationMethod.RANSAC)
    parser.add_argument('--dgr_model', type=str2dgr_model, default=DGRModels.DGR_3DMATCH)
    parser.add_argument('--point_dsc_snapshot', type=str2snapshot, default=Snapshot.SNAPSHOT_3DMATCH)
    parser.add_argument('--do_icp', type=str2bool, default=True)

    args: argparse.Namespace = parser.parse_args()

    args.results_file = f"./outputs/{CURRENT_DATE}-{args.dataset.name}-{args.feature_method.name}-{args.registration_method.name}.csv"

    print_config_summary(args)

    return args
