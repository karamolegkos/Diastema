# Using Spark jobs on a Kubernetes Cluster

This guide will show how to run a spark job on a kubernetes multinode cluster. Most of the examples that exist online, are actually in need of the reader to know about Google Clouds, AWS etc. This guide will focus more on how to run the job.
- Kubernetes Master Node will be hosted here: 192.168.222.14:6443

This guide is an extension of the official spark guide here [[1]](https://github.com/karamolegkos/Diastema/blob/main/diastema/spark-on-kubernetes/spark-on-kubernetes.md#references).

## Prerequisites
- Spark installed to use as a client machine [[2]](https://github.com/karamolegkos/Diastema/blob/main/diastema/spark-on-kubernetes/spark-on-kubernetes.md#references). It only need to be able to see the Kubernetes Master Host and IP as well as be able to make calls to them.

## K8s Multinode in Minikube VM installation
The machine that you will be using must have a good amount of RAM.

First of all update your system:
```
sudo apt update && sudo apt upgrade -y
```

### Docker Installation
Install Docker [[4]](https://github.com/karamolegkos/Diastema/blob/main/diastema/spark-on-kubernetes/spark-on-kubernetes.md#references):
```
sudo apt-get install \
ca-certificates \
curl \
gnupg \
lsb-release

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
"deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
$(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
```
Then test your Docker installation:
```
sudo docker run hello-world
```
The above command should build a docker container saying Hello from Docker to the user.

Run the following command to make Docker accesible to all users. This is needed for the Minikube system to be able to access your Docker later.
```
sudo chmod 666 /var/run/docker.sock
```

### Install Minikube
Run the following to download Minikube [[5]](https://github.com/karamolegkos/Diastema/blob/main/diastema/spark-on-kubernetes/spark-on-kubernetes.md#references):
```
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```
Then to start your cluster.

To start a default cluster you can run the following:
```
minikube start
```
But you can also make a lot of configurations in the above command like the ones below. A good documentation on all the configurations that you are able to do, can be found here [[6]](https://github.com/karamolegkos/Diastema/blob/main/diastema/spark-on-kubernetes/spark-on-kubernetes.md#references)
```
minikube start --cpus "3" --disk-size "48g" --memory "12g" --nodes 3
```
If you want to be able to use the kubectl command you only need to run the following alias command:
```
alias kubectl="minikube kubectl --"
```

### Spark Role Configuration
To be able to use spark jobs inside of your cluster. You have to run the following configurations in your Minikube cluster to configure your RBAC:
```
kubectl create serviceaccount spark
kubectl create clusterrolebinding spark-role --clusterrole=edit --serviceaccount=default:spark --namespace=default
```

## Make your spark job
To make the spark job, we need firstly, to have an image including the spark framework inside of it. As described here [[3]](https://github.com/karamolegkos/Diastema/blob/main/diastema/spark-on-kubernetes/spark-on-kubernetes.md#references), the 'docker-image-tool.sh' is able of building this image for us.

After we have this image, we need to make our own image extending the image of the docker-image-tool.sh script.

We should put out dependencies and all of our needed source code inside of that image. Inside the Kubernetes cluster, the pods are actually going to rebuild this image many times and actually run the source code inside of the container.

## How to run
Let's say that your image is in the registry 'docker.io/sonem/my-spark-job:v1.0.0' and that inside of this image, your source code is in the directory '/app/app.py'. Then we should do the following submit through the Spark API or the Spark CLI.
```
spark-submit \
--master k8s://https://192.168.222.14:6443 \
--deploy-mode cluster \
--name spark-pi \
--conf spark.app.name=sparkpi \
--conf spark.kubernetes.container.image=docker.io/sonem/my-spark-job:v1.0.0 \
local:///app/app.py
``` 
An example that I like using is the following:
```
spark-submit \
--master k8s://https://192.168.49.2:8443 \
--deploy-mode cluster \
--name test-job-step1 \
--conf spark.executorEnv.MINIO_HOST="10.20.20.191" \
--conf spark.executorEnv.MINIO_PORT="9000" \
--conf spark.executorEnv.MINIO_USER="diastema" \
--conf spark.executorEnv.MINIO_PASS="diastema" \
--conf spark.app.name=test-job-step1 \
--conf spark.kubernetes.authenticate.driver.serviceAccountName=spark \
--conf spark.kubernetes.container.image=docker.io/konvoulgaris/diastema-daas-analytics-catalogue:latest \
local:///app/classification/decision_tree.py \
panos/analysis-1/dataset-1 \
panos/analysis-1/dataset-sparked \
quality
```

If you need to find where is your kubernetes host. Type in the Kubernetes Master host the following:
```
kubectl cluster-info
```

# References
- [1] https://spark.apache.org/docs/latest/running-on-kubernetes.html
- [2] https://github.com/karamolegkos/Diastema/blob/main/diastema/spark/singlenode-spark-installation.md
- [3] https://spark.apache.org/docs/latest/running-on-kubernetes.html#docker-images
- [4] https://docs.docker.com/engine/install/ubuntu/
- [5] https://minikube.sigs.k8s.io/docs/start/
- [6] https://minikube.sigs.k8s.io/docs/commands/start/
