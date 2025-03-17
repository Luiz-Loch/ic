import numpy as np
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import utils

if __name__ == '__main__':
    test: int = 1
    print('Teste com arquivos do diretório KITTI')

    if test == 1:
        print('#' * 50)
        print("Primeiro caso: ")
        target_ply_path: str = '../data/KITTI/00/000000.bin'
        source_ply_path: str = '../data/KITTI/00/000001.bin'
        ground_truth_path: str = '../data/KITTI/00.txt'

        with open(ground_truth_path, 'r') as f:
            lines = f.readlines()

        values_0: list[float] = utils.string_to_vector(lines[0])
        values_1: list[float] = utils.string_to_vector(lines[1])
        T1 = utils.flattened_to_matrix(values_0)
        T2 = utils.flattened_to_matrix(values_1)

        T_relative = np.linalg.inv(T1) @ T2

        print(T_relative)
        t_gt = np.eye(4)

        print('Carregando nuvens de pontos.')
        source_cloud = utils.load_point_cloud(source_ply_path)
        target_cloud = utils.load_point_cloud(target_ply_path)

        print('Nuvens de pontos carregadas.')
        print("Nuvens de ponto alinhadas: ")
        utils.draw_registration_result(target_cloud, source_cloud, T_relative, window_name='KITTI')
        print('#' * 50)
