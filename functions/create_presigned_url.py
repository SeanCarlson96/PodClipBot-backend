import os
import boto3
from botocore.exceptions import NoCredentialsError
from boto3.s3.transfer import TransferConfig, S3Transfer
from botocore.client import Config

def progress_callback(bytes_transferred):
    # This function will be called every time progress is made.
    print("Downloaded", bytes_transferred, "bytes")

def retreive_video_file(video_name, destination_dir):
    """Retreive video file from S3 bucket"""
    s3 = boto3.client('s3')
    transfer_config = TransferConfig(use_threads=False)
    transfer = S3Transfer(s3, transfer_config)
    try:
        print("Retrieving video file from S3 bucket")
        print("Video name: ", video_name)
        directory_path = destination_dir + "/" + "/".join(video_name.split("/")[:-1])

        if not os.path.exists(directory_path):
            # Create the directory
            os.makedirs(directory_path)
            print(f"Directory '{directory_path}' created successfully.")

        transfer.download_file('video-file-uploads', video_name, directory_path, callback=progress_callback)
        return directory_path  # return the full path, not just the filename
    except NoCredentialsError:
        print("No AWS credentials were found.")
        return None

def upload_video_file(video_name: str, destination_dir: str):
    """Upload video file to S3 bucket"""
    s3 = boto3.client('s3')
    transfer_config = TransferConfig(use_threads=False)
    transfer = S3Transfer(s3, transfer_config)
    try:
        print("Video name: ", video_name)
        transfer.upload_file(video_name, 'video-file-uploads', destination_dir, callback=progress_callback)
    except NoCredentialsError:
        print("No AWS credentials were found.")

def create_presigned_url(bucket_name, object_name, expiration=10000):
    """Generate a presigned URL S3 PUT request"""
    s3_client = boto3.client('s3', region_name='us-east-2', config=Config(signature_version='s3v4'))
    try:
        response = s3_client.generate_presigned_url('put_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except NoCredentialsError:
        print("No AWS credentials were found.")
        return None
    return response
