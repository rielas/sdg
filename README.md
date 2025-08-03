# Demo

[![asciicast](https://asciinema.org/a/69k0HEm9akIH4hIKipQHHmdrQ.svg)](https://asciinema.org/a/69k0HEm9akIH4hIKipQHHmdrQ)

# Technical Task

Write a Kubernetes scheduler named gpu-scheduler in Python or Go that will place pods and sets environment variable `CUDA_VISIBLE_DEVICES` according to the annotation:

```yaml
gpu-scheduling-map: |
  0=node1:0,1
  1=node2:2
  2=node3:0,1,2
  3=node4:3
  4=node4:3
```

0=node1:0,1:
0 is the pod index, node1 is the node name, 0,1 is the value for the environment variable `CUDA_VISIBLE_DEVICES`.
1=node2:2:
1 is the pod index, node2 is the node name, 0,1 is the value for the environment variable `CUDA_VISIBLE_DEVICES`.
etc.
The result of the task should be a repository at gitlab.com containing:

1. The GPU scheduler code
2. A Dockerfile for the gpu-scheduler
3. A Dockerfile for a test service called gpu-scheduler-check, which will use the gpu-scheduler. Upon startup, the service should log the node name and the value of the `CUDA_VISIBLE_DEVICES` environment variable in an infinite loop.
Next, you need to create a Kubernetes cluster (KinD, microk8s, etc.) with 1 master and 4 nodes named node1, ..., node4 and install the gpu-scheduler and gpu-scheduler-check
Include in the repository the output of the command `kubectl get pod -owide -A` and the logs of pods located on node3 and node4."

# How to deploy Kind cluster

```sh
kind create cluster --name gpu-cluster --config kind-config.yaml
```

# Deployment of the required services

It's required then to deploy two services:
1. GPU scheduler. Which places pods on nodes according to the annotation `gpu-scheduling-map`.
2. Admission webhook service. Which will intercept pod creation requests and add the `CUDA_VISIBLE_DEVICES` environment variable to the pod spec based on the annotation `gpu-scheduling-map`.

Create a secret with TLS certificate and key for the admission webhook service:

```sh
openssl x509 -req -in server.csr -CA ca-cert.pem -CAkey ca-key.pem -CAcrea
teserial -out server-cert.pem -days 365 -extensions v3_req -extfile webhook-
csr.conf
kubectl create secret tls cuda-env-webhook-tls --cert=server-cert.pem --ke
y=server-key.pem -n kube-system
```

Update the `webhook.yaml` file with the correct CA bundle from the secret.

Build and load Docker images into the Kind cluster:

```sh
cd gpu-scheduler
docker build . --tag gpu-scheduler:latest;
kind load docker-image gpu-scheduler:latest --name gpu-cluster
docker build --file Dockerfile.webhook . --tag cuda-webhook:latest
kind load docker-image cuda-webhook:latest --name gpu-cluster
```

Deploy admission webhook service:

```sh
kubectl apply -f webhook.yaml
kubectl apply -f webhook-service.yaml
```

Deploy GPU scheduler:

```sh
kubectl apply -f gpu-scheduler.yaml
```

# Test the deployment

Deploy a stateful set to be placed by the GPU scheduler:

```sh
kubectl apply -f gpu-scheduler-check.yaml
```

Run the test script to check the deployment:

```sh
./test_script.fish
```

Final configuration should look like this:

```sh
~ kubectl get pod -owide -A                                                                                                                                                          (main ✔) 18:28
NAMESPACE            NAME                                                READY   STATUS    RESTARTS          AGE   IP            NODE                        NOMINATED NODE   READINESS GATES
default              gpu-scheduler-check-0                               1/1     Running   0                 21m   10.244.3.11   node1                       <none>           <none>
default              gpu-scheduler-check-1                               1/1     Running   0                 21m   10.244.1.14   node2                       <none>           <none>
default              gpu-scheduler-check-2                               1/1     Running   0                 21m   10.244.4.19   node3                       <none>           <none>
default              gpu-scheduler-check-3                               1/1     Running   0                 21m   10.244.2.32   node4                       <none>           <none>
default              gpu-scheduler-check-4                               1/1     Running   0                 21m   10.244.2.33   node4                       <none>           <none>
kube-system          coredns-674b8bbfcf-b6k69                            1/1     Running   0                 19h   10.244.0.6    gpu-cluster-control-plane   <none>           <none>
kube-system          coredns-674b8bbfcf-strxz                            1/1     Running   0                 19h   10.244.0.4    gpu-cluster-control-plane   <none>           <none>
kube-system          cuda-env-webhook-75897fb444-l5kn5                   1/1     Running   0                 18m   10.244.1.15   node2                       <none>           <none>
kube-system          etcd-gpu-cluster-control-plane                      1/1     Running   0                 19h   172.18.0.6    gpu-cluster-control-plane   <none>           <none>
kube-system          gpu-scheduler-554f8d45c7-76v4c                      1/1     Running   0                 18m   10.244.3.12   node1                       <none>           <none>
kube-system          kindnet-2647b                                       1/1     Running   0                 19h   172.18.0.5    node4                       <none>           <none>
kube-system          kindnet-k5rkj                                       1/1     Running   0                 19h   172.18.0.2    node1                       <none>           <none>
kube-system          kindnet-rhwxb                                       1/1     Running   0                 19h   172.18.0.3    node2                       <none>           <none>
kube-system          kindnet-rlrt4                                       1/1     Running   0                 19h   172.18.0.6    gpu-cluster-control-plane   <none>           <none>
kube-system          kindnet-w7jlb                                       1/1     Running   0                 38m   172.18.0.4    node3                       <none>           <none>
kube-system          kube-apiserver-gpu-cluster-control-plane            1/1     Running   0                 19h   172.18.0.6    gpu-cluster-control-plane   <none>           <none>
kube-system          kube-controller-manager-gpu-cluster-control-plane   1/1     Running   0                 19h   172.18.0.6    gpu-cluster-control-plane   <none>           <none>
kube-system          kube-proxy-659xq                                    1/1     Running   0                 19h   172.18.0.5    node4                       <none>           <none>
kube-system          kube-proxy-djhns                                    1/1     Running   0                 19h   172.18.0.2    node1                       <none>           <none>
kube-system          kube-proxy-kzz5p                                    0/1     Error     133 (5m13s ago)   19h   172.18.0.3    node2                       <none>           <none>
kube-system          kube-proxy-tl8n6                                    1/1     Running   0                 19h   172.18.0.6    gpu-cluster-control-plane   <none>           <none>
kube-system          kube-proxy-vv7nv                                    1/1     Running   0                 19h   172.18.0.4    node3                       <none>           <none>
kube-system          kube-scheduler-gpu-cluster-control-plane            1/1     Running   0                 19h   172.18.0.6    gpu-cluster-control-plane   <none>           <none>
local-path-storage   local-path-provisioner-7dc846544d-d4rwq             1/1     Running   0                 19h   10.244.0.5    gpu-cluster-control-plane   <none>           <none>
```

Logs on check pods:

```sh
~ kubectl logs gpu-scheduler-check-2
...
Node Name: node3
CUDA_VISIBLE_DEVICES: 0,1,2
---

~ kubectl logs gpu-scheduler-check-3
...
Node Name: node4
CUDA_VISIBLE_DEVICES: 3
---

~ kubectl logs gpu-scheduler-check-4
...
Node Name: node4
CUDA_VISIBLE_DEVICES: 3
```
