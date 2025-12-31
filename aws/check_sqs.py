from aws.sqs_client import get_sqs_client
from utils.logger import get_logger
from config.settings import SQS_QUEUE_URL, SQS_QUEUE_NAME
logger = get_logger(__name__)

def ensure_sqs_queue_exists() -> str:
    """
    Validate SQS queue URL is configured.
    
    Returns:
        str: The SQS Queue URL if configured, None otherwise
    """
    try:
        if not SQS_QUEUE_URL:
            logger.error("SQS_QUEUE_NAME is not configured in environment variables")
            return None
        
        logger.info(f"Using SQS Queue: {SQS_QUEUE_NAME} -> {SQS_QUEUE_URL}")
        return SQS_QUEUE_URL
                
    except Exception as e:
        logger.error(f"SQS configuration error: {str(e)}", exc_info=True)
        return None