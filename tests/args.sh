#!/usr/bin/env bash

# Caminho para o script Python a ser testado
SCRIPT="python tests/args.py"

# Lista de combinações de argumentos para testar
ARGUMENTS=(
    "--verbose true"
    "--verbose false"
    "--num_of_exec 10"
    "--num_of_exec 1"
    "--voxel_sizes 0.2"
    "--voxel_sizes 0.2 0.5"
    "--dataset ETH"
    "--dataset ALL"
    "--dataset _3DMatch"
    "--feature_method fpfh"
    "--feature_method FCGF"
    "--fcgf_model FCGF_3DMATCH"
    "--fcgf_model FCGF_kitti"
    "--registration_method ransac"
    "--registration_method fgr"
    "--registration_method teaser"
    "--registration_method dgr"
    "--registration_method mac"
    "--registration_method point_dsc"
    "--do_icp true"
    "--do_icp false"
)

# Códigos de cores ANSI
GREEN="\033[0;32m"
RED="\033[0;31m"
NC="\033[0m" # Sem cor

# Loop para testar cada conjunto de argumentos
for ARGS in "${ARGUMENTS[@]}"; do
    echo "Testando com argumentos: $ARGS"
    OUTPUT=$($SCRIPT $ARGS 2>&1) # Executa o script e captura a saída
    EXIT_CODE=$? # Captura o código de saída

    # Verifica se o teste foi bem-sucedido
    if [ $EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}Teste bem-sucedido!${NC}"
        echo "Saída: $OUTPUT"
    else
        echo -e "${RED}Teste falhou!${NC}"
        echo "Saída: $OUTPUT"
    fi
    echo "-----------------------------"
done