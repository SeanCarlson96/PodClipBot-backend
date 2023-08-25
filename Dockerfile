# Use the official Python base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /var/task
ENV PYTHONPATH "${PYTHONPATH}:/var/task"

# Install system dependencies
RUN apt update && apt install -y git gcc libmagic-dev ffmpeg

# Copy the Lambda function code into the container
COPY functions functions
COPY util util
COPY file_security_functions file_security_functions
COPY whisperx whisperx

# Install Python dependencies
COPY requirements.docker.txt .
RUN pip install -r requirements.docker.txt
RUN cd whisperx && pip install -e .

# Cache WhisperX Model
RUN python util/download_whisperx_model.py

# Uninstall build tools
RUN apt remove -y gcc

# Set the handler for the Lambda function
CMD ["python", "functions/build_clip_v2.py"]
