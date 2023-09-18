# Use the official Python base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /var/task
ENV PYTHONPATH "${PYTHONPATH}:/var/task"

# Install system dependencies
RUN apt update && apt install -y git gcc libmagic-dev libmagick++-dev ffmpeg ghostscript imagemagick
RUN sed -i '/<policy domain="path" rights="none" pattern="@\*"/d' /etc/ImageMagick-6/policy.xml

# Copy the Lambda function code into the container
COPY functions functions
COPY util util
COPY file_security_functions file_security_functions
COPY whisperx whisperx

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN cd whisperx && pip install .

# Uninstall build tools
RUN apt remove -y gcc

# Set the handler for the Lambda function
CMD ["python", "functions/build_clip_v2.py"]
