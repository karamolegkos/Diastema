# Installing a Multinode Spark Cluster on Ubuntu
In this guide I will use two machines with the below IPs:
- Master node IP: \<master-ip>
- Worker node IP: \<worker-ip>

The above machines will be my Spark Cluster in the end of this guide. 

The root privileges will be used, but for better safety you should better off use a normal user instead.

## Get your installations
**The following must be done in both of the machines** (all your nodes, if you have more than 2).
```
sudo -i
sudo apt update && sudo apt upgrade -y
sudo apt install default-jdk scala git -y
apt install python3-pip
pip install pyspark
```
Below is an advised way of organising your directories for the installation.
```
## Make a folder to download
# -> downloads
# -> sparkjob (only in Master node)
```

## Install Spark v3+ with Hadoop v3.2+
Now we will install Spark on all of the machines. Download your preferred version of Spark from this link [[1]](https://github.com/karamolegkos/Diastema/blob/main/diastema/spark/multinode-spark-installation.md#references) using wget.
```
cd ~/downloads
wget https://dlcdn.apache.org/spark/spark-3.1.2/spark-3.1.2-bin-hadoop3.2.tgz
tar xfz spark-3.1.2-bin-hadoop3.2.tgz -C /usr/local/
cd /usr/local
ln -sT spark-3.1.2-bin-hadoop3.2 spark
```

## Add spark binaries in your path
Use the '.bashrc' script to update you binaries.
```
vi ~/.bashrc
```
Add the two lines bellow IN THE END of the file and then :wq out.
```
export SPARK_HOME=/usr/local/spark
export PATH=$PATH:$SPARK_HOME/bin
```

## Check if spark-submit is working - If yes then you can continue
If the spark-submit is working in all your machines then you can continue.
```
cd
spark-submit
```

## Set up cluster configurations
Now we will start configuring the cluster. The last command will open up the spark-env.sh.
```
cd /usr/local/spark-*/conf
cp spark-env.sh.template spark-env.sh
vi spark-env.sh
```
Add/Edit the field below.
```
SPARK_MASTER_HOST='<master-ip>'
```
Now wq: out.

Do the following **only in the Master node**, to start the Master.
```
cd /usr/local/spark-*/sbin
./start-master.sh
```
The last command will give you a file that you can 'cat' to see if the Master started successfully.

Do the following **only in the Worker nodes**. The commands below will join and start the Workers.
```
cd /usr/local/spark-*/sbin
./start-slave.sh spark://<master-ip>:7077
```
The last command will give you a file that you can 'chat' to see if each Worker started successfully.

Your cluster is now ready for use!

## Submit jobs
To submit jobs in a Cluster you will need to download and use the needed jars **IN ALL NODES**.

# References
- [1] https://downloads.apache.org/spark
- [2] https://www.tutorialkart.com/apache-spark/how-to-setup-an-apache-spark-cluster/
