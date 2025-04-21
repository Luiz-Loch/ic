import open3d as o3d
import os
import sys
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
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
                                                                  feature_method=project_utils.FeatureMethod.FPFH,
                                                                  verbose=VERBOSE)
    source_down, target_down, source_features, target_features = results_preprocess

    if VERBOSE:
        print("Aplicando o alinhamento Point DSC ...")
    results_teaser, _ = project_utils.point_dsc(np.array(source_down.points),
                                                np.array(target_down.points),
                                                source_features,
                                                target_features,
                                                VOXEL_SIZE,
                                                verbose=VERBOSE,
                                                snapshot=project_utils.Snapshot.SNAPSHOT_KITTI)

    print(f"PointDSC: {results_teaser}")
    project_utils.draw_registration_result(source_cloud, target_cloud, np.eye(4))
    project_utils.draw_registration_result(source_cloud, target_cloud, results_teaser)