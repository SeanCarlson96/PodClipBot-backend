# PodClipBot

## Setup

    virtualenv -p python3 venv
    . ./venv/bin/activate
    pip install -r requirements.txt
    brew install libmagic
    brew install ffmpeg
    pip install git+https://github.com/m-bain/whisperx.git

## Running

    export FRONTEND_URL="http://localhost:3000"
    export MONGODB_HOST="localhost:27017"
    export JWT_SECRET_KEY="secret"
    export AWS_SES_SMTP_USERNAME=""
    export AWS_SES_SMTP_PASSWORD=""
    python application.py
