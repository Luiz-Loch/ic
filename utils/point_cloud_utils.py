from utils.decorators import measure_time
import copy
import numpy as np
import open3d as o3d


def load_point_cloud(file_path: str) -> o3d.geometry.PointCloud:
    """
    Loads a 3D point cloud file into a PointCloud object.

    Parameters:
    file_path (str): The path to the point cloud file.

    Returns:
    o3d.geometry.PointCloud: The loaded point cloud.
    """
    # Load point cloud from the specified file
    cloud: o3d.geometry.PointCloud = o3d.io.read_point_cloud(file_path)
    return cloud


@measure_time
def preprocess_point_clouds(source_cloud: o3d.geometry.PointCloud,
                            target_cloud: o3d.geometry.PointCloud,
                            voxel_size: float,
                            verbose: bool = False):
    """
    Preprocesses two point clouds by downsampling, estimating normals, and computing FPFH features.

    Parameters:
    source_cloud (o3d.geometry.PointCloud): The source point cloud.
    target_cloud (o3d.geometry.PointCloud): The target point cloud.
    voxel_size (float): The voxel size for downsampling.
    verbose (bool): If True, prints detailed processing information.

    Returns:
    tuple: A tuple containing the downsampled source cloud, downsampled target cloud, source features, and target features.
    """
    radius_normal: float = voxel_size * 2
    radius_feature: float = voxel_size * 5
    if verbose:
        print(f"Downsampling the point cloud to voxel size {voxel_size:0.03f}.")

    source_cloud_downsampled: o3d.geometry.PointCloud = source_cloud.voxel_down_sample(voxel_size)
    target_cloud_downsampled: o3d.geometry.PointCloud = target_cloud.voxel_down_sample(voxel_size)

    if verbose:
        print(f"Estimating normals with search radius {radius_normal:0.03f}.")

    source_cloud_downsampled.estimate_normals(
        o3d.geometry.KDTreeSearchParamHybrid(radius=radius_normal, max_nn=30)
    )

    target_cloud_downsampled.estimate_normals(
        o3d.geometry.KDTreeSearchParamHybrid(radius=radius_normal, max_nn=30)
    )

    source_feature = o3d.pipelines.registration.compute_fpfh_feature(
        source_cloud_downsampled,
        o3d.geometry.KDTreeSearchParamHybrid(radius=radius_feature, max_nn=100)
    )

    target_feature = o3d.pipelines.registration.compute_fpfh_feature(
        target_cloud_downsampled,
        o3d.geometry.KDTreeSearchParamHybrid(radius=radius_feature, max_nn=100)
    )

    return source_cloud_downsampled, target_cloud_downsampled, source_feature, target_feature


def draw_registration_result(source: o3d.geometry.PointCloud,
                             target: o3d.geometry.PointCloud,
                             transformation: np.ndarray,
                             window_name: str = "Open3D") -> None:
    """
    Draws the aligned point clouds.

    Parameters:
    source (o3d.geometry.PointCloud): The source point cloud.
    target (o3d.geometry.PointCloud): The target point cloud.
    transformation (np.ndarray): The transformation matrix to align the source to the target.
    window_name (str): The window name for visualization.
    """
    voxel_size: float = 0.10
    radius_normal: float = voxel_size * 2

    source_temp: o3d.geometry.PointCloud = copy.deepcopy(source)
    target_temp: o3d.geometry.PointCloud = copy.deepcopy(target)

    source_temp.voxel_down_sample(voxel_size)
    target_temp.voxel_down_sample(voxel_size)

    source_temp.paint_uniform_color([0.96, 0.76, 0.26])  # Yellow
    target_temp.paint_uniform_color([0.40, 0.74, 0.85])  # Blue

    source_temp.estimate_normals(o3d.geometry.KDTreeSearchParamHybrid(radius=radius_normal, max_nn=30))
    target_temp.estimate_normals(o3d.geometry.KDTreeSearchParamHybrid(radius=radius_normal, max_nn=30))

    source_temp.transform(transformation)
    o3d.visualization.draw_geometries([source_temp, target_temp], window_name=window_name)
