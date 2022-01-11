from func import fetching_containers, clearing_containers, restarting_containers
import asyncio
import os

async def asgi_handler(scope, receiver, sender):
  global loop
  if scope['type'] == 'lifespan':
    message = await receiver()
    if message['type'] == 'lifespan.startup':
      loop = asyncio.get_running_loop()
      loop.create_task(cron())

async def cron():
    status_state_list = fetching_containers()
    while True:
        try:
          clearing_containers(status_state_list)
          restarting_containers(status_state_list)
          await asyncio.sleep(30)
        except AssertionError as e:
          print(e)

if __name__ == '__main__':
  import uvicorn
  uvicorn.run("main:asgi_handler",
                host = '0.0.0.0',
                port = os.environ['PORT_CONTROLLER'],
                lifespan = 'on',
                workers = 1,
                log_level = "warning",
                timeout_keep_alive = 5)