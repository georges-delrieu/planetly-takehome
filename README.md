# Takehome assignment for Planetly

## Quickstart
To get things started make sure you have [Docker installed](https://docs.docker.com/get-docker/) and in path and run:
```
docker compose up
```

## Architecture
![Schematic of architecture](/compose_schematic.png)

The architecture of the tool revolves mainly around two containers: the Status State API (SSA) and the Status State Controller (SSC).
### Status State API: Monitoring 👀
The role of the SSA is to take a snapshot of locally running containers at the start of the SSA and make this snapshot available through a http endpoint.

The http requests to the SSA are handled by FastAPI, a web framework for developing APIs in Python.
For this use case, the main strengths of using [FastAPI](https://github.com/tiangolo/fastapi) is the very fast response time, the ease of development and the great documentation.

The FastAPI app exposes the /status endpoint which executes and return the output of the [Python SDK](https://docker-py.readthedocs.io/en/stable/containers.html) equivalent for ```docker ps``` upon request. It also exposes an OpenAPI doc for the app at /docs.

### Status State Controller: Healing 🚑
The role of the SSC is to take action based on the data collected by the SSA. It is tasked with ensuring that the locally running containers remain the same throughout the lifetime of the tool. 

Concretely, the SSC ingests the snapshot created by the SSA at launch and compares the running containers against this snapshot every 30 seconds. If some of the original containers go down, it restarts them. If new containers are created, it takes them down.

The SSC is another Python-based container, split in two parts: [func.py](./status-state-controller/app/func.py) and [main.py]((./status-state-controller/app/main.py)). 

Func.py contains the functions to ping the SSA, restart containers and stop them when necessary.

Main.py contains the CRON job definition and the asyncronous loop. Main.py uses the python built-in module [asyncio](https://docs.python.org/3/library/asyncio.html) to create the loop.

## Improvements 🔥
### Application level monitoring
An issue with the current design is that it simply monitors container runtime. However to keep a healthy system running it could also check for application state. Indeed the application inside the container might be failing while the container is up.
A more sophisticated version of the tool could be collecting logs from the containers and restarting them upon exceeding a pre-set severity level. Alternatively, the SSA could also ping the /health endpoint of the running containers.

### Load testing
To further improve the resilience of this tool and prevent downtime it would be important to conduct load testing on it. This would give us better idea of the current response time under stress and make appropriate design decisions.

It could be quickly performed using a tool like [Locust](https://locust.io/).

### Application testing
If the API were to grow in size, it would be important to improve the testing setting and increase the speed of testing.
## Kubernetes Implementation 🌊
### Design
The rough architecture of a Kubernetes implementation of this tool is the following:
![Schematic of architecture](/kubernetes_schematic.png)
### Service and Deployment
To deploy the tool in a Kubernetes cluster and fully take advantage of its scaling potential, we would put a load balancer as service in front of the uvicorn workers in the SSA and SSH. The load balancer is described in the first block ('service') of the [deployment file](./deployment-example.yaml).

We would also increase the number of SSA and SSH containers to balance the load between. This would be set in the second block ('deployment')

### Tooling: Kompose
To quickly transition from the current docker-compose setup to a Kubernetes cluster, [Kompose](https://github.com/kubernetes/kompose) seems appropriate.

Kompose would quickly transform the docker-compose.yaml into a set of Kubernetes manifest files by running 

````
kompose convert -f docker-compose.yaml
````
### Deployment strategy: Blue/green
For this tool, a 'blue/green' strategy of deployment would be suited. The idea of a blue/green deployment is to switch the traffic to new versions at the load balancer level using the version parameter of the 'selector' (line 9 of the [deployment file](./deployment-example.yaml)). 
This would avoid versioning issues and enable instant rollout and rollback.

For a stateless application like this one, the pros of a blue/green strategy outweigh the cons.
## Note on Kubernetes
### ReplicaSet
The tool would be made redundant by Kubernetes if the local containers were hosted inside the cluster. Then, the tool would be replaced by a [ReplicaSet](https://kubernetes.io/docs/concepts/workloads/controllers/replicaset/).

The ReplicaSet defined in the deployment file would take care terminating the unnecessary pods and starting the required ones.



Thanks for reading! 🌱