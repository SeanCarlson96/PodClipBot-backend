#
# Common commands for PCB
#

build:
	docker build -t pcb-clipper .

push:
	docker tag pcb-clipper 328963664440.dkr.ecr.us-east-2.amazonaws.com/pcb-clipper:latest
	docker push 328963664440.dkr.ecr.us-east-2.amazonaws.com/pcb-clipper:latest