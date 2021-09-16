# Guide on how to install a Kubernetes Cluster
This guide will show how to install a K8S cluster, with a Master node and a Worker node.

# The Cluster
The cluster described will be the one below:
```
Ubuntu Master with the IP : <ip-1>
Ubuntu Worker with the IP : <ip-2>
```
The two machines have at least the below requirements:
Master:
- RAM: 2G
- CPU 2

Worker:
- RAM 1G
- CPU: 1

# How to install

- In both Master and Worker nodes:

Make the latests updates:
```
sudo apt update && sudo apt upgrade -y
```
Log in both machines as root user:
```
sudo -i
```
Make the right firewalls:
```
ufw disable
swapoff -a; sed -i '/swap/d' /etc/fstab
```
Take the lines below and use them ass one command
```
cat >>/etc/sysctl.d/kubernetes.conf<<EOF
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
EOF
```
Modify kernel parameters at runtime:
```
sysctl --system
```
Install docker:
```
apt install -y apt-transport-https ca-certificates curl gnupg-agent software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
apt update
apt install -y docker-ce=5:19.03.10~3-0~ubuntu-focal containerd.io
```
Setup Kubernetes:
```
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" > /etc/apt/sources.list.d/kubernetes.list

apt update && apt install -y kubeadm=1.18.5-00 kubelet=1.18.5-00 kubectl=1.18.5-00
```

- Now use only the Master:

Setup K8S API Server (Remember to change the IP with your Master's IP):
```
kubeadm init --apiserver-advertise-address=<ip-1> --pod-network-cidr=192.168.0.0/16  --ignore-preflight-errors=all
  
kubectl --kubeconfig=/etc/kubernetes/admin.conf create -f https://docs.projectcalico.org/v3.14/manifests/calico.yaml
```

Create a Token for your Kubernetes Cluster

This command will give you a command to use at your Worker nodes, to make them join your cluster:
```
kubeadm token create --print-join-command
```

- At your Workers:

Use the command given by the last Master's command to your Workers.

- Back to your Master again:

Set your Kubernetes's admin.conf file:
```
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

Your K8S cluster is now ready!

# Useful Commands!
```
kubectl get nodes

kubectl get cs
```

# Deploy a test project to your cluster
```
# deploy an nginx project
kubectl create deploy nginx --image nginx
# deployment.apps/nginx created is what you are waiting for

kubectl get all
# This will give you the container status: Creating, created, η running

kubectl expose deploy nginx --port 80 --type NodePort
# expose nginx

kubectl get svc
```
