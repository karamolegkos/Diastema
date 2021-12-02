# Using Spark jobs on a Kubernetes Cluster

This guide will show how to run a spark job on a kubernetes multinode cluster. Most of the examples that exist online, are actually in need of the reader to know about Google Clouds, AWS etc. In this guide there will more focus on how to run the job.
- Kubernetes Master Node will be hosted here: 192.168.222.14:6443

This guide is an extension of the official spark guide here [[1]](https://github.com/karamolegkos/Diastema/blob/main/diastema/spark-on-kubernetes/spark-on-kubernetes.md#references).

## Prerequisites
- A running Kubernetes Cluster [[2]](https://github.com/karamolegkos/Diastema/blob/main/diastema/spark-on-kubernetes/spark-on-kubernetes.md#references)
- A Docker image Registry (Dockerhub is ok also too)
- Spark installed to use as a client machine [[3]](https://github.com/karamolegkos/Diastema/blob/main/diastema/spark-on-kubernetes/spark-on-kubernetes.md#references). It only need to be able to see the Kubernetes Master Host and IP as well as be able to make calls to them.

## Make your spark job
To make the spark job, we need firstly, to have an image including the spark framework inside of it. As described here [[4]](https://github.com/karamolegkos/Diastema/blob/main/diastema/spark-on-kubernetes/spark-on-kubernetes.md#references), the 'docker-image-tool.sh' is able of building this image for us.

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

If you need to find where is your kubernetes host. Type in the Kubernetes Master host the following:
```
kubectl cluster-info
```

# References
- [1] https://spark.apache.org/docs/latest/running-on-kubernetes.html
- [2] https://github.com/karamolegkos/Diastema/blob/main/diastema/kubernetes-cluster/kubernetes-cluster-installation.md
- [3] https://github.com/karamolegkos/Diastema/blob/main/diastema/spark/singlenode-spark-installation.md
- [4] https://spark.apache.org/docs/latest/running-on-kubernetes.html#docker-images
