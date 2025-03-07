#!/usr/bin/env bash

# User data is executed as root
echo "Start!" >>/home/ubuntu/status.txt

apt update -y
echo "update completed!" >>/home/ubuntu/status.txt

apt install -y git \
    gcc \
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

echo "packages installed!" >>/home/ubuntu/status.txt

# clone dos repositórios
git clone https://github.com/pyenv/pyenv.git /home/ubuntu/.pyenv
git clone https://github.com/Luiz-Loch/ic.git /home/ubuntu/ic
git clone https://github.com/chrischoy/DeepGlobalRegistration.git /home/ubuntu/DeepGlobalRegistration

cd /home/ubuntu/ic
git submodule init
git submodule update

echo "Repositories cloned!" >>/home/ubuntu/status.txt

# pyenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >>/home/ubuntu/.bashrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >>/home/ubuntu/.bashrc
echo 'eval "$(pyenv init -)"' >>/home/ubuntu/.bashrc

echo "pyenv echoes done!" >>/home/ubuntu/status.txt

#source /home/ubuntu/.bashrc

echo "source .bashrc done!" >>/home/ubuntu/status.txt
