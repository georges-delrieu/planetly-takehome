import requests
import docker
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
import ast
import logging

# Initializing the app and the logging
app = FastAPI(title="Status State Controller",description="Keeps required containers up and shuts down other containers")
logging.basicConfig(level=logging.INFO)

def fetching_containers():
    r = requests.get('http://host.docker.internal:80')
    return {container["container ID"]: container["name"] for container in ast.literal_eval(r.text)}

def clearing_containers(status_state_list):
    '''Destroys containers outside the list of required containers'''
    client = docker.from_env()
    logging.info('Checking for unwelcome containers')
    for running_container in client.containers.list():
        if running_container.id not in status_state_list:
            logging.warning(f'Container {running_container.name} should not be up... shutting it down')
            running_container.stop()

def restarting_containers(status_state_list):
    '''Restarts stopped containers among the required containers'''
    client = docker.from_env()
    id_running_containers = [container.id for container in client.containers.list()]
    logging.info('Checking for missing containers')
    for required_container in status_state_list.keys():
        if required_container not in id_running_containers:
            logging.warning(f'Container {status_state_list[required_container]} should not be down... restarting it')
            container = client.containers.get(required_container)
            container.start()

@app.on_event("startup")
def launch():
    status_state_list = fetching_containers()
    scheduler = BackgroundScheduler(daemon = True)
    scheduler.add_job(clearing_containers, 'interval', seconds=30, args=[status_state_list])
    scheduler.add_job(restarting_containers, 'interval', seconds=30, args=[status_state_list])
    scheduler.start()
