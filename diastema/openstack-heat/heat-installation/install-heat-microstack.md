# Install Heat Service in MicroStack - OpenStack

This .md file is made in a time that Heat is not one of the version services that are implemented in the MicroStack version of OpenStack [1]. This is also a on the wishlist for the MicroStack project, but it is not yet in on-progress phase.

This .md file will show how to install the Heat Services in the MicroStack project. This guide is for the ubuntu OS. To install MicroStack use the guide here [2]

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
# insert your password
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


# Documentation used
[]

# References

- [1] https://ubuntu.com/openstack/install
- [2] https://ubuntu.com/openstack/install
- [] https://docs.openstack.org/heat/wallaby/install/install-ubuntu.html
