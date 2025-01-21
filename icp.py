from tqdm import tqdm, trange
import numpy as np
from datetime import datetime
import json
import utils

if __name__ == '__main__':
    VERBOSE: bool = False
    NUM_OF_EXEC: int = 4
    voxel_sizes: tuple[float] = (0.05,)
    DATASETS = utils.get_datasets('./data/3DMatch/rgbd-scenes-v2-scene_10')
    CURRENT_DATE: str = datetime.now().strftime('%Y-%m-%d')
    # Registra o momento de início
    start_time = datetime.now()
    DO_ICP: bool = True

    ON_AWS: bool = False
    BUCKET: str = 'benchmarks-ic'
    region_name: str = 'us-east-1'

    execution_times = {}
    EXECUTION_FILE: str = 'output/execution_times.json'
    results = {}
    RESULTS_FILE: str = 'output/results.json'

    # Obter ID e nome da instância
    if ON_AWS:
        instance_id: str | None = utils.get_instance_id()
        instance_name: str | None = utils.get_instance_name(instance_id)
        print(f'ID da Instância: {instance_id}')
        if instance_name:
            print(f'Nome da Instância: {instance_name}')
        else:
            print('Nome da Instância não encontrado')

    for target_ply_path, source_ply_path, t_gt in tqdm(DATASETS):
        # As matrizes `t_gt` foram calculadas a partir da target -> source
        # Então, para manter o padrão e não precisar calcular a inversa de `t_gt`
        # A ordem das nuvens foi invertida

        # Cria as chaves para os dicionários:
        key_img: str = f'Source: {source_ply_path}; Target: {target_ply_path}'
        execution_times[key_img] = {}
        results[key_img] = {}

        # Carrega os dados:
        source_cloud = utils.load_point_cloud(source_ply_path)
        target_cloud = utils.load_point_cloud(target_ply_path)

        results[key_img]['length of source'] = len(source_cloud.points)
        results[key_img]['length of target'] = len(target_cloud.points)

        for voxel_size in tqdm(voxel_sizes):
            key_voxel: str = f'voxel: {voxel_size}'
            execution_times[key_img][key_voxel] = {}
            results[key_img][key_voxel] = {}

            for run in trange(NUM_OF_EXEC):
                run_key: str = f'run: {run}'
                execution_times[key_img][key_voxel][run_key] = {}
                results[key_img][key_voxel][run_key] = {}

                # Aplica o pre-processamento:
                # Devido ao decorator, a função `preprocess_point_clouds` retorna uma tupla com os resultados e o tempo de execução
                results_preprocess, execution_time = utils.preprocess_point_clouds(source_cloud, target_cloud,
                                                                                     voxel_size)
                source_down, target_down, source_features, target_features = results_preprocess
                execution_times[key_img][key_voxel][run_key]['preprocess'] = execution_time

                if DO_ICP:
                    # ICP Point-to-Point:
                    result_icp_point, execution_time = utils.fine_alignment_point_to_point(source_down,
                                                                                             target_down,
                                                                                             np.eye(4),
                                                                                             voxel_size)
                    execution_times[key_img][key_voxel][run_key]['ICP Point'] = execution_time
                    results[key_img][key_voxel][run_key]['ICP Point'] = {}
                    results[key_img][key_voxel][run_key]['ICP Point'][
                        'transformation'] = result_icp_point.transformation.tolist()
                    results[key_img][key_voxel][run_key]['ICP Point']['tre'] = utils.tre(
                        result_icp_point.transformation, t_gt)
                    results[key_img][key_voxel][run_key]['ICP Point']['rre'] = utils.rre(
                        result_icp_point.transformation, t_gt)

                    # ICP Point-to-Plane:
                    result_icp_plane, execution_time = utils.fine_alignment_point_to_plane(source_down,
                                                                                             target_down,
                                                                                             np.eye(4),
                                                                                             voxel_size)
                    execution_times[key_img][key_voxel][run_key]['ICP Plane'] = execution_time
                    results[key_img][key_voxel][run_key]['ICP Plane'] = {}
                    results[key_img][key_voxel][run_key]['ICP Plane'][
                        'transformation'] = result_icp_plane.transformation.tolist()
                    results[key_img][key_voxel][run_key]['ICP Plane']['tre'] = utils.tre(
                        result_icp_plane.transformation, t_gt)
                    results[key_img][key_voxel][run_key]['ICP Plane']['rre'] = utils.rre(
                        result_icp_plane.transformation, t_gt)

    # ########################### ####### ###########################

    with open(EXECUTION_FILE, 'w') as f:
        json.dump(execution_times, f, indent=4)

    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=4)

    # Envia os arquivos para o bucket S3:
    if ON_AWS:
        # O arquivo `execution_times.json` é enviado para o bucket com o nome `execution_times.json`
        s3_file = f'{instance_name}/{CURRENT_DATE}/{EXECUTION_FILE}'
        if utils.upload_to_aws(EXECUTION_FILE, BUCKET, s3_file):
            print(f'Arquivo `{EXECUTION_FILE}` enviado para o bucket {BUCKET} com sucesso!')
        else:
            print(f'Erro ao enviar o arquivo `{EXECUTION_FILE}` para o bucket {BUCKET}')

        # O arquivo `results.json` é enviado para o bucket com o nome `results.json`
        s3_file = f'{instance_name}/{CURRENT_DATE}/{RESULTS_FILE}'
        if utils.upload_to_aws(RESULTS_FILE, BUCKET, s3_file):
            print(f'Arquivo `{RESULTS_FILE}` enviado para o bucket {BUCKET} com sucesso!')
        else:
            print(f'Erro ao enviar o arquivo `{RESULTS_FILE}` para o bucket {BUCKET}')

    # Registra o momento de término
    end_time = datetime.now()

    # Calcula a duração total
    duration = end_time - start_time

    # Formata e mostra a duração total
    days, remainder = divmod(duration.total_seconds(), 86400)  # 60 s/min * 60 min/h * 24 h/day
    hours, remainder = divmod(remainder, 3600)  # 60 s/min * 60 min/h
    minutes, seconds = divmod(remainder, 60)  # 60 s/min

    print(
        f'Tempo total de execução: {int(days)} dias, {int(hours)} horas, {int(minutes)} minutos e {int(seconds)} segundos.')
