import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import project_utils

if __name__ == '__main__':
    test: int = 1
    print('Teste com arquivos do diretório KITTI')

    if test == 1:
        print('#' * 50)
        print("Primeiro caso: ")
        target_ply_path: str = '../data/KITTI/00/000489.bin'
        source_ply_path: str = '../data/KITTI/00/003496.bin'
        ground_truth_path: str = '../data/KITTI/00.txt'

        with open(ground_truth_path, 'r') as f:
            lines = f.readlines()

        values_0: list[float] = project_utils.string_to_vector(lines[489])
        values_1: list[float] = project_utils.string_to_vector(lines[3496])
        T1 = project_utils.flattened_to_matrix(values_0)
        T2 = project_utils.flattened_to_matrix(values_1)
        # T_rel = T1 @ np.linalg.inv(T2)
        # T_rel = np.linalg.inv(T1) @ T2
        # T_rel = T2 @ np.linalg.inv(T1)
        # T_rel = np.linalg.inv(T2) @ T1


        # Linha 100
        # 0 489 0 3496
        # 0.999646 0.026629 0.000520 -9.792343
        # -0.026594 0.999018 -0.035453 -0.174136
        # -0.001464 0.035427 0.999371 -0.119800
        # 0.000000 0.000000 0.000000 1.000000
        _T = [[0.999646, 0.026629, 0.000520, -9.792343],
              [-0.026594, 0.999018, -0.035453, -0.174136],
              [-0.001464, 0.035427, 0.999371, -0.119800],
              [0, 0, 0, 1]]

        print("Matriz T1 (t=0):\n", T1)
        print("Matriz T2 (t=1):\n", T2)
        # print("Transformação relativa T_rel:\n", T_rel)

        t_gt = np.eye(4)

        print('Carregando nuvens de pontos.')
        source_cloud = project_utils.load_point_cloud(source_ply_path)
        # source_cloud.transform(_T)
        # source_cloud = source_cloud.transform(T_rel)
        # source_cloud.transform(np.linalg.inv(T1))
        target_cloud = project_utils.load_point_cloud(target_ply_path)
        target_cloud.transform(_T)
        # target_cloud = target_cloud.transform(T2)
        # target_cloud.transform(np.linalg.inv(T2))

        print('Nuvens de pontos carregadas.')
        print("Nuvens de ponto alinhadas: ")
        project_utils.draw_registration_result(target_cloud, source_cloud, t_gt, window_name='KITTI')
        # project_project_utils.draw_registration_result(source_cloud, target_cloud, t_gt, window_name='KITTI')
        print('#' * 50)
