# Use an official Python runtime as a parent image
FROM continuumio/miniconda3

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Install libmagic
RUN apt-get update && apt-get install -y libmagic1
# Install ffmpeg
RUN apt-get install -y ffmpeg

# something for whisperx
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev

# Copy the environment file
COPY environment.yml .

# Update conda packages
RUN conda update conda

# Create the environment:
RUN conda env create -f environment.yml

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "whisperx", "/bin/bash", "-c"]

# RUN pip install torch==2.0.0 torchvision==0.15.0 torchaudio==2.0.0  # not sure
# why this line worked when building the image on my machine, but did not work
# when in codebuild
# lets try this conda line from whixperx instead
RUN conda install pytorch==2.0.0 torchvision==0.15.0 torchaudio==2.0.0 pytorch-cuda=11.7 -c pytorch -c nvidia

# Install the packages not found in Conda
RUN pip install gunicorn gevent httpx hmmlearn moviepy flask_mongoengine flask_bcrypt python-magic python-dotenv flask_socketio flask_mail pydub stripe

# Install whisperx
RUN pip install git+https://github.com/m-bain/whisperx.git

# Make sure the environment is activated:
RUN echo "Make sure flask is installed:"
RUN python -c "import flask"

# Make the image start with the Flask app:
# ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "whisperx", "python",
# "application.py"]
# ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "whisperx", "gunicorn", "--worker-class", "gevent", "-w", "1", "application:application"]
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "whisperx", "gunicorn", "--bind", "0.0.0.0:8000", "--worker-class", "gevent", "-w", "1", "application:application"]
