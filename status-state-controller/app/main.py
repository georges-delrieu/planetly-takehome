from func import fetching_containers, clearing_containers, restarting_containers
import asyncio
import docker

async def asgi_handler(scope, receiver, sender):
  global loop
  if scope['type'] == 'lifespan':
    message = await receiver()
    if message['type'] == 'lifespan.startup':
      loop = asyncio.get_running_loop()
      loop.create_task(cron())
      await sender({'type': 'lifespan.startup.complete'})
    elif message['type'] == 'lifespan.shutdown':
      await sender({'type': 'lifespan.shutdown.complete'})

async def cron():
    client = docker.from_env()
    status_state_list = fetching_containers()
    while True:
        clearing_containers(status_state_list, client)
        restarting_containers(status_state_list, client)
        await asyncio.sleep(30)

if __name__ == '__main__':
  import uvicorn
  uvicorn.run("main:asgi_handler",
                host = '0.0.0.0',
                port = 8000,
                lifespan = 'on',
                workers = 1,
                log_level = "warning",
                interface = 'asgi3',
                timeout_keep_alive = 5)