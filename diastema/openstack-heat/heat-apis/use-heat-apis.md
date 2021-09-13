# Examples on using the Heat REST APIs
This guide will analyze how to contact with the Heat APIs [[1]](https://github.com/karamolegkos/Diastema/blob/main/diastema/openstack-heat/heat-apis/use-heat-apis.md#references) using the OpenStack authentication.

I made this guide using MicroStack but the following should work on all versions of OpenStack.

The examples below will be using the Postman API Platform [[2]](https://github.com/karamolegkos/Diastema/blob/main/diastema/openstack-heat/heat-apis/use-heat-apis.md#references).

# Authentication
To use the API Server we need first to authenticate using the OpenStack Keystone Service. For this, we need to follow the Authentication and API request workflow [[3]](https://github.com/karamolegkos/Diastema/blob/main/diastema/openstack-heat/heat-apis/use-heat-apis.md#references).

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

If the request succeeds, it returns the Created (201) response code along with the token as a value in the '**X-Subject-Token**' response header. The header is followed by a response body that has an object of type token which has the token expiration date and time in the form "expires_at":"datetime" along with other attributes.

```
# For this guide lets assume that the Token is t0ken
```

# Make a Heat test call
Get the id of one of your porjects and follow the guide below.
```
# For this guide lets assume that the <project_id> is the id of your project
# The <project_id> is also called tenant_id.
```
Let's make a test call, the call will be like the one below:
```
Method: GET
URL: http://<ip>:8004/v1/<project_id>/stacks
```
Do not forget to include the header below to your call:
```
X-Auth-Token : t0ken
```
Now send the call, it will return you the stacks of your project.

# Use a template
In the Heat APIs you can give a JSON Heat template and make a stack right away!

// TODO: finish this sections with example calls


# References
- [1] https://docs.openstack.org/api-ref/orchestration/
- [2] https://www.postman.com/
- [3] https://docs.openstack.org/api-quick-start/api-quick-start.html
