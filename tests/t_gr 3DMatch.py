import project_utils
import numpy as np

if __name__ == '__main__':
    test = 5
    print('Teste com arquivos do diretório 3DMatch')
    if test == 1:
        # Source + Target.transformation
        # `gt.log` traz source: 0, target: 3
        # Mas o alinhamento ocorre com source: 3, target: 0
        print('#' * 50)
        print("Primeiro caso, nuvem de pontos de `7-scenes-office`: ")
        source_ply_path = '../data/3DMatch/7-scenes-office/cloud_bin_0.ply'
        target_ply_path = '../data/3DMatch/7-scenes-office/cloud_bin_3.ply'
        t_gt = np.array([[0.981473397043, 0.13855507584, -0.132248257845, -0.0030175927441],
                         [-0.122808034028, 0.985063671726, 0.120610475207, -0.570569782637],
                         [0.146988582971, -0.102135042662, 0.983836308333, 1.0922412657],
                         [0.0, 0.0, 0.0, 1.0]])

        print('Carregando nuvens de pontos.')
        source_cloud = project_utils.load_point_cloud(source_ply_path)
        target_cloud = project_utils.load_point_cloud(target_ply_path)
        print('Nuvens de pontos carregadas.')
        print("Nuvens de ponto alinhadas: ")
        project_utils.draw_registration_result(source_cloud, target_cloud, t_gt)
        print('#' * 50)

    if test == 2:
        # Source + Target.transformation
        # `gt.log` traz source: 0, target: 37
        # Mas o alinhamento ocorre com source: 37, target: 0
        print('#' * 50)
        print("Segundo caso, nuvem de pontos de `bundlefusion-office0`:")
        source_ply_path = '../data/3DMatch/bundlefusion-office0/cloud_bin_0.ply'
        target_ply_path = '../data/3DMatch/bundlefusion-office0/cloud_bin_37.ply'
        t_gt = np.array([[0.975503, 0.118258, -0.185496, 0.423766],
                         [-0.0945428, 0.986746, 0.131884, 0.138398],
                         [0.198634, -0.111116, 0.973754, -0.100138],
                         [0.0, 0.0, 0.0, 1.0]])

        print('Carregando nuvens de pontos.')
        source_cloud = project_utils.load_point_cloud(source_ply_path)
        target_cloud = project_utils.load_point_cloud(target_ply_path)
        print('Nuvens de pontos carregadas.')
        print("Nuvens de ponto alinhadas: ")
        project_utils.draw_registration_result(source_cloud, target_cloud, t_gt)
        print('#' * 50)

    if test == 3:
        # Source + Target.transformation
        # `gt.log` traz source: 0, target: 2
        # Mas o alinhamento ocorre com source: 2, target: 0
        print('#' * 50)
        print("Terceiro caso, nuvem de pontos de `rgbd-scenes-v2-scene_10`: ")
        source_ply_path = '../data/3DMatch/rgbd-scenes-v2-scene_10/cloud_bin_0.ply'
        target_ply_path = '../data/3DMatch/rgbd-scenes-v2-scene_10/cloud_bin_2.ply'
        t_gt = np.array([[0.954459891, - 0.144202469, 0.261174203, - 0.311835],
                         [0.168832927, 0.982836917, - 0.0743440474, - 0.192537],
                         [- 0.245971054, 0.115053217, 0.962424542, 0.0211015],
                         [0.0, 0.0, 0.0, 1.0]])

        print('Carregando nuvens de pontos.')
        source_cloud = project_utils.load_point_cloud(source_ply_path)
        target_cloud = project_utils.load_point_cloud(target_ply_path)
        print('Nuvens de pontos carregadas.')
        print("Nuvens de ponto alinhadas: ")
        project_utils.draw_registration_result(source_cloud, target_cloud, t_gt)
        print('#' * 50)

    if test == 4:
        # Source + Target.transformation
        # `gt.log` traz source: 0, target: 2
        # Mas o alinhamento ocorre com source: 2, target: 0
        print('#' * 50)
        print("Quarto caso, nuvem de pontos de `sun3d-harvard_c6-hv_c6_1`: ")
        source_ply_path = '../data/3DMatch/sun3d-harvard_c6-hv_c6_1/cloud_bin_0.ply'
        target_ply_path = '../data/3DMatch/sun3d-harvard_c6-hv_c6_1/cloud_bin_2.ply'
        t_gt = np.array([[0.973223509896, 0.0216605509097, 0.228842355594, -0.734615266444],
                         [-0.0275504313362, 0.99936588607, 0.0225744277487, -0.0842539582894],
                         [-0.228208279858, -0.0282744284877, 0.973201581426, 0.638138990765],
                         [0.0, 0.0, 0.0, 1.0]])

        print('Carregando nuvens de pontos.')
        source_cloud = project_utils.load_point_cloud(source_ply_path)
        target_cloud = project_utils.load_point_cloud(target_ply_path)
        print('Nuvens de pontos carregadas.')
        print("Nuvens de ponto alinhadas: ")
        project_utils.draw_registration_result(source_cloud, target_cloud, t_gt)
        print('#' * 50)

    if test == 5:
        voxel_size = 0.05
        source_ply_path = '../data/3DMatch/7-scenes-office/cloud_bin_0.ply'
        target_ply_path = '../data/3DMatch/7-scenes-office/cloud_bin_3.ply'
        t_gt = np.array([[0.981473397043, 0.13855507584, -0.132248257845, -0.0030175927441],
                         [-0.122808034028, 0.985063671726, 0.120610475207, -0.570569782637],
                         [0.146988582971, -0.102135042662, 0.983836308333, 1.0922412657],
                         [0.0, 0.0, 0.0, 1.0]])

        source_cloud = project_utils.load_point_cloud(source_ply_path)
        target_cloud = project_utils.load_point_cloud(target_ply_path)

        source_cloud, target_cloud = target_cloud, source_cloud

        results_preprocess, _ = project_utils.preprocess_point_clouds(source_cloud, target_cloud,
                                                                voxel_size)
        source_down, target_down, source_features, target_features = results_preprocess

        # Aplica o alinhamento RANSAC:
        result_gr, _ = project_utils.global_registration(source_down, target_down, source_features,
                                                   target_features,
                                                   voxel_size)

        # project_project_utils.draw_registration_result(source_cloud, target_cloud, result_gr.transformation)

        print('Source, Target')
        print(f'RRE: {project_utils.rre(result_gr.transformation, t_gt)}')
        print(f'TRE: {project_utils.tre(result_gr.transformation, t_gt)}')
