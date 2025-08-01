#! /usr/bin/env fish

cd gpu-scheduler
docker build . --tag gpu-scheduler:latest;
kind load docker-image gpu-scheduler:latest --name gpu-cluster
cd ..

printf "Test custom scheduler\n"

kubectl delete -f gpu-scheduler-check.yaml

sleep 5

kubectl delete -f gpu-scheduler.yaml

sleep 5

kubectl apply -f gpu-scheduler.yaml

printf "Waiting for GPU scheduler to be ready...\n"
kubectl wait --for=condition=ready pod -l app=gpu-scheduler --timeout=60s

printf "Start GPU scheduler check\n"
kubectl apply -f gpu-scheduler-check.yaml

sleep 50

if test (kubectl get pods/gpu-scheduler-check-2 -o jsonpath='{.spec.nodeName}') = "node3"
    printf "pod-2 on node3\n"
else
    printf "pod-2 is not on node3\n"
    exit 1
end

if test (kubectl get pods/gpu-scheduler-check-3 -o jsonpath='{.spec.nodeName}') = "node4"
    printf "pod-3 on node4\n"
else
    printf "pod-3 is not on node4\n"
    exit 1
end

if test (kubectl get pods/gpu-scheduler-check-4 -o jsonpath='{.spec.nodeName}') = "node4"
    printf "pod-4 on node4\n"
else
    printf "pod-4 is not on node4\n"
    exit 1
end

set_color green
printf "Test passed successfully\n"
set_color normal
