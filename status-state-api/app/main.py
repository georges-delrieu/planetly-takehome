from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
import docker
import logging


app = FastAPI(title="Status State API",description="Recurringly checks the status of locally running containers")
logger = logging.getLogger(__name__)

def listing_containers():
    client = docker.from_env()
    running_containers = client.containers.list()
    return [{"name": str(running_container.name),
            "status": str(running_container.status),
            "image": str(running_container.image),
            "container ID": str(running_container.id)} 
            for running_container in running_containers]


scheduler = BackgroundScheduler(daemon = True)
scheduler.add_job(listing_containers, 'interval', seconds=30)

@app.on_event("startup")
def display_statuses():
    scheduler.start()
    logger.info("Monitoring Container Health")

@app.get("/")
async def root():
    return listing_containers()


