import open3d as o3d
import numpy as np
import time
import torch
from igraph import Graph
from project_utils.decorators import measure_time
from project_utils.point_cloud import FeatureMethod
from project_utils.utils_maximal_cliques import transform, rigid_transform_3d, post_refinement

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


@measure_time
def maximal_cliques(source_cloud: o3d.geometry.PointCloud,
                    target_cloud: o3d.geometry.PointCloud,
                    source_features: o3d.pipelines.registration.Feature,
                    target_features: o3d.pipelines.registration.Feature,
                    voxel_size: int | float,
                    feature_method: FeatureMethod = FeatureMethod.FPFH,
                    verbose: bool = False):
    """"""
    if feature_method == FeatureMethod.FPFH:
        source_features = np.array(source_features.data).T
        source_features = source_features / (np.linalg.norm(source_features, axis=1, keepdims=True) + 1e-6)

        target_features = np.array(target_features.data).T
        target_features = target_features / (np.linalg.norm(target_features, axis=1, keepdims=True) + 1e-6)

    elif feature_method == FeatureMethod.FCGF:
        pass
    else:
        raise ValueError(f"Invalid feature method: {feature_method}")

    distance = np.sqrt(2 - 2 * (source_features @ target_features.T) + 1e-6)
    source_idx = np.argmin(distance, axis=1)  # for each row save the index of minimun
    # feature matching
    corr = np.concatenate([np.arange(source_idx.shape[0])[:, None],
                           source_idx[:, None]],
                          axis=-1)  # n to 1

    if feature_method == FeatureMethod.FPFH:
        src_pts = np.asarray(source_cloud.points, dtype=np.float32)[corr[:, 0]]
        tgt_pts = np.asarray(target_cloud.points, dtype=np.float32)[corr[:, 1]]
    elif feature_method == FeatureMethod.FCGF:
        src_pts = source_cloud[corr[:, 0]]
        tgt_pts = target_cloud[corr[:, 1]]
    else:
        raise ValueError(f"Invalid feature method: {feature_method}")

    src_pts = torch.from_numpy(src_pts).to(device)
    tgt_pts = torch.from_numpy(tgt_pts).to(device)
    t1 = time.perf_counter()
    # graph construction
    inlier_threshold = 0.1
    src_dist = ((src_pts[:, None, :] - src_pts[None, :, :]) ** 2).sum(-1) ** 0.5
    tgt_dist = ((tgt_pts[:, None, :] - tgt_pts[None, :, :]) ** 2).sum(-1) ** 0.5
    cross_dis = torch.abs(src_dist - tgt_dist)
    FCG = torch.clamp(1 - cross_dis ** 2 / inlier_threshold ** 2, min=0)
    FCG = FCG - torch.diag_embed(torch.diag(FCG))
    FCG[FCG < 0.99] = 0
    SCG = torch.matmul(FCG, FCG) * FCG
    t2 = time.perf_counter()

    if verbose:
        print(f'Graph construction: %.2fms' % ((t2 - t1) * 1000))

    # search cliques
    SCG = SCG.cpu().numpy()
    t1 = time.perf_counter()
    graph = Graph.Adjacency((SCG > 0).tolist())
    graph.es['weight'] = SCG[SCG.nonzero()]
    graph.vs['label'] = range(0, corr.shape[0])
    graph.to_undirected()

    macs = graph.maximal_cliques(min=3)
    t2 = time.perf_counter()

    if verbose:
        print(f'Search maximal cliques: %.2fms' % ((t2 - t1) * 1000))
        print(f'Total: %d' % len(macs))

    clique_weight = np.zeros(len(macs), dtype=float)
    for ind in range(len(macs)):
        mac = list(macs[ind])
        if len(mac) >= 3:
            for i in range(len(mac)):
                for j in range(i + 1, len(mac)):
                    clique_weight[ind] = clique_weight[ind] + SCG[mac[i], mac[j]]

    clique_ind_of_node = np.ones(corr.shape[0], dtype=int) * -1
    max_clique_weight = np.zeros(corr.shape[0], dtype=float)
    max_size = 3
    for ind in range(len(macs)):
        mac = list(macs[ind])
        weight = clique_weight[ind]
        if weight > 0:
            for i in range(len(mac)):
                if weight > max_clique_weight[mac[i]]:
                    max_clique_weight[mac[i]] = weight
                    clique_ind_of_node[mac[i]] = ind
                    max_size = len(mac) > max_size and len(mac) or max_size

    filtered_clique_ind = list(set(clique_ind_of_node))
    try:
        filtered_clique_ind.remove(-1)
    except:
        pass

    if verbose:
        print(f'After filtered: %d' % len(filtered_clique_ind))

    group = []
    for s in range(3, max_size + 1):
        group.append([])
    for ind in filtered_clique_ind:
        mac = list(macs[ind])
        group[len(mac) - 3].append(ind)

    tensor_list_A = []
    tensor_list_B = []
    for i in range(len(group)):
        if len(group[i]) == 0:
            continue
        batch_A = src_pts[list(macs[group[i][0]])][None]
        batch_B = tgt_pts[list(macs[group[i][0]])][None]
        if len(group) == 1:
            continue
        for j in range(1, len(group[i])):
            mac = list(macs[group[i][j]])
            src_corr = src_pts[mac][None]
            tgt_corr = tgt_pts[mac][None]
            batch_A = torch.cat((batch_A, src_corr), 0)
            batch_B = torch.cat((batch_B, tgt_corr), 0)
        tensor_list_A.append(batch_A)
        tensor_list_B.append(batch_B)

    max_score = 0
    final_trans = torch.eye(4, device=device)
    for i in range(len(tensor_list_A)):
        trans = rigid_transform_3d(tensor_list_A[i], tensor_list_B[i], None, 0)
        pred_tgt = transform(src_pts[None], trans)  # [bs, num_corr, 3]
        L2_dis = torch.norm(pred_tgt - tgt_pts[None], dim=-1)  # [bs, num_corr]
        MAE_score = torch.div(torch.sub(inlier_threshold, L2_dis), inlier_threshold)
        MAE_score = torch.sum(MAE_score * (L2_dis < inlier_threshold), dim=-1)
        max_batch_score_ind = MAE_score.argmax(dim=-1)
        max_batch_score = MAE_score[max_batch_score_ind]
        if max_batch_score > max_score:
            max_score = max_batch_score
            final_trans = trans[max_batch_score_ind]

    final_trans1 = post_refinement(final_trans[None], src_pts[None], tgt_pts[None], 20, inlier_threshold)

    return final_trans.cpu().numpy()
