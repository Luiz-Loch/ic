import modulos


if __name__ == '__main__':
    # Caminho do diretório
    data_dir = '../data/3DMatch/rgbd-scenes-v2-scene_10'
    VERBOSE = True

    # Teste da função get_datasets
    for source_ply_path, target_ply_path, t_gt in modulos.get_datasets(data_dir, VERBOSE):
        print(f'{source_ply_path}\n{target_ply_path}\n{t_gt}')
        print('#' * 50)
