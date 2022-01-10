# Takehome assignment for Planetly

## Quickstart
To get things started make sure you have [Docker installed](https://docs.docker.com/get-docker/) and in path and run:
```
docker compose up
```

## Architecture
![Schematic of architecture](/schematic_planetly.png)
The architecture of the tool revolves mainly around two containers: the Status State API (SSA) and the Status State Controller (SSC).
### Status State API: Monitoring 👀
The role of the SSA is to take a snapshot of locally running containers at the start of the SSA and make this snapshot available through a http endpoint.

The http requests to the SSA are handled by FastAPI, a web framework for developing APIs in Python.
For this use case, the main strengths of using [FastAPI](https://github.com/tiangolo/fastapi) is the very fast response time, the ease of development and the documentation.

The FastAPI app exposes a single endpoint (/) which triggers and responds the [Python SDK](https://docker-py.readthedocs.io/en/stable/containers.html) equivalent for ```docker ps``` upon request. 

### Status State Controller: Healing 🚑
The role of the SSC is to take action based on the data collected by the SSA. It is tasked with ensuring that the locally running containers remain the same throughout the lifetime of the tool. 

Concretely, the SSC ingests the snapshot created by the SSA at launch and compares the running containers against this snapshot every 30 seconds. If some of the original containers go down, it restarts them. If new containers are created, it takes them down.

The SSC is another Python-based container, split in two parts: func.py and main.py. 

Func.py contains the functions to ping the SSA, restart containers and stop them when necessary.

Main.py contains the CRON job definition and the asyncronous loop. Main.py uses the python built-in module [asyncio](https://docs.python.org/3/library/asyncio.html) to create the loop.

## Improvements
An issue with the current design is that it simply monitors container runtime. However to keep a healthy system running it could also check for application state. Indeed the application inside the container might be failing while the container is up.
A more sophisticated version of the tool could be collecting logs from the containers and restarting them upon exceeding a pre-set severity level.
## Kubernetes Implementation
### ReplicaSet
The tool is redundant with some of the built-in Kubernetes features and could be replaced by a [ReplicaSet](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/).

In a Kubernetes cluster, we would arrange our containers so that each of them is hosted in a separated pod. The ReplicaSet would then be a setting of Deployment tasked with terminating the unnecessary pods and starting the required ones.

### Deployment
To start our cluster, we would define a desired state through a deployment.yaml file. In it, we would set the pods that we want to see running and the numbers of replica we expect.

The file ```example-nginx-deployment.yaml``` provides an example on how containers would be defined. In there, the spec 'replicas' would have to be set to the number of nginx containers that we want to have up.

For Kubernetes to maintain our desired containers up, best practice would be to create a deployment file for each of the containers and let the ReplicaSet maintain the desired state.

After starting the cluster with the command:
````
kubectl apply -f ./example-nginx-deployment.yaml
````
We would be able to monitor the status of our containers with:
````
kubectl get pods --show-labels
````
