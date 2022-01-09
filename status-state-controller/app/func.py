import requests
import ast
import logging

logging.basicConfig(level=logging.INFO)

def fetching_containers():
    r = requests.get('http://host.docker.internal:8080')
    return [{"container_id": container["container ID"]
            ,"container_name": container["name"]} for container in ast.literal_eval(r.text)]

def clearing_containers(status_state_list, client):
    '''Destroys containers outside the list of required containers'''
    logging.info('Checking for unwelcome containers')
    id_required_containers = [container['container_id'] for container in status_state_list]
    for running_container in client.containers.list():
        if running_container.short_id not in id_required_containers:
            logging.warning(f'Container {running_container.name} should not be up... shutting it down')
            running_container.stop()
            logging.warning(f'Container {running_container.name} was successfully stopped ✅')

def restarting_containers(status_state_list, client):
    '''Restarts stopped containers among the required containers'''
    id_running_containers = [container.short_id for container in client.containers.list()]
    id_required_containers = [container['container_id'] for container in status_state_list]
    logging.info('Checking for missing containers')
    for required_container in id_required_containers:
        if required_container not in id_running_containers:
            name_required_container = status_state_list[id_required_containers.index(required_container)]["container_name"]
            logging.warning(f'Container {name_required_container} should not be down... restarting it')
            container = client.containers.get(required_container)
            container.start()
            logging.warning(f'Container {name_required_container} was successfully restarted ✅')
