from scipy.spatial import KDTree
import open3d as o3d
import numpy as np
import teaserpp_python


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


def Rt2T(R, t):
    """
    Função auxiliar para unir a solução rotacionar e solução linear em uma única matriz
    Retirado de: https://github.com/MIT-SPARK/TEASER-plusplus/blob/master/examples/teaser_python_fpfh_icp/helpers.py
    """
    T = np.identity(4)
    T[:3, :3] = R
    T[:3, 3] = t
    return T
