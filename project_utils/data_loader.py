import os

import numpy as np


def read_gt_log(file_path: str, verbose: bool = False) -> tuple[int, int, np.ndarray]:
    """
    Reads a `gt.log` transformation file and returns a generator of tuples.

    Args:
        file_path (str): The path to the `gt.log` file.
        verbose (bool): If True, prints detailed information during execution.

    Yields:
        tuple[int, int, np.ndarray]: A tuple containing the source ID, target ID, and the transformation matrix.
    """
    if verbose:
        print("#" * 50)
        print(f"Dentro da função `{read_gt_log.__name__}`.")
        print(f"Lendo o arquivo `{file_path}`.")

    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"File not found: `{file_path}`.")
        return

    if verbose:
        print(f"O arquivo `{file_path}` possui {len(lines)} linhas.")
    for i in range(0, len(lines), 5):
        if verbose:
            print(f"Linhas {i} a {i + 4}:")
            print(lines[i:i + 5])

        source, target, _ = lines[i].split()
        t_gt = np.array([float(x) for line in lines[i + 1:i + 5] for x in line.split()]).reshape(4, 4)

        if verbose:
            print(f"source: {source}; target: {target}")
            print(f"t_gt:\n{t_gt}")
            print("Fim da função.")
            print("#" * 50)
        yield source, target, t_gt


def get_datasets(data_dir: str, verbose: bool = False) -> tuple[str, str, np.ndarray]:
    """
    Returns a generator of tuples containing the paths to `gt.log`, `source.ply`, and `target.ply` files.

    Args:
        data_dir (str): The directory to search for `gt.log` files.
        verbose (bool): If True, prints detailed information during execution.

    Yields:
        tuple[str, str, np.ndarray]: A tuple containing the paths to the `source.ply` file, `target.ply` file, and the transformation matrix.
    """
    if verbose:
        print("#" * 50)
        print(f"Dentro da função {get_datasets.__name__}.")
        print(f"Procurando arquivos `gt.log` dentro do diretório {data_dir}.")
    for root, _, files in os.walk(data_dir):
        if verbose:
            print(f"Procurando arquivos dentro do diretório {root}.")
        for file in files:
            if verbose:
                print(f"Checando o arquivo {file}.")
            if file == 'gt.log':
                if verbose:
                    print(f"Arquivo {file} encontrado.")
                for source, target, t_gt in read_gt_log(os.path.join(root, file), verbose=verbose):
                    source_ply = f'_{source}.ply'
                    target_ply = f'_{target}.ply'

                    if verbose:
                        print(f"source: {source}; target: {target}")
                        print(f"t_gt:\n{t_gt}")
                        print(f"source_ply: {source_ply}; target_ply: {target_ply}")

                    source_ply_path = None
                    target_ply_path = None

                    if verbose:
                        print(f"Procurando arquivos que terminem com `{source_ply}` e `{target_ply}`.")

                    for ply_file in files:
                        if verbose:
                            print(f"Checando o arquivo {ply_file}.")
                        if ply_file.endswith(source_ply):
                            source_ply_path = os.path.join(root, ply_file)
                            if verbose:
                                print(f"Um arquivo que termina com `{source_ply}` foi encontrado.")
                                print(f"source_ply_path: {source_ply_path}")
                        if ply_file.endswith(target_ply):
                            target_ply_path = os.path.join(root, ply_file)
                            if verbose:
                                print(f"Um arquivo que termina com `{target_ply}` foi encontrado.")
                                print(f"target_ply_path: {target_ply_path}")

                        if source_ply_path and target_ply_path:
                            # Se ambos os arquivos foram encontrados, sai do loop
                            if verbose:
                                print(f"Ambos os arquivos foram encontrados.")
                            break
                    if verbose:
                        print(f'Retornando os valores: {source_ply_path}, {target_ply_path}, {t_gt}')
                    yield source_ply_path, target_ply_path, t_gt


def flattened_to_matrix(flattened):
    """
    Converts a flattened matrix (12 values) into a 4x4 matrix.

    Parameters:
        flattened (list or np.ndarray): List or array with 12 matrix values.

    Returns:
        np.ndarray: Corresponding 4x4 matrix.
    """
    assert len(flattened) == 12, "The list must contain exactly 12 elements."

    matrix = np.array(flattened, dtype=np.float64).reshape(3, 4)  # Shape (3, 4)
    matrix = np.vstack([matrix, [0, 0, 0, 1]])  # Add the last row [0, 0, 0, 1]

    return matrix


def string_to_vector(matrix_string: str) -> list[float]:
    """
    Converts a space-separated string of 12 values into a list of floats.

    Parameters:
        matrix_string (str): A string containing 12 space-separated numbers.

    Returns:
        list: A list of 12 floating-point numbers.
    """
    return [float(value) for value in matrix_string.split()]

def kitti_read_gt_log(data_dir: str, verbose: bool = False) -> tuple[str, str, np.ndarray]:
    """
    """
    base_path_name: str = "../data/KITTI/{:02d}/velodyne/{:06d}.bin"
    try:
        gt_log_file_path: str = os.path.join(data_dir, 'ground_truth.txt')
    except FileNotFoundError:
        raise Exception(f"File not found: `.../KITTI/ground_truth.txt`.")

    if verbose:
        print(f"Reading {gt_log_file_path}.")

    with (open(gt_log_file_path, "r") as file):
        next(file)  # Skip the first line (header)
        for line in file:
            parts = line.split()
            source_ply_path: str = base_path_name.format(int(parts[0]), int(parts[1]))
            target_ply_path: str = base_path_name.format(int(parts[2]), int(parts[3]))
            t_gt: np.ndarray = np.array([float(x) for x in parts[4:]]).reshape(4, 4)

            if verbose:
                print(f"source: {source_ply_path}; target: {target_ply_path}")
                print(f"t_gt:\n{t_gt}")
                print("Fim da função.")
                print("#" * 50)

            yield source_ply_path, target_ply_path, t_gt