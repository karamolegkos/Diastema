# Installing Singlenode Spark on Ubuntu

This guide will show the steps to install the Spark framework in your ubuntu OS. The root privileges will be used, but for better safety you should better of use a normal user instead.

## Make your updates
Run the following commands to update your machine.
```
sudo -i
sudo apt update && sudo apt upgrade -y
```

## Install java, Scala and Git
Java, Scala and Git are some good features to have with Spark.
```
#install JDK, Scala, Git
sudo apt install default-jdk scala git -y

# verify your versions
java -version; javac -version; scala -version; git --version
```
You should have an output like the one below.
```
# openjdk version "11.0.11" 2021-04-20
# OpenJDK Runtime Environment (build 11.0.11+9-Ubuntu-0ubuntu2.20.04)
# OpenJDK 64-Bit Server VM (build 11.0.11+9-Ubuntu-0ubuntu2.20.04, mixed mode, sharing)
# javac 11.0.11
# Scala code runner version 2.11.12 -- Copyright 2002-2017, LAMP/EPFL
# git version 2.25.1
```

## Download and Set Up Spark
Download your preferred version of Spark from this link [[1]](https://github.com/karamolegkos/Diastema/edit/main/diastema/spark/singlenode-spark-installation.md#References) using wget.
```
wget https://dlcdn.apache.org/spark/spark-3.2.0/spark-3.2.0-bin-hadoop3.2.tgz
```
Extract the saved archive using the tar command.
```
tar xvf spark-*
```
Move the unpacked directory to the opt/spark directory. After that your Spark will be to the path '/opt/spark'.
```
sudo mv spark-3.2.0-bin-hadoop3.2 /opt/spark
```

## Configure environment variables
Open your .profile script
```
vi ~/.profile
```
Scroll to the end of the file and add these lines IN THE END.
```
export SPARK_HOME=/opt/spark

export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin

export PYSPARK_PYTHON=/usr/bin/python3
```
When you finish adding the paths, load the .profile file in the command line by typing the command below.
```
source ~/.profile
```

## Test your Spark installation
To test your installation it is only needed to go to your home directory and check if the command 'spark-submit' is able to be used, like below.
```
cd
spark-submit
```

## Some useful commands

Start a Master (Spark web user at http://127.0.0.1:8080/).
```
cd 
start-master.sh
```

Start a Slave for a Master.
- Having <master> as the IP of the Spark Master node.
- Having <port> as the port of the Spark Master node (Usuaslly it is 7077 - in the documentation at least)
```
start-slave.sh spark://<master>:<port>
```

Get in the spark shell.
```
spark-shell
```

Quit from scala.
```
:q
```

Stop a master.
```
stop-master.sh
```

Stop a running worker process.
```
stop-slave.sh
```

# References
- [1] https://downloads.apache.org/spark
- [2] https://phoenixnap.com/kb/install-spark-on-ubuntu
