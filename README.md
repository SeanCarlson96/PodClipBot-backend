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

## Docker Image

    docker build -t pcb-clipper .
    docker tag pcb-clipper 328963664440.dkr.ecr.us-east-2.amazonaws.com/pcb-clipper:latest
    aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 328963664440.dkr.ecr.us-east-2.amazonaws.com
    docker push 328963664440.dkr.ecr.us-east-2.amazonaws.com/pcb-clipper:latest

## SQS: Running Serverless Clip Builder
Example payload to send to https://us-east-2.console.aws.amazon.com/sqs/v2/home?region=us-east-2#/queues/https%3A%2F%2Fsqs.us-east-2.amazonaws.com%2F328963664440%2FPCBClipProcessingQueue/send-receive

    {
        "video-file-name": "s3://video-file-uploads-test/Na Pali 2022.mp4",
        "clip-id": "1", 
        "clip-info": {
            "subtitlesToggle": True
        },
        "start-time": "00:01:00",
        "end-time": "00:02:00",
        "music-file": "",
        "watermark-file": ""
    }

    #os.environ["INPUT_PAYLOAD"] = json.dumps(payload)

## Stepfunction (deprecated): Running Serverless Clip Builder

```
    from util.stepfunction import start_step_function
    start_step_function("arn:aws:states:us-east-2:328963664440:stateMachine:PcbClipBuilderStateMachine", [clipData, clipData])
```

Example payload from step function UI:

["{\"video-file-name\": \"s3://video-file-uploads-test/testvid.mp4\", \"clip-id\": \"1\", \"clip-info\": {\"subtitlesToggle\": true}, \"start-time\": \"00:01:00\", \"end-time\": \"00:02:00\", \"music-file\": \"\", \"watermark-file\": \"\"}"]

