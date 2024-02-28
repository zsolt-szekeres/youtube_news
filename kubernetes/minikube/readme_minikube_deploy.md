# Start minikube
```bash
minikube start --driver docker --container-runtime docker --gpus all --memory no-limit --cpus no-limit
minikube addons enable nvidia-gpu-device-plugin
minikube addons enable nvidia-device-plugin
minikube addons enable metrics-server
minikube addons enable ingress
```
## Add ingress-dns 
https://minikube.sigs.k8s.io/docs/handbook/addons/ingress-dns/

The ingress-dns addon acts as a DNS service that runs inside your Kubernetes cluster. All you have to do is install the service and add the minikube ip as a DNS server on your host machine. Each time the DNS service is queried, an API call is made to the Kubernetes master service for a list of all the ingresses. If a match is found for the name, a response is given with an IP address matching minikube ip.

```bash
minikube addons enable ingress-dns
```

```bash
sudo nano /etc/NetworkManager/NetworkManager.conf
### add under [main] section the following line:
# dns=dnsmasq

echo "server=/test/$(minikube ip)" | sudo tee /etc/NetworkManager/dnsmasq.d/minikube.conf
systemctl restart NetworkManager.service

# test:
nslookup yt-news.minikube.local
# Server:		127.0.0.53
# Address:	127.0.0.53#53

# Name:	yt-news.minikube.local
# Address: 192.168.49.2
```

## Start minikube console in a new terminal
```bash
minikube dashboard
```

# Pushing images into a minikube without uploading docker image to a conainer registry
https://minikube.sigs.k8s.io/docs/handbook/pushing/#5-building-images-inside-of-minikube-using-ssh

```bash
# get environmental variables of docker engine running in minikube VM
$ minikube docker-env
export DOCKER_TLS_VERIFY="1"
export DOCKER_HOST="tcp://192.168.49.2:2376"
export DOCKER_CERT_PATH="/home/zoltanf/.minikube/certs"
export MINIKUBE_ACTIVE_DOCKERD="minikube"

# point your shell to minikube's docker-daemon, instead of the default docker-daemon of the host machine:
eval $(minikube -p minikube docker-env)
```
# Build image using docker in minikube VM

1. Git pull latest updates
```bash
git clone https://github.com/zsolt-szekeres/youtube_news.git \
    && cd youtube_news \
    && git checkout main
```
or
```bash
cd youtube_news \
    && git checkout main \
    && git pull
```

2. Build docker image
From youtube_news repository folder run:
```bash
docker build -t youtube_news_minikube:main . -f kubernetes/minikube/Dockerfile
```

# Deploy in minikube

## Briefly

1. Start NFS server
```bash
modprobe nfs
modprobe nfsd
docker run -d --rm --privileged --name nfs-server  -v /var/nfs:/var/nfs phico/nfs-server:latest
docker network connect minikube nfs-server
sudo mkdir /var/nfs/youtube_news/data
```

2. Add your api keys to secrets 
```bash
nano kubernetes/minikube/yt_news-deployment.yaml
```

API keys must be given in a base64 encoded format:
```bash
echo -n 'your_youtube_api_key' | base64
```

This is another way to get the base64 encoded secrets, if kubectl is installed
```bash
kubectl create secret generic yt-news-secret \
  --from-literal='youtube_api_key'='your_youtube_api_key' \
  --from-literal='openai_api_key'='your_openai_api_key' \
  --from-literal='gmail_twofactor'='your_gmail_twofactor_app_password' \
  --dry-run='client' \
  --output=yaml 
```

3. Deploy application
```bash
kubectl apply -f kubernetes/minikube/yt_news-deployment.yaml
```

# Useful kubectl commands for tests
```bash
# check state of pod (running, crashed, etc)
kubectl -n yt-news get pods
# Note: <...> refers to a unique character code series in the pod name
kubectl -n yt-news describe pod youtube-news-deployment-<...>

# watch streamlit web page on local host
kubectl port-forward pod/youtube-news-deployment-<...> 8501 -n yt-news

# re-build and re-deploy
kubectl delete -f yt_news-deployment.yaml
docker build -t youtube_news_minikube:main .
kubectl apply -f yt_news-deployment.yaml 

# open a bash terminal on pod
kubectl -n yt-news exec -it youtube-news-deployment-<...> -- /bin/bash

# watch logs of application, if started at entrypoint 
kubectl -n yt-news logs youtube-news -f
```

# Stop minikube
```bash
minikube stop
```

# Purge munikube settings
```bash
minikube delete
```

# Persistent volumes of type ReadWriteMany (additional info)

In order to persist the output files of the containerized application, we need a volume mount in the container.

## HostPath mount
The simplest option is to make a host path mount, i.e. select/create a folder on the minikube VM and mount it in the container.
In this case we also may want to persist minikube VM's folder, hence we mount a local host folder in minikube VM, and we will mount that folder in the container.

Mounting host path /volumes/youtube-news/data into minikube VM as /volumes/youtube-news/data
```bash
sudo mkdir /volumes
sudo chown -R <user>:<group> volumes
mkdir -p /volumes/youtube-news/data
minikube mount /volumes/youtube-news/data:/volumes/youtube-news/data &
```

To use this volume, the deployment file of the application should contain the followings:
```bash
...
  template:
    metadata:
      labels:
        app: youtube-news
    spec:
      containers:
      - name: youtube-news
...
        volumeMounts:
        - mountPath: /data
          name: localVolume
      volumes:
      - name: localvolume
        hostPath:
          path: /volumes/youtube-news/data
          type: DirectoryOrCreate
...
```

## NFS mount

Later we might require that multiple pods read from and write to the same persistent volume.
One way to achieve this is mounting an NFS share.

1. Create NFS server

Here we create a test NFS server as described in ./nfs/readme-nfs-dev.md

Run run the following commands in a new terminal (where we have NOT executed `eval $(minikube -p minikube docker-env)` yet).

```bash
modprobe nfs
modprobe nfsd
docker run -d --rm --privileged --name nfs-server  -v /var/nfs:/var/nfs phico/nfs-server:latest
docker network connect minikube nfs-server
```
The NFS share can be found at /var/nfs/ on the host machine. The docker container name and host name is nfs-server.

2. Create persistent volume, persistent volume claim

Let the persistent Volume point to `nfs-server:/youtube-news/data`

On host machine run
```bash
sudo mkdir /var/nfs/youtube_news/data
```

Definition of Persistent Volume (PV) and Persistent Volume Claim (PVC)

```bash
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: nfs
  namespace: yt-news
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: ""
  resources:
    requests:
      storage: 500Mi
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: nfs
  namespace: yt-news
spec:
  capacity:
    storage: 500Mi
  accessModes:
    - ReadWriteMany
  nfs:
    server: nfs-server
    path: /youtube-news/data
```

3. Mount NFS volume in the container using the PVC

```bash
apiVersion: apps/v1
kind: Deployment
metadata:
  name: youtube-news-deployment
  namespace: yt-news
spec:
  replicas: 1
  selector:
    matchLabels:
      app: youtube-news
  template:
    metadata:
      labels:
        app: youtube-news
    spec:
      containers:
      - name: youtube-news
...
        volumeMounts:
        - mountPath: /data
          name: nfs
      volumes:
      - name: nfs
        persistentVolumeClaim:
          claimName: nfs
...
```
