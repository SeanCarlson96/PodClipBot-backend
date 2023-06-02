# Use Miniconda3 as a parent image
# FROM continuumio/miniconda3:4.9.2-alpine
FROM continuumio/miniconda3

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Install necessary packages, create environment and install pip packages
RUN apt-get update && apt-get install -y libmagic1 ffmpeg gcc python3-dev && \
    rm -rf /var/lib/apt/lists/* && \
    conda update conda && \
    conda env create -f environment.yml && \
    conda install pytorch==2.0.0 torchvision==0.15.0 torchaudio==2.0.0 pytorch-cuda=11.7 -c pytorch -c nvidia && \
    # pip install torch==2.0.0 torchvision==0.15.1 torchaudio==2.0.1 && \
    pip install gunicorn gevent httpx hmmlearn moviepy flask_mongoengine flask_bcrypt python-magic python-dotenv flask_socketio flask_mail pydub stripe && \
    pip install git+https://github.com/m-bain/whisperx.git

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "whisperx", "/bin/bash", "-c"]

# Make sure the environment is activated:
RUN echo "Make sure flask is installed:"
RUN python -c "import flask"

# Make the image start with the Flask app:
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "whisperx", "gunicorn", "--bind", "0.0.0.0:8000", "--worker-class", "gevent", "-w", "1", "application:application"]
