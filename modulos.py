from decorators import measure_time
import open3d as o3d
import numpy as np
import copy
import os
import requests
import boto3
from botocore.exceptions import NoCredentialsError
from scipy.spatial import KDTree
import teaserpp_python


# ######################################################################################
# Funções para uso dentro da AWS:
def upload_to_aws(local_file: str, bucket: str, s3_file: str) -> bool:
    """
        Faz o upload de um arquivo para o S3.
    """
    s3 = boto3.client('s3')

    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False


def get_instance_id() -> str | None:
    """
        Função para obter o ID da instância
    """
    try:
        # Obter o token
        token_url = 'http://169.254.169.254/latest/api/token'
        token_headers = {'X-aws-ec2-metadata-token-ttl-seconds': '21600'}
        token_response = requests.put(token_url, headers=token_headers)
        token = token_response.text

        # Usar o token para acessar os metadados
        metadata_url = 'http://169.254.169.254/latest/meta-data/instance-id'
        metadata_headers = {'X-aws-ec2-metadata-token': token}
        response = requests.get(metadata_url, headers=metadata_headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Erro ao obter o ID da instância: {e}")
        return None


def get_instance_name(instance_id: str | None, region_name: str = 'us-east-1') -> str | None:
    """
        Função para obter o nome da instância (Tag "Name")
    """
    try:
        ec2 = boto3.client('ec2', region_name=region_name)
        response = ec2.describe_instances(InstanceIds=[instance_id])
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                for tag in instance.get('Tags', []):
                    if tag['Key'] == 'Name':
                        return tag['Value']
        return None
    except Exception as e:
        print(f"Erro ao obter o nome da instância: {e}")
        return None


def get_container_or_instance_name(region_name: str = 'us-east-1') -> str | None:
    """
        Função para obter o nome da instância ou do contêiner
    """
    instance_id = get_instance_id()
    if instance_id:
        # Se a instância estiver em execução no EC2, tente obter o nome da instância
        instance_name = get_instance_name(instance_id, region_name)
        if instance_name:
            return instance_name

    # Se não for possível obter o nome da instância, tente obter o nome do contêiner ECS
    try:
        ecs_metadata_url = 'http://169.254.170.2/v2/metadata'
        response = requests.get(ecs_metadata_url)
        response.raise_for_status()
        metadata = response.json()

        # Coleta o nome da tarefa ECS
        task_name = metadata.get('TaskARN').split('/')[-1]
        return task_name
    except requests.RequestException:
        # Se não for possível obter o nome do contêiner, retorne None
        return None


# ######################################################################################
# Funções para:
# - Carragamento e pré-processamento dos dados
# - Métricas de avaliação
# - Coleta das nuvens de dados a partir do arquivo `gt.log`

def load_point_cloud(file_path: str) -> o3d.geometry.PointCloud:
    """
        Carrega um arquivo de ponto 3D em um objeto PointCloud.
    """
    # Carrega nuvem de pontos a partir do arquivo especificado
    cloud = o3d.io.read_point_cloud(file_path)
    return cloud


@measure_time
def preprocess_point_clouds(source_cloud: o3d.geometry.PointCloud,
                            target_cloud: o3d.geometry.PointCloud,
                            voxel_size: int | float,
                            verbose: bool = False):
    """
        Recebe duas nuvens de pontos e aplica o pre-processamento:
        - Redimensiona a nuvem de pontos para o tamanho especificado;
        - Calcula as normais;
        - Calcula o descritor FPFH;
        Referência: https://www.open3d.org/docs/release/tutorial/pipelines/global_registration.html#Extract-geometric-feature
    """
    radius_normal = voxel_size * 2
    radius_feature = voxel_size * 5
    if verbose:
        print(
            f"Redimensionando a nuvem de pontos para o tamanho {voxel_size:0.03f}.")
    source_cloud_downsampled = source_cloud.voxel_down_sample(voxel_size)
    target_cloud_downsampled = target_cloud.voxel_down_sample(voxel_size)
    if verbose:
        print(
            f"Calculando as normais com busca de raio {radius_normal:0.03f}.")
    source_cloud_downsampled.estimate_normals(
        o3d.geometry.KDTreeSearchParamHybrid(radius=radius_normal, max_nn=30))

    target_cloud_downsampled.estimate_normals(
        o3d.geometry.KDTreeSearchParamHybrid(radius=radius_normal, max_nn=30))

    source_feature = o3d.pipelines.registration.compute_fpfh_feature(
        source_cloud_downsampled, o3d.geometry.KDTreeSearchParamHybrid(radius=radius_feature, max_nn=100))

    target_feature = o3d.pipelines.registration.compute_fpfh_feature(
        target_cloud_downsampled, o3d.geometry.KDTreeSearchParamHybrid(radius=radius_feature, max_nn=100))

    return source_cloud_downsampled, target_cloud_downsampled, source_feature, target_feature


def tre(T_est: np.ndarray, T_gt: np.ndarray) -> float:
    """
    Calcula o erro de translação entre as matrizes de transformação.
    Em caso de erro, retorna infinito (`np.inf`).
    """
    try:
        return np.linalg.norm(T_est[:3, 3] - T_gt[:3, 3])
    except:
        return np.inf


def rre(T_est, T_gt) -> float:
    """
    Calcula o erro angular entre as rotações das matrizes de transformação.
    Em caso de erro, retorna infinito (`np.inf`).
    """
    try:
        return np.arccos((np.trace(T_est[:3, :3].T @ T_gt[:3, :3]) - 1) / 2)
    except:
        return np.inf


def read_gt_log(file_path: str, verbose: bool = False) -> tuple[int, int, np.ndarray]:
    """
        Lê um arquivo  `gt.log` de transformação e retorna uma lista de tuplas.
    """
    if verbose:
        print("#" * 50)
        print(f"Dentro da função {read_gt_log.__name__}.")
        print(f"Lendo o arquivo {file_path}.")
    with open(file_path, 'r') as f:
        if verbose:
            print(f"Arquivo {file_path} aberto com sucesso.")
        lines = f.readlines()
    if verbose:
        print(f"O arquivo {file_path} possui {len(lines)} linhas.")
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
        Retorna uma lista de tuplas com os caminhos dos arquivos `gt.log`, `source.ply` e `target.ply`.
    """
    if verbose:
        print("#" * 50)
        print(f"Dentro da função {get_datasets.__name__}.")
        print(f"Procurando arquivos `gt.log` dentro do diretório {data_dir}.")
    for root, dirs, files in os.walk(data_dir):
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


def draw_registration_result(source: o3d.geometry.PointCloud, target: o3d.geometry.PointCloud, transformation) -> None:
    """
        Desenha as nuvens de pontos alinhadas.
    """
    voxel_size = 0.10
    source_temp = copy.deepcopy(source)
    target_temp = copy.deepcopy(target)

    source_temp.voxel_down_sample(voxel_size)
    target_temp.voxel_down_sample(voxel_size)

    source_temp.paint_uniform_color([1, 0.706, 0])
    target.paint_uniform_color([0, 0.651, 0.929])

    source_temp.transform(transformation)
    o3d.visualization.draw_plotly([source_temp, target_temp])


# ######################################################################################
# Processamento dos dados com a biblioteca Open3D
#     - Global registration usando RANSAC
#     - Fast Global Registration
#     - ICP com o método de ponto a ponto
#     - ICP com o método de ponto a plano

@measure_time
def global_registration(source_cloud: o3d.geometry.PointCloud,
                        target_cloud: o3d.geometry.PointCloud,
                        source_features: o3d.pipelines.registration.Feature,
                        target_features: o3d.pipelines.registration.Feature,
                        voxel_size: int | float,
                        verbose: bool = False) -> o3d.pipelines.registration.RegistrationResult:
    """
        Recebe uma par de nuvem de pontos, bem como seus descritores e realiza *global registration*.
        Utiliza o método RANSAC da biblioteca Open3D.
        Referência: https://www.open3d.org/docs/release/tutorial/pipelines/global_registration.html#RANSAC
    """
    distance_threshold = voxel_size * 1.5
    max_iteration = 100000
    confidence = 0.999
    if verbose:
        print("Realiza o alinhamento grosseiro usando o método RANSAC.")
        print(f"O raio de busca é {distance_threshold:0.03f}.")
    result = o3d.pipelines.registration.registration_ransac_based_on_feature_matching(
        source_cloud, target_cloud, source_features, target_features, True,
        distance_threshold,
        o3d.pipelines.registration.TransformationEstimationPointToPoint(False),
        3, [
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnEdgeLength(
                0.9),
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnDistance(
                distance_threshold)
        ],
        o3d.pipelines.registration.RANSACConvergenceCriteria(
            max_iteration, confidence))
    # Executa até atingir `max_iteration` ou `confidence`.
    return result


@measure_time
def fast_global_registration(source_cloud: o3d.geometry.PointCloud,
                             target_cloud: o3d.geometry.PointCloud,
                             source_features: o3d.pipelines.registration.Feature,
                             target_features: o3d.pipelines.registration.Feature,
                             voxel_size: int | float,
                             verbose: bool = False) -> o3d.pipelines.registration.RegistrationResult:
    """
         Recebe uma par de nuvem de pontos, bem como seus descritores e realiza *fast global registration*.
         Referência: https://www.open3d.org/docs/release/tutorial/pipelines/global_registration.html#id2
    """
    distance_threshold = voxel_size * 0.5
    if verbose:
        print("Realiza o *fast global registration*.")
        print(f"O raio de busca é {distance_threshold:0.03f}.")
    result = o3d.pipelines.registration.registration_fgr_based_on_feature_matching(
        source_cloud, target_cloud, source_features, target_features,
        o3d.pipelines.registration.FastGlobalRegistrationOption(
            maximum_correspondence_distance=distance_threshold))
    return result


@measure_time
def fine_alignment_point_to_point(source_cloud: o3d.geometry.PointCloud,
                                  target_cloud: o3d.geometry.PointCloud,
                                  initial_transform: np.ndarray,
                                  voxel_size: int | float,
                                  verbose: bool = False) -> o3d.pipelines.registration.RegistrationResult:
    """
        Recebe um par de nuvem de pontos, bem como uma transformação inicial para realizar um alinhamento fino.
        Utiliza o método Point to Point da biblioteca Open3D.
        Referência: https://www.open3d.org/docs/release/tutorial/pipelines/global_registration.html#Local-refinement
    """
    distance_threshold = voxel_size * 0.4
    icp_method = o3d.pipelines.registration.TransformationEstimationPointToPoint()
    if verbose:
        print("Realizando o alinhamento com ICP - Point to Point")
    result = o3d.pipelines.registration.registration_icp(source_cloud, target_cloud, distance_threshold,
                                                         initial_transform, icp_method)
    return result


@measure_time
def fine_alignment_point_to_plane(source_cloud: o3d.geometry.PointCloud,
                                  target_cloud: o3d.geometry.PointCloud,
                                  initial_transform: np.ndarray,
                                  voxel_size: int | float,
                                  verbose: bool = False) -> o3d.pipelines.registration.RegistrationResult:
    """
        Recebe um par de nuvem de pontos, bem como uma transformação inicial para realizar um alinhamento fino.
        Utiliza o método Point to Plane da biblioteca Open3D.
        Referência: https://www.open3d.org/docs/release/tutorial/pipelines/global_registration.html#Local-refinement
    """
    distance_threshold = voxel_size * 0.4
    icp_method = o3d.pipelines.registration.TransformationEstimationPointToPlane()
    if verbose:
        print("Realizando o alinhamento com ICP - Point to Plane com ")
    result = o3d.pipelines.registration.registration_icp(source_cloud, target_cloud, distance_threshold,
                                                         initial_transform, icp_method)
    return result


# ######################################################################################
# Processamento dos dados com a biblioteca TEASER++
# E algumas funções auxiliares necessárias.

def pcd2xyz(pcd: o3d.geometry.PointCloud):
    """
        Função auxiliar para converter um objeto PointCloud em um array numpy.
        Usando em `establish_correspondences()`
        Retirado de: https://github.com/MIT-SPARK/TEASER-plusplus/blob/master/examples/teaser_python_fpfh_icp/helpers.py
    """
    return np.asarray(pcd.points).T


def find_knn_cpu(feat0, feat1, knn=1, return_distance=False):
    """
        Função auxiliar para executar `find_correspondences()`
        Retirado de: https://github.com/MIT-SPARK/TEASER-plusplus/blob/master/examples/teaser_python_fpfh_icp/helpers.py
    """
    # feat1tree = cKDTree(feat1) # Documentação recomenda usar KDTree em vez de cKDTree
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.cKDTree.html
    feat1tree = KDTree(feat1)
    # feat1tree = o3d.geometry.KDTreeFlann(feat1) # Open3D KDTree
    # dists, nn_inds = feat1tree.query(feat0, k=knn, n_jobs=-1) # n_jobs=-1 is not supported in cKDTree
    dists, nn_inds = feat1tree.query(feat0, k=knn, workers=-1)
    if return_distance:
        return nn_inds, dists
    else:
        return nn_inds


def find_correspondences(feats0, feats1, mutual_filter=True):
    """
        Função necessária para executar `establish_correspondences()`
        Retirado de: https://github.com/MIT-SPARK/TEASER-plusplus/blob/master/examples/teaser_python_fpfh_icp/helpers.py
    """
    nns01 = find_knn_cpu(feats0, feats1, knn=1, return_distance=False)
    corres01_idx0 = np.arange(len(nns01))
    corres01_idx1 = nns01

    if not mutual_filter:
        return corres01_idx0, corres01_idx1

    nns10 = find_knn_cpu(feats1, feats0, knn=1, return_distance=False)
    corres10_idx1 = np.arange(len(nns10))
    corres10_idx0 = nns10

    mutual_filter = (corres10_idx0[corres01_idx1] == corres01_idx0)
    corres_idx0 = corres01_idx0[mutual_filter]
    corres_idx1 = corres01_idx1[mutual_filter]
    return corres_idx0, corres_idx1


def establish_correspondences(source_cloud: o3d.geometry.PointCloud,
                              target_cloud: o3d.geometry.PointCloud,
                              source_features: o3d.pipelines.registration.Feature,
                              target_features: o3d.pipelines.registration.Feature,
                              verbose: bool = False):
    """
        Estabelece correspondências entre os pontos de uma nuvem de pontos.
        Necessário para a função `robust_global_registration()`
        Referência: https://github.com/MIT-SPARK/TEASER-plusplus/tree/master/examples/teaser_python_fpfh_icp#4-establish-putative-correspondences
    """

    # Converte os descritores em arrays numpy
    source_features_xyz = np.array(source_features.data).T
    target_features_xyz = np.array(target_features.data).T

    # Converte as nuvens de pontos em arrays numpy
    source_cloud_xyz = pcd2xyz(source_cloud)  # np array of size 3 by N
    target_cloud_xyz = pcd2xyz(target_cloud)  # np array of size 3 by M

    source_corrs, target_corrs = find_correspondences(source_features_xyz,
                                                      target_features_xyz,
                                                      mutual_filter=True)
    source_corrs = source_cloud_xyz[:, source_corrs]  # np array of size 3 by num_corrs
    target_corrs = target_cloud_xyz[:, target_corrs]  # np array of size 3 by num_corrs
    if verbose:
        num_corrs = source_corrs.shape[1]
        print(f'FPFH gerou {num_corrs} correspondências.')
    return source_corrs, target_corrs


@measure_time
def robust_global_registration(source_cloud: o3d.geometry.PointCloud,
                               target_cloud: o3d.geometry.PointCloud,
                               source_features: o3d.pipelines.registration.Feature,
                               target_features: o3d.pipelines.registration.Feature,
                               voxel_size: int | float,
                               verbose: bool = False):
    """
    Recebe uma par de nuvem de pontos, bem como seus descritores e realiza *global registration*.
    Utiliza a biblioteca TEASER++.
    Referência: https://github.com/MIT-SPARK/TEASER-plusplus/tree/master/examples/teaser_python_fpfh_icp
    """
    source_corrs, target_corrs = establish_correspondences(source_cloud, target_cloud, source_features, target_features,
                                                           verbose=verbose)

    noise_bound = voxel_size
    if verbose:
        print("Configurando os parâmetros do TEASER++.")
    solver_params = teaserpp_python.RobustRegistrationSolver.Params()
    solver_params.cbar2 = 1.0
    solver_params.noise_bound = noise_bound
    solver_params.estimate_scaling = False
    solver_params.inlier_selection_mode = teaserpp_python.RobustRegistrationSolver.INLIER_SELECTION_MODE.PMC_EXACT
    solver_params.rotation_tim_graph = teaserpp_python.RobustRegistrationSolver.INLIER_GRAPH_FORMULATION.CHAIN
    solver_params.rotation_estimation_algorithm = teaserpp_python.RobustRegistrationSolver.ROTATION_ESTIMATION_ALGORITHM.GNC_TLS
    solver_params.rotation_gnc_factor = 1.4
    solver_params.rotation_max_iterations = 10000
    solver_params.rotation_cost_threshold = 1e-16
    if verbose:
        print("Realiza o alinhamento grosseiro usando o método TEASER++.")
    solver = teaserpp_python.RobustRegistrationSolver(solver_params)
    solver.solve(source_corrs, target_corrs)
    return solver.getSolution()


def Rt2T(R, t):
    """
        Função auxiliar para unir a solução rotacionar e solução linear em uma única matriz
        Retirado de: https://github.com/MIT-SPARK/TEASER-plusplus/blob/master/examples/teaser_python_fpfh_icp/helpers.py
    """
    T = np.identity(4)
    T[:3, :3] = R
    T[:3, 3] = t
    return T

# ######################################################################################
