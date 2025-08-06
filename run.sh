#!/usr/bin/env bash

STATUS_FILE="./outputs/status.txt"
mkdir -p outputs
echo "Iniciando benchmarks em $(date)" | tee "$STATUS_FILE"


# Lista de comandos
COMMANDS=(
  "python main.py --feature_method FPFH --registration_method RANSAC"
  "python main.py --feature_method FPFH --registration_method FGR"
  "python main.py --feature_method FPFH --registration_method TEASER"
  "python main.py --feature_method FPFH --registration_method DGR       --dgr_model DGR_3DMATCH"
  "python main.py --feature_method FPFH --registration_method DGR       --dgr_model DGR_KITTI"
  "python main.py --feature_method FPFH --registration_method MAC"
  "python main.py --feature_method FPFH --registration_method POINT_DSC --point_dsc_snapshot SNAPSHOT_3DMATCH"
  "python main.py --feature_method FPFH --registration_method POINT_DSC --point_dsc_snapshot SNAPSHOT_KITTI"

  "python main.py --feature_method FCGF --fcgf_model FCGF_3DMATCH --registration_method RANSAC"
  "python main.py --feature_method FCGF --fcgf_model FCGF_3DMATCH --registration_method FGR"
  "python main.py --feature_method FCGF --fcgf_model FCGF_3DMATCH --registration_method TEASER"
  "python main.py --feature_method FCGF --fcgf_model FCGF_3DMATCH --registration_method DGR       --dgr_model DGR_3DMATCH"
  "python main.py --feature_method FCGF --fcgf_model FCGF_3DMATCH --registration_method DGR       --dgr_model DGR_KITTI"
  "python main.py --feature_method FCGF --fcgf_model FCGF_3DMATCH --registration_method MAC"
  "python main.py --feature_method FCGF --fcgf_model FCGF_3DMATCH --registration_method POINT_DSC --point_dsc_snapshot SNAPSHOT_3DMATCH"
  "python main.py --feature_method FCGF --fcgf_model FCGF_3DMATCH --registration_method POINT_DSC --point_dsc_snapshot SNAPSHOT_KITTI"

  "python main.py --feature_method FCGF --fcgf_model FCGF_KITTI --registration_method RANSAC"
  "python main.py --feature_method FCGF --fcgf_model FCGF_KITTI --registration_method FGR"
  "python main.py --feature_method FCGF --fcgf_model FCGF_KITTI --registration_method TEASER"
  "python main.py --feature_method FCGF --fcgf_model FCGF_KITTI --registration_method DGR       --dgr_model DGR_3DMATCH"
  "python main.py --feature_method FCGF --fcgf_model FCGF_KITTI --registration_method DGR       --dgr_model DGR_KITTI"
  "python main.py --feature_method FCGF --fcgf_model FCGF_KITTI --registration_method MAC"
  "python main.py --feature_method FCGF --fcgf_model FCGF_KITTI --registration_method POINT_DSC --point_dsc_snapshot SNAPSHOT_3DMATCH"
  "python main.py --feature_method FCGF --fcgf_model FCGF_KITTI --registration_method POINT_DSC --point_dsc_snapshot SNAPSHOT_KITTI"
)

# Loop para executar os comandos
for CMD in "${COMMANDS[@]}"; do
  echo -e "\nExecutando: $CMD" | tee -a "$STATUS_FILE"

  # Executa o comando e deixa stdout/stderr no terminal
  eval $CMD
  EXIT_CODE=$?

  if [ $EXIT_CODE -eq 0 ]; then
    echo "Terminado com sucesso." | tee -a "$STATUS_FILE"
  else
    echo "Terminado com erro (código $EXIT_CODE)." | tee -a "$STATUS_FILE"
  fi
done

echo -e "\nTodos os benchmarks finalizados em $(date)." | tee -a "$STATUS_FILE"