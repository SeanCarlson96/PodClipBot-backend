# Use Python slim-buster as a parent image
FROM python:3.9-slim-buster as build

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Install necessary Debian packages
RUN apt-get update && apt-get install -y \
    gcc \
    libmagic1 \
    ffmpeg \
    python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy the environment file
COPY environment.yml .

# Install Python packages not found in Conda
RUN pip install gunicorn gevent httpx hmmlearn moviepy flask_mongoengine flask_bcrypt python-magic python-dotenv flask_socketio flask_mail pydub stripe

# Install whisperx
RUN pip install git+https://github.com/m-bain/whisperx.git

# Use a smaller image to create the final image
FROM python:3.9-slim-buster

WORKDIR /app

COPY --from=build /app /app

# Make sure the environment is activated:
RUN echo "Make sure flask is installed:"
RUN python -c "import flask"

# Make the image start with the Flask app:
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8000", "--worker-class", "gevent", "-w", "1", "application:application"]
