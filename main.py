#!/usr/bin/env python
import argparse
import os
from datetime import datetime

import pandas as pd
from tqdm import tqdm, trange

import project_utils
from project_config import get_config

if __name__ == "__main__":
    config: argparse.Namespace = get_config()
    # project_utils.download_models() # Downloads the models of DGR and FCGF

    verbose: bool = config.verbose
    num_of_exec: int = config.num_of_exec
    voxel_sizes: list[float] = config.voxel_sizes
    dataset: project_utils.DataSetType = config.dataset
    feature_method: project_utils.FeatureMethod = config.feature_method
    # fcgf_model: project_utils.FCGFModels = config.fcgf_model
    registration_method: project_utils.RegistrationMethod = config.registration_method
    # dgr_model = config.dgr_model
    point_dsc_snapshot = config.point_dsc_snapshot
    do_icp: bool = config.do_icp
    results_file: str = config.results_file

    fcgf_model = None  # temp
    dgr_model = None  # temp

    results: list[list] = []
    header: list[str] = [
        "RUN",
        "SOURCE DATASET",
        "SOURCE SCENE",
        "SOURCE FRAME",
        "SOURCE NUMBER OF POINTS",
        "SOURCE LOAD TIME",
        "TARGET DATASET",
        "TARGET SCENE",
        "TARGET FRAME",
        "TARGET NUMBER OF POINTS",
        "TARGET LOAD TIME",
        "VOXEL SIZE",
        "PREPROCESS FEATURE METHOD",
        "PREPROCESS MODEL",
        "PREPROCESS TIME",
        "REGISTRATION METHOD",
        "REGISTRATION MODEL",
        "REGISTRATION TIME",
        "REGISTRATION TRANSFORMATION",
        "ICP METHOD",
        "ICP TIME",
        "ICP TRANSFORMATION",
    ]
    results.append(header)

    for target_ply_path, source_ply_path, t_gt in tqdm(dataset.datasets):
        log_time: str = datetime.now().strftime("%H:%M:%S")
        source_dataset, source_scene, source_frame = project_utils.get_dataset_info(source_ply_path)
        target_dataset, target_scene, target_frame = project_utils.get_dataset_info(target_ply_path)
        tqdm.write(f"[{log_time}] Running {registration_method.value[0]} on {source_dataset} {source_scene}")
        tqdm.write(f"[{log_time}] Source: {source_frame}, Target: {target_frame}")

        for voxel_size in voxel_sizes:
            for run in trange(num_of_exec, leave=False):
                # Load the point clouds
                source_cloud, source_cloud_load_time = project_utils.load_point_cloud(source_ply_path)
                target_cloud, target_cloud_load_time = project_utils.load_point_cloud(target_ply_path)

                # Preprocess the point clouds
                results_preprocess, preprocess_time = project_utils.preprocess_point_clouds(source_cloud,
                                                                                            target_cloud,
                                                                                            voxel_size,
                                                                                            feature_method,
                                                                                            # fcgf_model
                                                                                            )
                source_down, target_down, source_features, target_features = (results_preprocess)

                # Apply the registration
                registration_result, registration_time = registration_method.run(source_down,
                                                                                 target_down,
                                                                                 source_features,
                                                                                 target_features,
                                                                                 voxel_size,
                                                                                 # dgr_model=dgr_model,
                                                                                 point_dsc_snapshot=point_dsc_snapshot,
                                                                                 )

                # Apply the ICP refinement and save the results with icp
                if do_icp:
                    for icp_method, icp_function in [("Point-to-Point", project_utils.fine_alignment_point_to_point),
                                                     ("Point-to-Plane", project_utils.fine_alignment_point_to_plane),
                                                     ]:
                        icp_result, icp_time = icp_function(source_down, target_down, registration_result, voxel_size)

                        # Save the results
                        results.append([
                            run,
                            source_dataset,
                            source_scene,
                            source_frame,
                            len(source_cloud.points),
                            source_cloud_load_time,
                            source_dataset,
                            source_scene,
                            source_frame,
                            len(target_cloud.points),
                            target_cloud_load_time,
                            voxel_size,
                            feature_method.value,
                            feature_method.model(fcgf_model),
                            preprocess_time,
                            registration_method.value[0],
                            registration_method.model(dgr_model, point_dsc_snapshot),
                            registration_time,
                            registration_result.tolist(),
                            icp_method,
                            icp_time,
                            icp_result,
                        ])

                # Save the results without icp
                else:
                    results.append([
                        run,
                        source_dataset,
                        source_scene,
                        source_frame,
                        len(source_cloud.points),
                        source_cloud_load_time,
                        source_dataset,
                        source_scene,
                        source_frame,
                        len(target_cloud.points),
                        target_cloud_load_time,
                        voxel_size,
                        feature_method.value[0],
                        feature_method.model(fcgf_model),
                        preprocess_time,
                        registration_method.value,
                        registration_method.model(dgr_model, point_dsc_snapshot),
                        registration_time,
                        registration_result.tolist(),
                        None,
                        None,
                        None,
                    ])

                # Save the results to a csv file
                os.makedirs(os.path.dirname(results_file), exist_ok=True)
                df = pd.DataFrame(results[1:], columns=results[0])  # Ignore the header row
                df.to_csv(results_file, index=False, encoding="UTF-8")
