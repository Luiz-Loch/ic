import open3d as o3d
from utils.decorators import measure_time


@measure_time
def fast_global_registration(source_cloud: o3d.geometry.PointCloud,
                             target_cloud: o3d.geometry.PointCloud,
                             source_features: o3d.pipelines.registration.Feature,
                             target_features: o3d.pipelines.registration.Feature,
                             voxel_size: float,
                             verbose: bool = False) -> o3d.pipelines.registration.RegistrationResult:
    """
     Recebe uma par de nuvem de pontos, bem como seus descritores e realiza *fast global registration*.
     Referência: https://www.open3d.org/docs/release/tutorial/pipelines/global_registration.html#id2
    """
    distance_threshold: float = voxel_size * 0.5

    if verbose:
        print("Realiza o *fast global registration*.")
        print(f"O raio de busca é {distance_threshold:0.03f}.")

    return o3d.pipelines.registration.registration_fgr_based_on_feature_matching(
        source_cloud,
        target_cloud,
        source_features,
        target_features,
        o3d.pipelines.registration.FastGlobalRegistrationOption(maximum_correspondence_distance=distance_threshold))
