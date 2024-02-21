# References

1. https://learn.microsoft.com/hu-hu/visualstudio/docker/tutorials/docker-tutorial 
2. https://code.visualstudio.com/docs/containers/overview
3. https://linux.how2shout.com/2-ways-to-install-docker-engine-on-linux-mint/
4. https://www.knowledgehut.com/blog/devops/docker-vs-containerd
5. https://hub.docker.com/r/nvidia/cuda

# Environment

## Install Docker Engine

```bash
$ sudo apt install docker docker-compose docker-doc docker-registry docker.io
The following NEW packages will be installed:
  bridge-utils containerd docker docker-compose docker-doc docker-registry docker.io pigz python3-attr python3-docker python3-dockerpty python3-docopt
  python3-dotenv python3-jsonschema python3-pyrsistent python3-setuptools python3-texttable python3-websocket runc ubuntu-fan wmdocker
$ sudo usermod -aG docker zoltanf
$ sudo reboot
$ docker --version
Docker version 24.0.5, build 24.0.5-0ubuntu1~22.04.1
```

```bash
# list available docker contexts (default is Docker Engine
# NOTE: Docker Desktop is a VM, not installed, it would be called desktop-linux
$ docker context ls
NAME        DESCRIPTION                               DOCKER ENDPOINT               ERROR
default *   Current DOCKER_HOST based configuration   unix:///var/run/docker.sock

# if multiple contexts are available, switch to Docker Engine context:
$  docker context use default

# Stop and Start docker engine
$ sudo systemctl stop docker docker.socket containerd
$ sudo systemctl start docker docker.socket containerd

# Status
$ sudo systemctl status docker
```

## Installing the NVIDIA Container Toolkit
https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html

The NVIDIA Container Toolkit enables users to build and run GPU-accelerated containers. The toolkit includes a container runtime library and utilities to automatically configure containers to leverage NVIDIA GPUs.

![NVIDIA Container Toolkit](https://cloud.githubusercontent.com/assets/3028125/12213714/5b208976-b632-11e5-8406-38d379ec46aa.png)

```bash
$ curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
$ sudo apt-get update
$ sudo apt-get install -y nvidia-container-toolkit
The following NEW packages will be installed:
  libnvidia-container-tools libnvidia-container1 nvidia-container-toolkit nvidia-container-toolkit-base
```
Configuring Docker Engine to use nvidia-container-runtime 

(NOTE: rootless mode should be used in production environment,
see https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#rootless-mode)
```bash
$ sudo nvidia-ctk runtime configure --runtime=docker
$ cat /etc/docker/daemon.json 
{
    "runtimes": {
        "nvidia": {
            "args": [],
            "path": "nvidia-container-runtime"
        }
    }
}
$ sudo systemctl restart docker docker.socket containerd
```

Test: run a sample CUDA container
```bash
$ sudo docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi
Unable to find image 'ubuntu:latest' locally
latest: Pulling from library/ubuntu
01007420e9b0: Pull complete 
Digest: sha256:f9d633ff6640178c2d0525017174a688e2c1aef28f0a0130b26bd5554491f0da
Status: Downloaded newer image for ubuntu:latest
Wed Feb 21 16:04:26 2024       
+---------------------------------------------------------------------------------------+
| NVIDIA-SMI 545.29.06              Driver Version: 545.29.06    CUDA Version: 12.3     |
|-----------------------------------------+----------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |         Memory-Usage | GPU-Util  Compute M. |
|                                         |                      |               MIG M. |
|=========================================+======================+======================|
|   0  NVIDIA GeForce RTX 4060 ...    Off | 00000000:01:00.0 Off |                  N/A |
| N/A   34C    P3               8W /  35W |      9MiB /  8188MiB |      0%      Default |
|                                         |                      |                  N/A |
+-----------------------------------------+----------------------+----------------------+
                                                                                         
+---------------------------------------------------------------------------------------+
| Processes:                                                                            |
|  GPU   GI   CI        PID   Type   Process name                            GPU Memory |
|        ID   ID                                                             Usage      |
|=======================================================================================|
+---------------------------------------------------------------------------------------+
```

## Build image
```bash
$ cd dockerize
$ docker build \
  --build-arg YOUTUBE_API_KEY=${YOUTUBE_API_KEY} \
  --build-arg OPENAI_API_KEY=${OPENAI_API_KEY} \
  --build-arg GMAIL_TWOFACTOR=${GMAIL_TWOFACTOR} \
  --build-arg STREAMLIT_PORT=8884 \
  -t youtube_news:main \
  .
```
TODO: docker image inspect contains the API keys. Sensitive info should not be stored in dockerimage. Neither passed as -e argument of docker run.

## Run image in local environment
```bash
$ docker run --rm --gpus all --runtime=nvidia -e STREAMLIT_PORT=8501 -p 8501:8501 youtube_news:main streamlit run main.py --server.port 8501
```

TODO: 
 * configure config.json during build or runtime.
 * save files to S3 or GFS.

