# Stage 1: Base Image
FROM continuumio/miniconda3 as base

WORKDIR /app

ADD . /app

# Install necessary packages, create environment and install pip packages
RUN apt-get update && apt-get install -y libmagic1 ffmpeg gcc python3-dev && \
    rm -rf /var/lib/apt/lists/* && \
    conda update conda && \
    conda env create -f environment.yml && \
    conda install -n whisperx pytorch==2.0.0 torchvision==0.15.0 torchaudio==2.0.0 pytorch-cuda=11.7 -c pytorch -c nvidia && \
    /opt/conda/envs/whisperx/bin/pip install gunicorn gevent httpx hmmlearn moviepy flask_mongoengine flask_bcrypt python-magic python-dotenv flask_socketio flask_mail pydub stripe && \
    /opt/conda/envs/whisperx/bin/pip install git+https://github.com/m-bain/whisperx.git

# Stage 2: Runtime Image
FROM continuumio/miniconda3 as runtime

COPY --from=base /opt/conda /opt/conda

WORKDIR /app

COPY --from=base /app /app

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "whisperx", "/bin/bash", "-c"]

# Make sure the environment is activated:
RUN echo "Make sure flask is installed:"
RUN python -c "import flask"

# Make the image start with the Flask app:
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "whisperx", "gunicorn", "--bind", "0.0.0.0:8000", "--worker-class", "gevent", "-w", "1", "application:application"]
