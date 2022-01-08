from fastapi import FastAPI
import docker

app = FastAPI(title="Status State API",description="Recurringly checks the status of locally running containers")

def listing_containers():
    client = docker.from_env()
    running_containers = client.containers.list()
    return [{"name": str(running_container.name),
            "status": str(running_container.status),
            "image": str(running_container.image),
            "container ID": str(running_container.id)} 
            for running_container in running_containers]

@app.on_event("startup")
def display_statuses():
    listing_containers()

@app.get("/")
async def root():
    return listing_containers()


