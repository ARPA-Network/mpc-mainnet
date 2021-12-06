import boto3
import paramiko
import sys

def lambda_handler(event, context):
    local_private_key = 'PATH_TO_PRIVATE_KEY'
    s3_client = boto3.client('s3')
    s3_client.download_file('mpc-ssh-keys', 'PRIVATE_KEY.pem', local_private_key)
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    hostname = event['hostname']
    username = event['username']
    ssh_client.connect(hostname=hostname, username=username, key_filename=local_private_key)
    cmd = (
        "sudo apt update"
        " && sudo apt install --yes"
        " build-essential"
        " autoconf"
        " automake"
        " libtool"
        " pkg-config"
        " cmake"
        " clang-format"
        " libgflags-dev"
        " libgtest-dev"
        " python-dev"
        " git"
        " curl"
        " libboost-filesystem-dev"
        " python-gmpy2"
        " yasm"
        " libcrypto++-dev"
        " libcrypto++-doc"
        " libcrypto++-utils"
        " && cd"
        " && wget http://mpir.org/mpir-3.0.0.tar.bz2"
        " && tar -xvf mpir-3.0.0.tar.bz2"
        " && cd mpir-3.0.0"
        " && ./configure --enable-cxx"
        " && make"
        " && sudo make install"
        " && sudo ldconfig # refresh shared library cache"
        " && cd"
        " && wget https://www.openssl.org/source/openssl-1.1.1.tar.gz"
        " && tar -xvf openssl-1.1.1.tar.gz"
        " && cd openssl-1.1.1"
        " && ./config"
        " && make"
        " && sudo make install"
        " && sudo ldconfig # refresh shared library cache"
        " && cd"
        " && git clone https://github.com/KULeuven-COSIC/SCALE-MAMBA.git scale"
        " && cd scale"
        " && echo \"ROOT = $HOME/scale\" >> CONFIG.mine"
        " && echo \"OSSL = $HOME/openssl-1.1.1\" >> CONFIG.mine"
        " && echo \"FLAGS = -DMAX_MOD_SZ=7\" >> CONFIG.mine"
        " && echo \"OPT = -O3\" >> CONFIG.mine"
        " && echo \"LDFLAGS =\" >> CONFIG.mine"
        " && make"
        " && cp Auto-Test-Data/Cert-Store/* Cert-Store/"
        " && cp Auto-Test-Data/1/* Data/"
        " && Scripts/test.sh test_sqrt"
        " 2>&1 | tee --append ~/setupEnv.log > /dev/null 2>&1 &"
        )
    stdin, stdout, stderr = ssh_client.exec_command(cmd)
    print(stdout.readlines())
    print(stderr.readlines())
    return 0