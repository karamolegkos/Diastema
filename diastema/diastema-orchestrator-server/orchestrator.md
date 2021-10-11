# How to use Docker image

- Put the app.py and the Dockerfile in the same directory
- Then run the following command from the above directory
```
docker build --tag orchestrator-server-image .
docker run -d -p 0.0.0.0:5000:5000 --name orchestrator-server orchestrator-server-image
```
