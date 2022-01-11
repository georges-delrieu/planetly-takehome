from fastapi import FastAPI, HTTPException
from app.utils import getting_container_list

app = FastAPI(title="Status State API",description="Checks the status of locally running containers at launch")

def listing_containers():
    running_containers = getting_container_list()
    try:
        return [{"name": str(running_container.name),
                "status": str(running_container.status),
                "image": str(running_container.image),
                "container ID": str(running_container.short_id)} 
                for running_container in running_containers]
    except:
        raise HTTPException(status_code=500, detail="Containers not found")


@app.on_event("startup")
def display_statuses():
    listing_containers()

@app.get("/status")
async def status():
    return listing_containers()


