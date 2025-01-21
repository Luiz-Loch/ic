import utils


if __name__ == '__main__':
    # Caminho do diretório
    data_dir = '../data'
    VERBOSE = False
    count = 0

    # Teste da função get_datasets
    for source_ply_path, target_ply_path, t_gt in utils.get_datasets(data_dir, VERBOSE):
        print(f'{source_ply_path}\n{target_ply_path}\n{t_gt}')
        print('#' * 50)
        count += 1

    print(f'Número de pares de nuvens de pontos: {count}')