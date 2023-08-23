#
# Common commands for PCB
#

build:
	docker build --platform=linux/amd64 -t pcb-clipper .

push:
	docker tag pcb-clipper 328963664440.dkr.ecr.us-east-2.amazonaws.com/pcb-clipper:latest
	aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 328963664440.dkr.ecr.us-east-2.amazonaws.com
	docker push 328963664440.dkr.ecr.us-east-2.amazonaws.com/pcb-clipper:latest
