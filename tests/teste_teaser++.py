import open3d as o3d
import utils

if __name__ == '__main__':
    VERBOSE = True
    VOXEL_SIZE = 0.05
    if VERBOSE:
        print("Carregando os dados...")
    point_clouds = o3d.data.DemoICPPointClouds("../demo")
    source_cloud = o3d.io.read_point_cloud(point_clouds.paths[0])
    target_cloud = o3d.io.read_point_cloud(point_clouds.paths[1])

    if VERBOSE:
        print("Aplicando o pre-processamento e descritor FPFH...")
    results_preprocess, _ = utils.preprocess_point_clouds(source_cloud, target_cloud, VOXEL_SIZE, VERBOSE)
    source_down, target_down, source_features, target_features = results_preprocess

    if VERBOSE:
        print("Aplicando o alinhamento global robusto ...")
    results_teaser, _ = utils.robust_global_registration(source_down, target_down, source_features, target_features,
                                                           VOXEL_SIZE, VERBOSE)

    print(f"RGR: {results_teaser}")
    print(f"RGR:                         {results_teaser.fitness}")
    print(f"RGR:                         {results_teaser.inlier_rmse}")
