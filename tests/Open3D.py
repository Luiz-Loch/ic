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
        print("Aplicando o alinhamento RANSAC e FGR...")
    result_gr, _ = project_utils.global_registration(source_down,
                                             target_down,
                                             source_features,
                                             target_features,
                                             VOXEL_SIZE,
                                             VERBOSE)
    result_fgr, _ = project_utils.fast_global_registration(source_down,
                                                   target_down,
                                                   source_features,
                                                   target_features,
                                                   VOXEL_SIZE,
                                                   VERBOSE)

    print(f"RANSAC: {result_gr}")
    print(f"RANSAC:                         {result_gr.fitness}")
    print(f"RANSAC:                         {result_gr.inlier_rmse}")
    print(f"FGR: {result_fgr}")
    print(f"FGR:                            {result_fgr.fitness}")
    print(f"FGR:                            {result_fgr.inlier_rmse}")

    if VERBOSE:
        print("Refinando o alinhamento com ICP Point-to-Point e ICP Point-to-Plane...")
    result_gr_icp_point, _ = project_utils.fine_alignment_point_to_point(source_down, target_down, result_gr.transformation,
                                                                 VOXEL_SIZE, VERBOSE)
    result_gr_icp_plane, _ = project_utils.fine_alignment_point_to_plane(source_down, target_down, result_gr.transformation,
                                                                 VOXEL_SIZE, VERBOSE)

    print(f"RANSAC + ICP Point-to-Point: {result_gr_icp_point}")
    print(f"RANSAC + ICP Point-to-Point:    {result_gr_icp_point.fitness}")
    print(f"RANSAC + ICP Point-to-Point:    {result_gr_icp_point.inlier_rmse}")
    print("################")
    print(f"RANSAC + ICP Point-to-Plane: {result_gr_icp_plane}")
    print(f"RANSAC + ICP Point-to-Plane:    {result_gr_icp_plane.fitness}")
    print(f"RANSAC + ICP Point-to-Plane:    {result_gr_icp_plane.inlier_rmse}")
