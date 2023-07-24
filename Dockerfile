# Use the official Python base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /var/task

# Install system dependencies
RUN apt update && apt install -y git gcc libmagic-dev ffmpeg

# Copy the Lambda function code into the container
COPY functions functions
COPY util util

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install git+https://github.com/m-bain/whisperx.git
RUN pip install awslambdaric

# Cache WhisperX Model
RUN python util/download_whisperx_model.py

# Uninstall build tools
RUN apt remove -y gcc

# Set the handler for the Lambda function
CMD ["python", "functions.build_clip_lambda.lambda_handler"]
