import open3d as o3d
import os
import sys
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
import project_utils

if __name__ == '__main__':
    VERBOSE: bool = True
    VOXEL_SIZE: float = 0.10

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
                                                                  feature_method=project_utils.FeatureMethod.FPFH,
                                                                  verbose=VERBOSE)
    source_down, target_down, source_features, target_features = results_preprocess

    if VERBOSE:
        print("Aplicando o alinhamento Point Maximal Cliques ...")
    results_mac, _ = project_utils.maximal_cliques(source_down,
                                                   target_down,
                                                   source_features,
                                                   target_features,
                                                   VOXEL_SIZE,
                                                   feature_method=project_utils.FeatureMethod.FPFH,
                                                   verbose=VERBOSE)

    print("Maximal Cliques:")
    print(f"{results_mac}")
    project_utils.draw_registration_result(source_cloud, target_cloud, np.eye(4))
    project_utils.draw_registration_result(source_cloud, target_cloud, results_mac)


# voxel_size = 0.10:
# Graph construction: 30.66ms
# Search maximal cliques: 57.20ms
# Total: 16765
# After filtered: 941

# voxel_size = 0.08:
# Graph construction: 73.14ms
# Search maximal cliques: 270.85ms
# Total: 141 442
# After filtered: 1 746

# voxel_size = 0.07:
# Graph construction: 129.89ms
# Search maximal cliques: 751.11ms
# Total: 434 005
# After filtered: 2 183

# voxel_size = 0.06:
# Graph construction: 265.84ms
# Search maximal cliques: 1733.25ms
# Total: 893 966
# After filtered: 2 936