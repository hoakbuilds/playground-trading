DOCKER_BUILD = docker build 
DOCKER_RUN = docker run
DOCKER_STOP = docker stop
DOCKER_RM = docker rm

build_app:
	$(DOCKER_BUILD) . -t playground

start_app:
	$(DOCKER_RUN) -d -p 5000:5566 --name playground playground -env docker

stop_backend:
	$(DOCKER_STOP) playground
	$(DOCKER_RM) playground