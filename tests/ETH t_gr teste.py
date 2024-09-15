import modulos
import numpy as np

if __name__ == '__main__':
    test = 4
    print('Teste com arquivos do diretório ETH')
    if test == 1:
        # Source + Target.transformation
        # `gt.log` traz source: 0, target: 1
        # Mas o alinhamento ocorre com source: 1, target: 0
        print('#' * 50)
        print("Primeiro caso, nuvem de pontos de `gazebo_summer`: ")
        source_ply_path = '../data/ETH/gazebo_summer/Hokuyo_0.ply'
        target_ply_path = '../data/ETH/gazebo_summer/Hokuyo_1.ply'
        t_gt = np.array([[0.9994700000, -0.0317550000, -0.0072210000, 0.7565390000],
                         [0.0317680000, 0.9994940000, 0.0016100000, 0.0817570000],
                         [0.0071660000, -0.0018380000, 0.9999720000, 0.0141140000],
                         [0.0000000000, 0.0000000000, 0.0000000000, 1.0000000000]])

        print('Carregando nuvens de pontos.')
        source_cloud = modulos.load_point_cloud(source_ply_path)
        target_cloud = modulos.load_point_cloud(target_ply_path)
        print('Nuvens de pontos carregadas.')
        print("Nuvens de ponto alinhadas: ")
        modulos.draw_registration_result(target_cloud, source_cloud, t_gt, nome='ETH')
        print('#' * 50)

    if test == 2:
        # Source + Target.transformation
        # `gt.log` traz source: 0, target: 1
        # Mas o alinhamento ocorre com source: 1, target: 0
        print('#' * 50)
        print("Segundo caso, nuvem de pontos de `gazebo_winter`:")
        source_ply_path = '../data/ETH/gazebo_winter/Hokuyo_0.ply'
        target_ply_path = '../data/ETH/gazebo_winter/Hokuyo_1.ply'
        t_gt = np.array([[0.9988430000, -0.0480960000, -0.0010840000, 0.6192810000],
                         [0.0480970000, 0.9988420000, 0.0010300000, 0.0138970000],
                         [0.0010340000, -0.0010800000, 0.9999990000, 0.0055930000],
                         [0.0000000000, 0.0000000000, 0.0000000000, 1.0000000000]])

        print('Carregando nuvens de pontos.')
        source_cloud = modulos.load_point_cloud(source_ply_path)
        target_cloud = modulos.load_point_cloud(target_ply_path)
        print('Nuvens de pontos carregadas.')
        print("Nuvens de ponto alinhadas: ")
        modulos.draw_registration_result(target_cloud, source_cloud, t_gt, nome='ETH')
        print('#' * 50)

    if test == 3:
        # Source + Target.transformation
        # `gt.log` traz source: 0, target: 2
        # Mas o alinhamento ocorre com source: 2, target: 0
        print('#' * 50)
        print("Terceiro caso, nuvem de pontos de `wood_autmn`: ")
        source_ply_path = '../data/ETH/wood_autmn/Hokuyo_0.ply'
        target_ply_path = '../data/ETH/wood_autmn/Hokuyo_1.ply'
        t_gt = np.array([[0.9895540000, -0.1438740000, 0.0091230000, 0.4946280000],
                         [0.1440770000, 0.9891690000, -0.0280470000, 0.0496910000],
                         [-0.0049890000, 0.0290690000, 0.9995650000, 0.0150680000],
                         [0.0000000000, 0.0000000000, 0.0000000000, 1.0000000000]])

        print('Carregando nuvens de pontos.')
        source_cloud = modulos.load_point_cloud(source_ply_path)
        target_cloud = modulos.load_point_cloud(target_ply_path)
        print('Nuvens de pontos carregadas.')
        print("Nuvens de ponto alinhadas: ")
        modulos.draw_registration_result(target_cloud, source_cloud, t_gt, nome='ETH')
        print('#' * 50)

    if test == 4:
        # Source + Target.transformation
        # `gt.log` traz source: 0, target: 1
        # Mas o alinhamento ocorre com source: 1, target: 0
        print('#' * 50)
        print("Quarto caso, nuvem de pontos de `wood_summer`: ")
        source_ply_path = '../data/ETH/wood_summer/Hokuyo_0.ply'
        target_ply_path = '../data/ETH/wood_summer/Hokuyo_1.ply'
        t_gt = np.array([[0.9843110000, -0.1727000000, -0.0361340000, 0.6057420000],
                         [0.1726860000, 0.9849700000, -0.0035320000, 0.0407490000],
                         [0.0362000000, -0.0027620000, 0.9993410000, 0.0269290000],
                         [0.0000000000, 0.0000000000, 0.0000000000, 1.0000000000]])

        print('Carregando nuvens de pontos.')
        source_cloud = modulos.load_point_cloud(source_ply_path)
        target_cloud = modulos.load_point_cloud(target_ply_path)
        print('Nuvens de pontos carregadas.')
        print("Nuvens de ponto alinhadas: ")
        modulos.draw_registration_result(target_cloud, source_cloud, t_gt, nome='ETH')
        print('#' * 50)

    if test == 5:
        voxel_size = 0.05
        source_ply_path = '../data/ETH/gazebo_summer/Hokuyo_0.ply'
        target_ply_path = '../data/ETH/gazebo_summer/Hokuyo_1.ply'
        t_gt = np.array([[0.9994700000, -0.0317550000, -0.0072210000, 0.7565390000],
                         [0.0317680000, 0.9994940000, 0.0016100000, 0.0817570000],
                         [0.0071660000, -0.0018380000, 0.9999720000, 0.0141140000],
                         [0.0000000000, 0.0000000000, 0.0000000000, 1.0000000000]])

        source_cloud = modulos.load_point_cloud(source_ply_path)
        target_cloud = modulos.load_point_cloud(target_ply_path)

        source_cloud, target_cloud = target_cloud, source_cloud

        results_preprocess, _ = modulos.preprocess_point_clouds(source_cloud, target_cloud,
                                                                voxel_size)
        source_down, target_down, source_features, target_features = results_preprocess

        # Aplica o alinhamento RANSAC:
        result_gr, _ = modulos.global_registration(source_down, target_down, source_features,
                                                   target_features,
                                                   voxel_size)

        modulos.draw_registration_result(source_cloud, target_cloud, result_gr.transformation, nome='ETH')

        print('Source, Target')
        print(f'RRE: {modulos.rre(result_gr.transformation, t_gt)}')
        print(f'TRE: {modulos.tre(result_gr.transformation, t_gt)}')
