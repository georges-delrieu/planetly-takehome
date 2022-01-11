import docker

def getting_container_list():
    client = docker.from_env()
    try:
        return client.containers.list()
    except AssertionError as e:
        print(f"{e}: Could not list your containers")