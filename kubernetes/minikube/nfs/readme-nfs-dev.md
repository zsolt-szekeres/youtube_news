# Setting NFS server in docker environment
https://github.com/phcollignon/nfs-server-minikube/tree/main

```bash
modprobe nfs
modprobe nfsd
```

```bash
docker run -d --rm --privileged --name nfs-server  -v /var/nfs:/var/nfs phico/nfs-server:latest
```
NFS share is mounted with a volume in a /var/nfs directory on docker engine host machine

# Connect NFS server with minikube
```bash
$ docker ps
# check existence of running containers with name minikube and nfs-server
$ docker network connect minikube nfs-server
# test connection
$ docker inspect nfs-server
$ docker network inspect minikube
```

# Test mount using PVC and PV
```bash
git clone https://github.com/phcollignon/nfs-server-minikube.git
cd nfs-server-minikube/examples
kubectl apply -f busybox-nfs-pvc-pv.yaml
# busybox pod is running 
kubectl get pods
# test log.txt file written by busybox in nfs share from host machine
cat /var/nfs/exports/log.txt
```

## Delete resources
```bash
kubectl delete -f busybox-nfs-pvc-pv.yaml
```

```bash
kubectl delete deployment busybox
kubectl patch pvc nfs -p '{"metadata":{"finalizers":null}}'
kubectl delete pvc nfs
kubectl delete pv nfs
```

# NFS CSI driver
```bash
git clone https://github.com/phcollignon/nfs-server-minikube.git
cd nfs-server-minikube/csi-driver-nfs/deploy
# in csi-nfs-driverinfo.yaml change apiVersion from storage.k8s.io/v1beta to storage.k8s.io/v1
kubectl apply -f rbac-csi-nfs-controller.yaml
kubectl apply -f csi-nfs-driverinfo.yaml
kubectl apply -f csi-nfs-controller.yaml
kubectl apply -f csi-nfs-node.yaml

# delete driver
kubectl delete -f csi-nfs-node.yaml
kubectl delete -f csi-nfs-controller.yaml
kubectl delete -f csi-nfs-driverinfo.yaml
kubectl delete -f rbac-csi-nfs-controller.yaml
```

```bash
cd nfs-server-minikube/examples
```

# Test mount using NFS CSI driver, PVC and PV
```bash
cd nfs-server-minikube/examples
kubectl apply -f busybox-nfs-pvc-pv-csi.yaml
```
