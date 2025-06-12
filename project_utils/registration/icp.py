import open3d as o3d
import numpy as np
from project_utils.decorators import measure_time


def fine_alignment(source_cloud: o3d.geometry.PointCloud,
                   target_cloud: o3d.geometry.PointCloud,
                   initial_transform: np.ndarray,
                   voxel_size: float,
                   icp_method,
                   verbose: bool = False) -> np.ndarray:
    """
    Recebe um par de nuvem de pontos, bem como uma transformação inicial para realizar um alinhamento.
    O tipo de alinhamento deve ser informado em `icp_method`.
    Utiliza o método Point to Point da biblioteca Open3D.
    Referência: https://www.open3d.org/docs/release/tutorial/pipelines/global_registration.html#Local-refinement
    """

    distance_threshold: float = voxel_size * 0.4
    if verbose:
        print(f"Realizando o alinhamento com ICP - {icp_method}.")
    result = o3d.pipelines.registration.registration_icp(source_cloud,
                                                         target_cloud,
                                                         distance_threshold,
                                                         initial_transform,
                                                         icp_method)
    return np.asarray(result.transformation)


@measure_time
def fine_alignment_point_to_point(source_cloud: o3d.geometry.PointCloud,
                                  target_cloud: o3d.geometry.PointCloud,
                                  initial_transform: np.ndarray,
                                  voxel_size: float,
                                  verbose: bool = False) -> np.ndarray:
    """
    Recebe um par de nuvem de pontos, bem como uma transformação inicial para realizar um alinhamento fino.
    Utiliza o método Point to Point da biblioteca Open3D.
    Referência: https://www.open3d.org/docs/release/tutorial/pipelines/global_registration.html#Local-refinement
    """
    icp_method = o3d.pipelines.registration.TransformationEstimationPointToPoint()

    return fine_alignment(source_cloud,
                          target_cloud,
                          initial_transform,
                          voxel_size,
                          icp_method,
                          verbose=verbose)


@measure_time
def fine_alignment_point_to_plane(source_cloud: o3d.geometry.PointCloud,
                                  target_cloud: o3d.geometry.PointCloud,
                                  initial_transform: np.ndarray,
                                  voxel_size: float,
                                  verbose: bool = False) -> np.ndarray:
    """
    Recebe um par de nuvem de pontos, bem como uma transformação inicial para realizar um alinhamento fino.
    Utiliza o método Point to Plane da biblioteca Open3D.
    Referência: https://www.open3d.org/docs/release/tutorial/pipelines/global_registration.html#Local-refinement
    """
    icp_method = o3d.pipelines.registration.TransformationEstimationPointToPlane()

    return fine_alignment(source_cloud,
                          target_cloud,
                          initial_transform,
                          voxel_size,
                          icp_method,
                          verbose=verbose)
