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

