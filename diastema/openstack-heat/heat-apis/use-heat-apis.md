# Examples on using the Heat REST APIs
This guide will analyze how to contact with the Heat APIs [1] using the OpenStack authentication.

I made this guide using MicroStack but the following should work on all versions of OpenStack.

The examples below will be using the Postman API Platform [[2]](https://github.com/karamolegkos/Diastema/blob/main/diastema/openstack-heat/heat-apis/use-heat-apis.md#references).

# Authentication
To use the API Server we need first to authenticate using the OpenStack Keystone Service. For this, we need to follow the Authentication and API request workflow [3].

From now on remember the following:
```
<ip> = your MicroStack Server API (probably your own)
Example:
<ip> = 86.53.200.78
```
You will also need the admin keystone password of your OpenStack enviroment. (Below is an example on how to get it for the Ubuntu MicroStack version):
```
sudo snap get microstack config.credentials.keystone-password
# For this guide lets assume that the password is KeYst0ne
```
To authenticate, we need a Token for our calls. A Token is only "alive" for only 1 to 2 hours. To get the token we need to do the following call:
```
Method: POST
URL: http://<ip>:5000/v3/auth/tokens?nocatalog
```
The body of the call, needs to be like this:
```json
{ "auth": { 
    "identity": { 
        "methods": ["password"],
        "password": {
            "user": {
                "domain": {
                    "name": "Default"},
                    "name": "admin", 
                    "password": "KeYst0ne"
                    } 
            } 
        }, 
        "scope": { 
            "project": { 
                "domain": { 
                    "name": "Default" 
                }, 
                "name":  "admin" 
            } 
        } 
    }
}
```

# References
- [1] https://docs.openstack.org/api-ref/orchestration/
- [2] https://www.postman.com/
- [3] https://docs.openstack.org/api-quick-start/api-quick-start.html
