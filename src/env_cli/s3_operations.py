import boto3
from botocore.exceptions import ClientError
import os

# Define a custom exception for S3 operation errors
class S3OperationError(Exception):
    """Custom exception raised for controlled S3 operation errors (e.g., non-existent bucket, access denied)."""
    pass

class S3BucketManager:
    """
    A utility class for managing common Amazon S3 operations like listing objects
    and retrieving object data, handling exceptions gracefully.
    """
    def __init__(self, bucket_name):
        """
        Initializes the S3BucketManager with a specific bucket name.
        Initializes the S3 client.
        
        Args:
            bucket_name (str): The name of the S3 bucket to operate on.
        """
        self.bucket_name = bucket_name
        self.s3_client = boto3.client('s3')

    def list(self, prefix=''):
        """
        Lists all objects (files) in the configured S3 bucket using a generator
        for memory efficiency and automatic pagination.

        Args:
            prefix (str, optional): A prefix to filter the object keys by. Defaults to ''.

        Yields:
            str: The key (full path/filename) of an object in the S3 bucket.

        Raises:
            S3OperationError: If the bucket does not exist or access is denied.
            ClientError: If an unexpected Boto3 error occurs.
            Exception: For any other unexpected errors.
        """
        try:
            # Use a Paginator for automatic pagination handling, which is cleaner
            # than manually managing the ContinuationToken.
            paginator = self.s3_client.get_paginator('list_objects_v2')
            
            # Configure the pagination operation
            operation_parameters = {
                'Bucket': self.bucket_name,
                'Prefix': prefix
            }
            
            # Create a page iterator
            page_iterator = paginator.paginate(**operation_parameters)

            # Iterate over each page of results
            for page in page_iterator:
                # Check if 'Contents' key exists (it doesn't if the bucket is empty)
                if 'Contents' in page:
                    for obj in page['Contents']:
                        # Use yield to return one key at a time (generator behavior)
                        yield obj['Key']

        except ClientError as e:
            # Determine the AWS error code and raise a custom, descriptive error
            error_code = e.response.get('Error', {}).get('Code')
            if error_code == 'NoSuchBucket':
                raise S3OperationError(f"Bucket Error: The S3 bucket '{self.bucket_name}' does not exist.") from e
            elif error_code == 'AccessDenied':
                raise S3OperationError(f"Permission Error: Access denied to bucket '{self.bucket_name}'. Check credentials and region.") from e
            else:
                # For other known Boto3 errors, re-raise the original ClientError
                raise
        except Exception as e:
            # For any other unexpected errors, raise a generic operation error
            raise S3OperationError(f"An unexpected error occurred during S3 listing: {type(e).__name__} - {e}") from e

    def put_object_data(self, object_key, data, content_type='text/plain'):
        """
        Uploads data to a specific S3 object (file) in the configured bucket.

        Args:
            object_key (str): The full key (path/filename) where the data will be stored.
            data (bytes or str): The content to upload. If a string, it will be encoded to bytes.
            content_type (str, optional): The Content-Type header for the object. Defaults to 'text/plain'.

        Returns:
            dict: The response metadata from the S3 put_object operation.

        Raises:
            S3OperationError: If the bucket does not exist or access is denied.
            ClientError: If an unexpected Boto3 error occurs.
        """
        # Ensure data is in bytes format for upload
        if isinstance(data, str):
            data = data.encode('utf-8')

        try:
            response = self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=data,
                ContentType=content_type
            )
            return response
            
        except ClientError as e:
            # Determine the AWS error code and raise a custom, descriptive error
            error_code = e.response.get('Error', {}).get('Code')
            if error_code == 'NoSuchBucket':
                raise S3OperationError(f"Bucket Error: The S3 bucket '{self.bucket_name}' does not exist.") from e
            elif error_code == 'AccessDenied':
                raise S3OperationError(f"Permission Error: Access denied to bucket '{self.bucket_name}'. Check credentials and region.") from e
            else:
                # For other known Boto3 errors, re-raise the original ClientError
                raise
        except Exception as e:
            # For any other unexpected errors, raise a generic operation error
            raise S3OperationError(f"An unexpected error occurred during S3 object upload: {type(e).__name__} - {e}") from e

    def get_object_data(self, object_key):
        """
        Retrieves the content of a specific S3 object (file) from the configured bucket.

        Args:
            object_key (str): The full key (path/filename) of the object.

        Returns:
            bytes: The content of the object as bytes.

        Raises:
            S3OperationError: If the object, bucket does not exist, or access is denied.
            ClientError: If an unexpected Boto3 error occurs.
        """
        try:
            # Get the object
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=object_key)
            
            # Read the content from the Body stream
            # NOTE: This loads the entire file into memory. Use carefully for large files.
            object_data = response['Body'].read()
            
            return object_data
            
        except ClientError as e:
            # Determine the AWS error code and raise a custom, descriptive error
            error_code = e.response.get('Error', {}).get('Code')
            if error_code == 'NoSuchKey':
                raise S3OperationError(f"Object Error: The S3 object '{object_key}' in bucket '{self.bucket_name}' does not exist.") from e
            elif error_code == 'NoSuchBucket':
                raise S3OperationError(f"Bucket Error: The S3 bucket '{self.bucket_name}' does not exist.") from e
            elif error_code == 'AccessDenied':
                raise S3OperationError(f"Permission Error: Access denied to bucket '{self.bucket_name}'. Check credentials and region.") from e
            else:
                # For other known Boto3 errors, re-raise the original ClientError
                raise
        except Exception as e:
            # For any other unexpected errors, raise a generic operation error
            raise S3OperationError(f"An unexpected error occurred during S3 object retrieval: {type(e).__name__} - {e}") from e

