# planetly-takehome


to get things started
````
docker run -d --name api -p 80:80 -v /var/run/docker.sock:/var/run/docker.sock api
````

docker run -d --name controller -e PYTHONUNBUFFERED=1 -p 90:90 -v /var/run/docker.sock:/var/run/docker.sock controller


docker on docker doc:
https://jpetazzo.github.io/2015/09/03/do-not-use-docker-in-docker-for-ci/

