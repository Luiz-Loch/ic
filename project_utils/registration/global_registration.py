import open3d as o3d
import numpy as np


def global_registration(source_cloud: o3d.geometry.PointCloud,
                        target_cloud: o3d.geometry.PointCloud,
                        source_features: o3d.pipelines.registration.Feature,
                        target_features: o3d.pipelines.registration.Feature,
                        voxel_size: int | float,
                        verbose: bool = False,
                        **kwargs) -> np.ndarray:
    """
        Recebe uma par de nuvem de pontos, bem como seus descritores e realiza *global registration*.
        Utiliza o método RANSAC da biblioteca Open3D.
        Referência: https://www.open3d.org/docs/release/tutorial/pipelines/global_registration.html#RANSAC
    """
    distance_threshold: float = voxel_size * 1.5
    max_iteration: int = 100_000
    confidence: float = 0.999

    if verbose:
        print("Realiza o alinhamento grosseiro usando o método RANSAC.")
        print(f"O raio de busca é {distance_threshold:0.03f}.")

    # Executa até atingir `max_iteration` ou `confidence`.
    result = o3d.pipelines.registration.registration_ransac_based_on_feature_matching(
        source_cloud, target_cloud, source_features, target_features, True,
        distance_threshold,
        o3d.pipelines.registration.TransformationEstimationPointToPoint(False),
        3, [
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnEdgeLength(
                0.9),
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnDistance(
                distance_threshold)
        ],
        o3d.pipelines.registration.RANSACConvergenceCriteria(
            max_iteration, confidence))

    return np.asarray(result.transformation)