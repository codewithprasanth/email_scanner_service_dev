import boto3
import certifi
from config.settings import *
from utils.logger import get_logger

logger = get_logger(__name__)

def get_s3_client():
    """Create and return S3 client with logging."""
    try:
        logger.info("Initializing S3 client...")
        client_config = {
            'aws_access_key_id': AWS_ACCESS_KEY_ID,
            'aws_secret_access_key': AWS_SECRET_ACCESS_KEY,
            'region_name': AWS_REGION,
        }
        
        # Add session token if available
        if AWS_SESSION_TOKEN:
            client_config['aws_session_token'] = AWS_SESSION_TOKEN
        
        # Add endpoint URL only if specified (for LocalStack)
        if AWS_ENDPOINT_URL:
            client_config['endpoint_url'] = AWS_ENDPOINT_URL
            client_config['use_ssl'] = False
            client_config['verify'] = False
        else:
            # Use VERIFY_SSL environment variable to control SSL verification
            client_config['verify'] = VERIFY_SSL
        
        client = boto3.client('s3', **client_config)
        logger.info(f"S3 client initialized successfully (region: {AWS_REGION}, SSL verify: {client_config.get('verify', True)})")
        return client
    except Exception as e:
        logger.error(f"Failed to create S3 client: {str(e)}", exc_info=True)
        return None