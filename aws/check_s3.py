from aws.s3_client import get_s3_client
from utils.logger import get_logger
from botocore.exceptions import ClientError
from config.settings import S3_BUCKET_NAME 
logger = get_logger(__name__)
def ensure_s3_bucket_exists():
    """Ensure S3 bucket exists."""
    try:
        logger.info(f"Starting S3 Bucket check for: {S3_BUCKET_NAME}")
        s3_client = get_s3_client()
        try:
            s3_client.head_bucket(Bucket=S3_BUCKET_NAME)
            logger.info(f"A S3 bucket '{S3_BUCKET_NAME}' exists")
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                s3_client.create_bucket(Bucket=S3_BUCKET_NAME)
                logger.info(f"Created S3 bucket '{S3_BUCKET_NAME}'")
        return True
    except Exception as e:
        logger.error(f"S3 bucket error: {str(e)}")
        return False
