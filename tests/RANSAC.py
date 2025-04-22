import open3d as o3d
import project_utils

if __name__ == '__main__':
    VERBOSE: bool = True
    VOXEL_SIZE: float = 0.05

    if VERBOSE:
        print("Carregando os dados...")
    point_clouds = o3d.data.DemoICPPointClouds("../demo")
    source_cloud = o3d.io.read_point_cloud(point_clouds.paths[0])
    target_cloud = o3d.io.read_point_cloud(point_clouds.paths[1])

    if VERBOSE:
        print("Aplicando o pre-processamento e descritor FPFH...")
    results_preprocess, _ = project_utils.preprocess_point_clouds(source_cloud,
                                                          target_cloud,
                                                          VOXEL_SIZE,
                                                          VERBOSE)
    source_down, target_down, source_features, target_features = results_preprocess

    if VERBOSE:
        print("Aplicando o alinhamento global robusto ...")
    results_ransac, _ = project_utils.robust_global_registration(source_down,
                                                         target_down,
                                                         source_features,
                                                         target_features,
                                                         VOXEL_SIZE,
                                                         VERBOSE)

    print(f"RANSAC: {results_ransac}")
    print(f"RANSAC:                         {results_ransac.fitness}")
    print(f"RANSAC:                         {results_ransac.inlier_rmse}")
