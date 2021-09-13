# Install Heat Service in MicroStack - OpenStack

This .md file is made in a time that Heat is not one of the services that are implemented in the MicroStack version of OpenStack [[1]](https://github.com/karamolegkos/Diastema/blob/main/diastema/openstack-heat/heat-installation/install-heat-microstack.md#references). This is also a on the wishlist for the MicroStack project, but it is not yet in on-progress phase [[2]](https://github.com/karamolegkos/Diastema/blob/main/diastema/openstack-heat/heat-installation/install-heat-microstack.md#references).

This .md file will show how to install the Heat Services in the MicroStack project. This guide is for the ubuntu OS. To install MicroStack use the guide here [[1]](https://github.com/karamolegkos/Diastema/blob/main/diastema/openstack-heat/heat-installation/install-heat-microstack.md#references).

# Log in your MicroStack MySQL DB 
Go to the MySQL database made by your MicroStack project

First install mysql client to be able to use the '**mysql**' command:
```
sudo apt install mysql-client-core-8.0
```
MicroStack MySQL DB socket is located below:
```
/var/snap/microstack/common/run/mysql/mysqld.sock
```
Run the following commands to get your MicroStack MySQL DB password and log in the MySQL Server:
```
sudo snap get microstack config.credentials.mysql-root-password
sudo mysql -u root -p -S /var/snap/microstack/common/run/mysql/mysqld.sock
# insert the MySQL root password
```
In MySQL input the following commands:
```
# 'pAassw0rd' is a password!!!
GRANT ALL PRIVILEGES ON heat.* TO 'heat'@'localhost' IDENTIFIED BY 'pAassw0rd';
GRANT ALL PRIVILEGES ON heat.* TO 'heat'@'%' IDENTIFIED BY 'pAassw0rd';

# If the above commands are giving an error, then and only then, run the following:
# CREATE USER 'heat'@'localhost' IDENTIFIED BY 'pAassw0rd';
# GRANT ALL PRIVILEGES ON heat.* TO 'heat'@'localhost';
# CREATE USER 'heat'@'%' IDENTIFIED BY 'pAassw0rd';
# GRANT ALL PRIVILEGES ON heat.* TO 'heat'@'%';
```
For simplicity, whenever we want a password, we will use '**pAassw0rd**' as the password.

# Configure OpenStack
- Tip: the following code will make '**microstack.openstack**' just an '**openstack**' command:
```
sudo snap alias microstack.openstack openstack
```
Make the below configurations in your OpenStack environment:
```
# make heat user as an admin
openstack user create --domain default --password-prompt heat
openstack role add --project service --user heat admin

# Name the sevices
openstack service create --name heat --description "Orchestration" orchestration
openstack service create --name heat-cfn --description "Orchestration"  cloudformation

# Make the endpoints of the ochestration (Use your own ip in the <ip> field)
# example
# openstack endpoint create --region microstack orchestration public http://83.60.200.4:8004/v1/%\(tenant_id\)s
openstack endpoint create --region microstack orchestration public http://<ip>:8004/v1/%\(tenant_id\)s
openstack endpoint create --region microstack orchestration internal http://<ip>:8004/v1/%\(tenant_id\)s
openstack endpoint create --region microstack orchestration admin http://<ip>:8004/v1/%\(tenant_id\)s

# Make cloudformation endpoints (Use your own ip in the <ip> field)
openstack endpoint create --region microstack cloudformation public http://<ip>:8000/v1
openstack endpoint create --region microstack cloudformation internal http://<ip>:8000/v1
openstack endpoint create --region microstack cloudformation admin http://<ip>:8000/v1

# Heat domain
# If there is an error with the description flag then just do not use a description
openstack domain create --description "Stack projects and users" heat
# openstack domain create heat

# User to manage projects and users in the heat domain (password: 'pAassw0rd')
openstack user create --domain heat --password-prompt heat_domain_admin
openstack role add --domain heat --user-domain heat --user heat_domain_admin admin

# Make 'admin' user, a heat_stack_owner in the 'admin' project
openstack role create heat_stack_owner
openstack role add --project admin --user admin heat_stack_owner
## You must add the heat_stack_owner role to each user that manages stacks.

openstack role create heat_stack_user
```
Now use root privileges to install Heat to your machine:
```
sudo -i
apt-get install heat-api heat-api-cfn heat-engine
```

# Configure the heat.conf file

Configure the heat.conf file:
```
sudo vi /etc/heat/heat.conf
```
In this file everything is commented out. 
```
# Do not forget that:
# pAassw0rd is a password
# <ip> is your own ip
```
You can just add the following lines:
```
[DEFAULT]

heat_metadata_server_url = http://<ip>:8000
heat_waitcondition_server_url = http://<ip>:8000/v1/waitcondition

stack_domain_admin = heat_domain_admin
stack_domain_admin_password = pAassw0rd
stack_user_domain_name = heat

[database]

connection = mysql+pymysql://heat:pAassw0rd@<ip>/heat

[keystone_authtoken]

www_authenticate_uri = http://<ip>:5000/v3/
auth_url = http://<ip>:5000/v3/
memcached_servers = <ip>:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = heat
password = pAassw0rd

[trustee]

auth_type = password
auth_url = http://<ip>:5000/v3/
username = heat
password = pAassw0rd
user_domain_name = default

[clients_keystone]

auth_uri = http://<ip>:5000/v3/
```

# Populate rchestration DB
Make sure you are still using root privileges and do the following:
```
su -s /bin/sh -c "heat-manage db_sync" heat
```

# Finalize your installation
Make sure you are still using root privileges and do the following:
```
service heat-api restart
service heat-api-cfn restart
service heat-engine restart

systemctl enable heat-api
systemctl enable heat-api-cfn
systemctl enable heat-engine
```

# Last steps
Get your keystone password:
```
sudo snap get microstack config.credentials.keystone-password
# For this guide lets assume that the password is KeYst0ne
```
Go to a directory that you like and then make a file named '**admin-openrc**':
```
sudo vi admin-openrc
```
```
# Remember that:
# KeYst0ne is the keystone password
# <ip> is your own ip
```
Insert the following lines and save your file:
```
export OS_PROJECT_DOMAIN_NAME=Default
export OS_USER_DOMAIN_NAME=Default
export OS_PROJECT_NAME=admin
export OS_USERNAME=admin
export OS_PASSWORD=KeYst0ne
export OS_AUTH_URL=http://<ip>:5000/v3/
```
After the above you should reboot your machine.

# After the reboot
Now every time that you want to run any openstack commands, you have to run first the following command in the directory that you put the admin-openrc file:
```
. admin-openrc
```
After that, you can use heat commands like:
```
openstack stack list
#It is ok if does not output nothing while not having any stacks
```

# Documentation used
[[3]](https://github.com/karamolegkos/Diastema/blob/main/diastema/openstack-heat/heat-installation/install-heat-microstack.md#references)

# References

- [1] https://ubuntu.com/openstack/install
- [2] https://bugs.launchpad.net/microstack/+bug/1812416
- [3] https://docs.openstack.org/heat/wallaby/install/install-ubuntu.html
