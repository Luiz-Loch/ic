from tqdm import tqdm, trange
from datetime import datetime
import json
import modulos

if __name__ == '__main__':
    VERBOSE = False
    NUM_OF_EXEC = 1
    voxel_sizes = (0.05,)
    DATASETS = modulos.get_datasets('./data/3DMatch/rgbd-scenes-v2-scene_10')
    CURRENT_DATE = datetime.now().strftime('%Y-%m-%d')
    # Registra o momento de início
    start_time = datetime.now()
    DO_ICP = False

    ON_AWS = False
    BUCKET = 'benchmarks-ic'
    region_name = 'us-east-1'

    execution_times = {}
    EXECUTION_FILE = 'execution_times.json'
    results = {}
    RESULTS_FILE = 'results.json'

    # Obter ID e Nome da Instância
    if ON_AWS:
        instance_id = modulos.get_instance_id()
        instance_name = modulos.get_instance_name(instance_id)
        print(f'ID da Instância: {instance_id}')
        if instance_name:
            print(f'Nome da Instância: {instance_name}')
        else:
            print('Nome da Instância não encontrado')

    for target_ply_path, source_ply_path, t_gt in tqdm(DATASETS):
        # As matrizes `t_gt` foram calculadas a partir da target -> source
        # Então, para manter o padrão e não precisar calcular a inversa de `t_gt`
        # A ordem das nuvem foi invertida

        # Cria as chaves para os dicionários:
        key_img = f'Source: {source_ply_path}; Target: {target_ply_path}'
        execution_times[key_img] = {}
        results[key_img] = {}

        # Carrega os dados:
        source_cloud = modulos.load_point_cloud(source_ply_path)
        target_cloud = modulos.load_point_cloud(target_ply_path)

        results[key_img]['length of source'] = len(source_cloud.points)
        results[key_img]['length of target'] = len(target_cloud.points)

        for voxel_size in tqdm(voxel_sizes):
            key_voxel = f'voxel: {voxel_size}'
            execution_times[key_img][key_voxel] = {}
            results[key_img][key_voxel] = {}

            for run in trange(NUM_OF_EXEC):
                run_key = f'run: {run}'
                execution_times[key_img][key_voxel][run_key] = {}
                results[key_img][key_voxel][run_key] = {}

                # Aplica o pre-processamento:
                # Por causa do decorator, a função `preprocess_point_clouds` retorna uma tupla com os resultados e o tempo de execução
                results_preprocess, execution_time = modulos.preprocess_point_clouds(source_cloud, target_cloud,
                                                                                     voxel_size)
                source_down, target_down, source_features, target_features = results_preprocess
                execution_times[key_img][key_voxel][run_key]['preprocess'] = execution_time

                # Aplica o alinhamento RANSAC:
                result_gr, execution_time = modulos.global_registration(source_down, target_down, source_features,
                                                                        target_features,
                                                                        voxel_size)
                execution_times[key_img][key_voxel][run_key]['RANSAC'] = execution_time
                results[key_img][key_voxel][run_key]['RANSAC'] = {}
                results[key_img][key_voxel][run_key]['RANSAC']['transformation'] = result_gr.transformation.tolist()
                results[key_img][key_voxel][run_key]['RANSAC']['tre'] = modulos.tre(result_gr.transformation, t_gt)
                results[key_img][key_voxel][run_key]['RANSAC']['rre'] = modulos.rre(result_gr.transformation, t_gt)

                # Aplica o alinhamento FGR:
                result_fgr, execution_time = modulos.fast_global_registration(source_down, target_down, source_features,
                                                                              target_features, voxel_size)
                execution_times[key_img][key_voxel][run_key]['Fast Global Registration'] = execution_time
                results[key_img][key_voxel][run_key]['Fast Global Registration'] = {}
                results[key_img][key_voxel][run_key]['Fast Global Registration'][
                    'transformation'] = result_fgr.transformation.tolist()
                results[key_img][key_voxel][run_key]['Fast Global Registration']['tre'] = modulos.tre(
                    result_fgr.transformation, t_gt)
                results[key_img][key_voxel][run_key]['Fast Global Registration']['rre'] = modulos.rre(
                    result_fgr.transformation, t_gt)

                if DO_ICP:
                    # Refina o alinhamento RANSAC com ICP Point-to-Point:
                    result_gr_icp_point, execution_time = modulos.fine_alignment_point_to_point(source_down,
                                                                                                target_down,
                                                                                                result_gr.transformation,
                                                                                                voxel_size)
                    execution_times[key_img][key_voxel][run_key]['RANSAC -> ICP_Point'] = execution_time
                    results[key_img][key_voxel][run_key]['RANSAC + ICP_Point'] = {}
                    results[key_img][key_voxel][run_key]['RANSAC + ICP_Point'][
                        'transformation'] = result_gr_icp_point.transformation.tolist()
                    results[key_img][key_voxel][run_key]['RANSAC + ICP_Point']['tre'] = modulos.tre(
                        result_gr_icp_point.transformation, t_gt)
                    results[key_img][key_voxel][run_key]['RANSAC + ICP_Point']['rre'] = modulos.rre(
                        result_gr_icp_point.transformation, t_gt)

                    # Refina o alinhamento RANSAC com ICP Point-to-Plane:
                    result_gr_icp_plane, execution_time = modulos.fine_alignment_point_to_plane(source_down,
                                                                                                target_down,
                                                                                                result_gr.transformation,
                                                                                                voxel_size)
                    execution_times[key_img][key_voxel][run_key]['RANSAC -> ICP_Plane'] = execution_time
                    results[key_img][key_voxel][run_key]['RANSAC + ICP_Plane'] = {}
                    results[key_img][key_voxel][run_key]['RANSAC + ICP_Plane'][
                        'transformation'] = result_gr_icp_plane.transformation.tolist()
                    results[key_img][key_voxel][run_key]['RANSAC + ICP_Plane']['tre'] = modulos.tre(
                        result_gr_icp_plane.transformation, t_gt)
                    results[key_img][key_voxel][run_key]['RANSAC + ICP_Plane']['rre'] = modulos.rre(
                        result_gr_icp_plane.transformation, t_gt)

                    # Refina o alinhamento FGR com ICP Point-to-Point:
                    result_fgr_icp_point, execution_time = modulos.fine_alignment_point_to_point(source_down,
                                                                                                 target_down,
                                                                                                 result_fgr.transformation,
                                                                                                 voxel_size)
                    execution_times[key_img][key_voxel][run_key][
                        'Fast Global Registration -> ICP_Point'] = execution_time
                    results[key_img][key_voxel][run_key]['Fast Global Registration + ICP_Point'] = {}
                    results[key_img][key_voxel][run_key]['Fast Global Registration + ICP_Point'][
                        'transformation'] = result_fgr_icp_point.transformation.tolist()
                    results[key_img][key_voxel][run_key]['Fast Global Registration + ICP_Point']['tre'] = modulos.tre(
                        result_fgr_icp_point.transformation, t_gt)
                    results[key_img][key_voxel][run_key]['Fast Global Registration + ICP_Point']['rre'] = modulos.rre(
                        result_fgr_icp_point.transformation, t_gt)

                    # Refina o alinhamento FGR com ICP Point-to-Plane:
                    result_fgr_icp_plane, execution_time = modulos.fine_alignment_point_to_plane(source_down,
                                                                                                 target_down,
                                                                                                 result_fgr.transformation,
                                                                                                 voxel_size)
                    execution_times[key_img][key_voxel][run_key][
                        'Fast Global Registration -> ICP_Plane'] = execution_time
                    results[key_img][key_voxel][run_key]['Fast Global Registration + ICP_Plane'] = {}
                    results[key_img][key_voxel][run_key]['Fast Global Registration + ICP_Plane'][
                        'transformation'] = result_fgr_icp_plane.transformation.tolist()
                    results[key_img][key_voxel][run_key]['Fast Global Registration + ICP_Plane']['tre'] = modulos.tre(
                        result_fgr_icp_plane.transformation, t_gt)
                    results[key_img][key_voxel][run_key]['Fast Global Registration + ICP_Plane']['rre'] = modulos.rre(
                        result_fgr_icp_plane.transformation, t_gt)

                # ########################### TEASE++ ###########################
                result_teaser, execution_time = modulos.robust_global_registration(source_down, target_down,
                                                                                   source_features,
                                                                                   target_features,
                                                                                   voxel_size)

                R_teaser = result_teaser.rotation
                t_teaser = result_teaser.translation
                T_teaser = modulos.Rt2T(R_teaser, t_teaser)

                execution_times[key_img][key_voxel][run_key]['Robust Global Registration'] = execution_time
                results[key_img][key_voxel][run_key]['Robust Global Registration'] = {}
                results[key_img][key_voxel][run_key]['Robust Global Registration']['transformation'] = T_teaser.tolist()
                results[key_img][key_voxel][run_key]['Robust Global Registration']['tre'] = modulos.tre(T_teaser, t_gt)
                results[key_img][key_voxel][run_key]['Robust Global Registration']['rre'] = modulos.rre(T_teaser, t_gt)

                # Refina o alinhamento TEASER com ICP Point-to-Point:
                if DO_ICP:
                    result_teaser_icp_point, execution_time = modulos.fine_alignment_point_to_point(source_down,
                                                                                                    target_down,
                                                                                                    T_teaser,
                                                                                                    voxel_size)
                    execution_times[key_img][key_voxel][run_key][
                        'Robust Global Registration -> ICP_Point'] = execution_time
                    results[key_img][key_voxel][run_key]['Robust Global Registration + ICP_Point'] = {}
                    results[key_img][key_voxel][run_key]['Robust Global Registration + ICP_Point'][
                        'transformation'] = result_teaser_icp_point.transformation.tolist()
                    results[key_img][key_voxel][run_key]['Robust Global Registration + ICP_Point']['tre'] = modulos.tre(
                        result_teaser_icp_point.transformation, t_gt)
                    results[key_img][key_voxel][run_key]['Robust Global Registration + ICP_Point']['rre'] = modulos.rre(
                        result_teaser_icp_point.transformation, t_gt)

                    # Refina o alinhamento TEASER com ICP Point-to-Plane:
                    result_teaser_icp_plane, execution_time = modulos.fine_alignment_point_to_plane(source_down,
                                                                                                    target_down,
                                                                                                    T_teaser,
                                                                                                    voxel_size)
                    execution_times[key_img][key_voxel][run_key][
                        'Robust Global Registration -> ICP_Plane'] = execution_time
                    results[key_img][key_voxel][run_key]['Robust Global Registration + ICP_Plane'] = {}
                    results[key_img][key_voxel][run_key]['Robust Global Registration + ICP_Plane'][
                        'transformation'] = result_teaser_icp_plane.transformation.tolist()
                    results[key_img][key_voxel][run_key]['Robust Global Registration + ICP_Plane']['tre'] = modulos.tre(
                        result_teaser_icp_plane.transformation, t_gt)
                    results[key_img][key_voxel][run_key]['Robust Global Registration + ICP_Plane']['rre'] = modulos.rre(
                        result_teaser_icp_plane.transformation, t_gt)

                # ########################### ####### ###########################

    with open(EXECUTION_FILE, 'w') as f:
        json.dump(execution_times, f, indent=4)

    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=4)

    # Envia os arquivos para o bucket S3:
    if ON_AWS:
        # O arquivo `execution_times.json` é enviado para o bucket com o nome `execution_times.json`
        s3_file = f'{instance_name}/{CURRENT_DATE}/{EXECUTION_FILE}'
        if modulos.upload_to_aws(EXECUTION_FILE, BUCKET, s3_file):
            print(f'Arquivo `{EXECUTION_FILE}` enviado para o bucket {BUCKET} com sucesso!')
        else:
            print(f'Erro ao enviar o arquivo `{EXECUTION_FILE}` para o bucket {BUCKET}')

        # O arquivo `results.json` é enviado para o bucket com o nome `results.json`
        s3_file = f'{instance_name}/{CURRENT_DATE}/{RESULTS_FILE}'
        if modulos.upload_to_aws(RESULTS_FILE, BUCKET, s3_file):
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
