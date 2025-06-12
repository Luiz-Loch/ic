import open3d as o3d
import teaserpp_python
import numpy as np
from project_utils.utils_teaser import establish_correspondences, Rt2T

def robust_global_registration(source_cloud: o3d.geometry.PointCloud,
                               target_cloud: o3d.geometry.PointCloud,
                               source_features: o3d.pipelines.registration.Feature,
                               target_features: o3d.pipelines.registration.Feature,
                               voxel_size: int | float,
                               verbose: bool = False,
                               **kwargs) -> np.ndarray:
    """
    Recebe uma par de nuvem de pontos, bem como seus descritores e realiza *global registration*.
    Utiliza a biblioteca TEASER++.
    Referência: https://github.com/MIT-SPARK/TEASER-plusplus/tree/master/examples/teaser_python_fpfh_icp
    """
    source_corrs, target_corrs = establish_correspondences(source_cloud,
                                                           target_cloud,
                                                           source_features,
                                                           target_features,
                                                           verbose=verbose)

    noise_bound: float = voxel_size

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
    solution = solver.getSolution()
    r = solution.rotation
    t = solution.translation
    return Rt2T(r, t)
