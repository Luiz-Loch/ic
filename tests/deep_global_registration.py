import open3d as o3d
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import project_utils

if __name__ == '__main__':
    VERBOSE: bool = True
    VOXEL_SIZE: float = 0.05
    project_utils.download_models()

    if VERBOSE:
        print("Carregando os dados...")
    point_clouds = o3d.data.DemoICPPointClouds("../demo")
    source_cloud = o3d.io.read_point_cloud(point_clouds.paths[0])
    target_cloud = o3d.io.read_point_cloud(point_clouds.paths[1])

    if VERBOSE:
        print("Aplicando o alinhamento Deep Global registration ...")

    # results_dgr, time = project_project_utils.deep_global_registration(source_cloud,
    #                                                    target_cloud,
    #                                                    VOXEL_SIZE,
    #                                                    VERBOSE,
    #                                                    project_project_utils.DeepGlobalRegistrationModels.DGR_3DMATCH)
    #
    # print(f"Tempo de processamento: {time}")
    # print(f"DGR: {results_dgr}")
    #
    # project_project_utils.draw_registration_result(source_cloud, target_cloud, results_dgr)
