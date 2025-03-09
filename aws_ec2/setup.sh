#!/usr/bin/env bash

# User data is executed as root
echo "Start!" >>~/status.txt

apt update -y
echo "update completed!" >>~/status.txt

apt install -y git \
    gcc build-essential \
    cmake \
    libreadline-dev \
    openssl libssl-dev \
    bzip2 libbz2-dev \
    sqlite3 libsqlite3-dev \
    libffi-dev liblzma-dev \
    libegl1 libgl1 \
    libeigen3-dev \
    libboost-all-dev \
    libopenblas-dev

echo "packages installed!" >>~/status.txt

# Pyenv
#curl https://pyenv.run | bash
#echo "pyenv echoes done!" >>~/status.txt

# clone dos repositórios
git clone --recursive https://github.com/Luiz-Loch/ic.git ~/ic

echo "Repositories cloned!" >>~/status.txt
