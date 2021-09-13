# Examples on using the Kubernetes API Server
This guide will analyze how to contact with the Kubernetes APIs [[1]](https://github.com/karamolegkos/Diastema/blob/main/diastema/kubernetes-apis/use-k8s-apis.md#references).

I made this guide using two different machines. A test machine (The '**Alpha**' machine) and a machine having the kubernetes Master Node inside of it (The '**Beta**' machine).

The example below will be using the curl command to access the Kubernetes API Server.

# Get the Kubernetes API Server Credentials
To get the credentials for your Kubernetes API Server, get in the '**Beta**' machine and run the following commands:
```
APISERVER=$(kubectl config view --minify | grep server | cut -f 2- -d ":" | tr -d " ")
SECRET_NAME=$(kubectl get secrets | grep ^default | cut -f1 -d ' ')
TOKEN=$(kubectl describe secret $SECRET_NAME | grep -E '^token' | cut -f2 -d':' | tr -d " ")
```
Then **echo** the APISERVER and TOKEN variables:
```
echo $APISERVER
echo $TOKEN
```
The variables above need to be used as:
- APISERVER: Kubernetes API Server host
- TOKEN: Secret Token to authenticate for your cluster

You must copy or save the **echo**-ed values to make your calls.

# Contact the Kubernetes API
Lets assume that the values of the two needed variables are the ones below:
```
APISERVER is <ip>
TOKEN is t0ken
```
To use these values, go to the '**Alpha**' machine and type the commands below:
```
TOKEN="t0ken"
APISERVER="<ip>"
```
Then, make your curl request:
```
curl $APISERVER/api --header "Authorization: Bearer $TOKEN" --insecure
```

You can make calls from your applications, contaction the '**$APISERVER/api**' URL including the header '**Authorization**' with the value '**Bearer $TOKEN**'.

Here [[2]](https://github.com/karamolegkos/Diastema/blob/main/diastema/kubernetes-apis/use-k8s-apis.md#references) is a good github repository for examples in python code

# References

- [1] https://kubernetes.io/docs/tasks/access-application-cluster/access-cluster/
- [2] https://github.com/kubernetes-client/python/blob/master/examples/remote_cluster.py
