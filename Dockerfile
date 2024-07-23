# Imagem oficial do Python como base
FROM python:3.11.9

# scipy pode ser utilizado pelo TEASER++
RUN pip install scipy tqdm boto3

# Instalação das dependências do Open3D
RUN apt-get update && apt-get install --no-install-recommends -y \
    libegl1 \
    libgl1 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Instalação do Open3D a partir do repositório do PyPI
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir --upgrade open3d

# Instalação do cmake e pacotes de desenvolvimento necessários para TEASER++
RUN apt-get update && apt-get install -y \
    g++ \
    cmake \
    libeigen3-dev \
    libboost-all-dev

# Definição do diretório de trabalho como /app
WORKDIR /app

# Cópia dos arquivos do diretório atual para /app no container
COPY . .

# Instalação das dependências do Python
RUN python3 -m pip install -r requirements.txt

# Execução dos comandos necessários para compilar o TEASER++ e adicionar ao Python
WORKDIR /app/TEASER-plusplus
RUN mkdir build && cd build && cmake .. && make
RUN cd build && cmake -DTEASERPP_PYTHON_VERSION=3.11.9 .. && make teaserpp_python && cd python && pip install .

# Retorna para o diretório /app
WORKDIR /app

# Comando para executar o benchmark
#CMD ["python", "main.py"]