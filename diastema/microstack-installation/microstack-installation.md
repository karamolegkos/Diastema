# Install MicroStack - OpenStack on Ubuntu
MicroStack is OpenStack in a Snap made by Canonical and RedHat [[1]](https://github.com/karamolegkos/Diastema/blob/main/diastema/microstack-installation/microstack-installation.md#references). It can be used to make public, private or hybrid virtual clouds. 

MicroStack is not so well documented as the other OpenStack versions, so here is a nice guide to get you started with a mini cloud!

# How to install
We will use some iptables commands to make the right firewall for our cloud!
These commands will let your Virtual Machines in the cloud to have internet access:
```
sudo iptables -P INPUT ACCEPT
sudo iptables -P FORWARD ACCEPT
sudo iptables -P OUTPUT ACCEPT
```
Wait about 1-2 minutes and then type the below commands:
```
sudo iptables -t nat -F
sudo iptables -t mangle -F
sudo iptables -F
sudo iptables -X
sudo reboot
```
MicroStack uses snap, so let's use it!
```
sudo snap install microstack --beta --devmode
```
This will make a test project inside your MicroStack:
```
sudo microstack init --auto --control
```
Do the following to have the right configurations for your internet access inside of your Virtual Machines:
```
sudo microstack.openstack subnet set --dhcp external-subnet
sudo microstack.openstack subnet set --dhcp test-subnet
sudo microstack.openstack subnet set --dns-nameserver 8.8.8.8 external-subnet
sudo microstack.openstack subnet set --dns-nameserver 8.8.8.8 test-subnet
sudo microstack.openstack network set --share external
sudo microstack.openstack network set --share test
```
Then finish the installations with the commands below:
```
sudo iptables -t nat -A POSTROUTING -s 10.20.20.1/24 ! -d 10.20.20.1/24 -j MASQUERADE
sudo sysctl net.ipv4.ip_forward=1
```
! The last two commands must run on start-up because they will reset after any reboot !

Also after a reboot run the following:
```
sudo iptables -P INPUT ACCEPT
sudo iptables -P FORWARD ACCEPT
sudo iptables -P OUTPUT ACCEPT
```

# Important
You can access OpenStack Horizon (The OpenStack Dashboard) through your browser in the URL: http://10.20.20.1/ .

The Dashboard will be accessable from your machine through the port 80.

# Useful Commands!
- Get your admin keystone password:
```
sudo snap get microstack config.credentials.keystone-password
```
- If you have an SSH key for a Virtual Machine, then your key must have the permissions below with the .pem ending in the name of it:
```
chmod 400 key-name.pem
```
- Upload a new qcow2 image in OpenStack Glance (Image Service) through CLI:
```
microstack.openstack image create --disk-format qcow2 --container-format bare --public --file /path/file.qcow2 "name-of-the-image"
```
- Connect in a Virtual Machine using an SSH key:
```
ssh -i key-name.pem <user>@<ip-inside-the-cloud>
```
- Check your MicroStack's configurations:
```
sudo snap get microstack
```
- Configure your Dashboard's port (You can use simial commands for other configurations also):
```
# View the port
sudo snap get microstack config.network.ports.dashboard

# Change the port
sudo snap set microstack config.network.ports.dashboard=8787

# Reset the port
sudo snap unset microstack config.network.ports.dashboard
sudo reboot
```
- Use **openstack** instead of **microstack.openstack**:
```
sudo snap alias microstack.openstack openstack
```
- OpenStack uses a MySQL DB for its services, so:
```
# Get mysql client
sudo apt install mysql-client-core-8.0
# Get your MicroStack MySQL password
sudo snap get microstack config.credentials.mysql-root-password

# Then type:
sudo mysql -u root -p -S /var/snap/microstack/common/run/mysql/mysqld.sock
# Then use your MicroStack MySQL password
```
- Change a quota for your OpenStack profiles and projects
```
# View default quotas for all projects
microstack.openstack quota show --default

# View quotas for "admin" project
microstack.openstack quota show admin

# Change instances quotas for "admin" project
microstack.openstack quota set --instances 15 admin
```

# References

- [1] https://ubuntu.com/openstack/install
