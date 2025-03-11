#!/usr/bin/env bash

# Definir a versão do Miniconda e o link de download
CONDA_VERSION="latest"
INSTALLER="Miniconda3-${CONDA_VERSION}-Linux-x86_64.sh"
INSTALL_PATH="$HOME/miniconda"
PYTHON_VERSION="3.10"
ENVIRONMENT_NAME="ic"

# Baixar o instalador
echo "Baixando Miniconda..."
wget -q https://repo.anaconda.com/miniconda/$INSTALLER -O $INSTALLER

# Tornar o instalador executável
chmod +x $INSTALLER

# Instalar de forma silenciosa (sem interação)
echo "Instalando Miniconda em $INSTALL_PATH..."
./$INSTALLER -b -p $INSTALL_PATH

# Remover o instalador após a instalação
rm $INSTALLER

# Adicionar Conda ao PATH
echo "Configurando ambiente Conda..."
echo "export PATH=\"$INSTALL_PATH/bin:\$PATH\"" >> ~/.bashrc
export PATH="$INSTALL_PATH/bin:$PATH"

# Testar a instalação
echo "Testando Conda..."
conda --version && echo "Miniconda instalado com sucesso!" || echo "Erro na instalação."

# Atualizar Conda
echo "Atualizando Conda..."
conda update -n base -c defaults conda -y

echo "Instalação finalizada!"

echo "Inicializando conda..."
conda init

echo "Criando ambiente ${ENVIRONMENT_NAME} com python ${PYTHON_VERSION}..."
conda create -n ${ENVIRONMENT_NAME} python=${PYTHON_VERSION} -y
echo "Ambiente criado com sucesso"

echo "Ativando ambiente '${ENVIRONMENT_NAME}'..."
conda activate ${ENVIRONMENT_NAME}

python --version
