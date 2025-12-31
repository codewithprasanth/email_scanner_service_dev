from aws.sqs_client import get_sqs_client
from utils.logger import get_logger
import json

logger = get_logger(__name__)

def push_to_sqs_queue(work_id: str, queue_url: str) -> bool:
    """
    Push ONLY work_id to SQS queue.
    
    Args:
        work_id: The work_id to send
        queue_url: The SQS queue URL (passed from caller)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info(f"Preparing to push work_id={work_id} to SQS")
        
        if not queue_url:
            logger.error("SQS Queue URL not provided")
            return False
        
        sqs_client = get_sqs_client()
        if not sqs_client:
            logger.error("Failed to get SQS client")
            return False
        
        # MINIMAL PAYLOAD - Only work_id
        message_body = {"work_id": work_id}
        
        logger.debug(f"Message payload: {message_body}")
        logger.debug(f"Sending message to SQS queue: {queue_url}")
        
        response = sqs_client.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message_body)
        )
        
        logger.debug(f"Full SQS response: {response}")
        logger.info(f"✓ SQS: work_id={work_id}, msg_id={response.get('MessageId')}")
        
        return True
        
    except Exception as e:
        logger.error(f"SQS push error for work_id={work_id}: {str(e)}", exc_info=True)
        return False