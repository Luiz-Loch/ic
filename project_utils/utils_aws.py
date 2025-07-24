import boto3
import requests
from botocore.exceptions import NoCredentialsError


def upload_to_aws(local_file: str, bucket: str, s3_file: str) -> bool:
    """
    Uploads a file to an AWS S3 bucket.

    Args:
        local_file (str): The path to the local file to be uploaded.
        bucket (str): The name of the S3 bucket.
        s3_file (str): The name of the file to be saved in the S3 bucket.

    Returns:
        bool: True if the upload was successful, False otherwise.
    """
    s3 = boto3.client('s3')

    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

def get_instance_id() -> str | None:
    """
    Retrieves the instance ID of the current EC2 instance.

    Returns:
        str | None: The instance ID if available, None otherwise.
    """
    try:
        # Get the token
        token_url = 'http://169.254.169.254/latest/api/token'
        token_headers = {'X-aws-ec2-metadata-token-ttl-seconds': '21600'}
        token_response = requests.put(token_url, headers=token_headers)
        token = token_response.text

        # Use the token to access the metadata
        metadata_url = 'http://169.254.169.254/latest/meta-data/instance-id'
        metadata_headers = {'X-aws-ec2-metadata-token': token}
        response = requests.get(metadata_url, headers=metadata_headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error retrieving instance ID: {e}")
        return None

def get_instance_name(instance_id: str | None, region_name: str = 'us-east-1') -> str | None:
    """
    Retrieves the name of the EC2 instance (Tag "Name").

    Args:
        instance_id (str | None): The ID of the instance.
        region_name (str): The AWS region name. Default is 'us-east-1'.

    Returns:
        str | None: The name of the instance if available, None otherwise.
    """
    try:
        ec2 = boto3.client('ec2', region_name=region_name)
        response = ec2.describe_instances(InstanceIds=[instance_id])
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                for tag in instance.get('Tags', []):
                    if tag['Key'] == 'Name':
                        return tag['Value']
        return None
    except Exception as e:
        print(f"Error retrieving instance name: {e}")
        return None