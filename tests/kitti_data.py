import os

# Caminho do arquivo que contém os dados
arquivo_dados: str = "../data/KITTI/ground_truth.txt"

# Ler o arquivo e extrair os caminhos válidos
valid_paths: set = set()

with open(arquivo_dados, "r") as file:
    next(file)  # Pular a primeira linha (cabeçalho)
    for line in file:
        parts = line.split()
        if len(parts) >= 4:
            pasta1, arquivo1, pasta2, arquivo2 = parts[:4]
            valid_paths.add((int(pasta1), int(arquivo1)))
            valid_paths.add((int(pasta2), int(arquivo2)))

print(len(valid_paths))

# Diretório base onde os arquivos estão localizados
base_directory: str = "../data/KITTI/{:02d}/velodyne/{:06d}.bin"
# Diretório onde os arquivos serão movidos
target_directory: str = "../data/KITTI/necessarios/{:02d}/velodyne/{:06d}.bin"

# Mover os arquivos para o diretório de destino
for pasta, arquivo in valid_paths:
    origem = base_directory.format(pasta, arquivo)
    destino = target_directory.format(pasta, arquivo)
    print(origem)
    print(destino)
    # os.makedirs(os.path.dirname(destino), exist_ok=True)
    # os.rename(origem, destino)
