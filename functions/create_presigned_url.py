import boto3
from botocore.exceptions import NoCredentialsError
from boto3.s3.transfer import TransferConfig, S3Transfer

def progress_callback(bytes_transferred):
    # This function will be called every time progress is made.
    print("Downloaded", bytes_transferred, "bytes")

def retreive_video_file(video_name):
    """Retreive video file from S3 bucket"""
    s3 = boto3.client('s3')
    transfer_config = TransferConfig(use_threads=False)
    transfer = S3Transfer(s3, transfer_config)
    try:
        print("Retrieving video file from S3 bucket")
        print("Video name: ", video_name)
        transfer.download_file('video-file-uploads', video_name, video_name, callback=progress_callback)
    except NoCredentialsError:
        print("No AWS credentials were found.")
        return None
    return video_name

def create_presigned_url(bucket_name, object_name, expiration=10000):
    """Generate a presigned URL S3 PUT request"""
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url('put_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except NoCredentialsError:
        print("No AWS credentials were found.")
        return None
    return response
