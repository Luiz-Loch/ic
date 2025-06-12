import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import project_utils

if __name__ == '__main__':
    # Caminho do diretório
    data_dir: str = './data/ETH'
    VERBOSE: bool = False
    count: int = 0
    _count: int = 0

    # Teste da função get_datasets
    # for source_ply_path, target_ply_path, t_gt in project_utils.get_datasets(data_dir, VERBOSE):
        # print(f'{source_ply_path}\n{target_ply_path}\n{t_gt}')
        # print('#' * 50)
        # count += 1

    # print(f'{source_ply_path} - {target_ply_path}')

    for source_ply_path, target_ply_path, t_gt in project_utils.DataSetType._ALL.datasets:
        _count += 1

    print(f'{source_ply_path} - {target_ply_path}')

    print(f'{t_gt}')

    # print(f'Número de pares de nuvens de pontos 1: {count}')
    print(f'Número de pares de nuvens de pontos 2: {_count}')
