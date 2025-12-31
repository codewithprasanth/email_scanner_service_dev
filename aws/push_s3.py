from aws.s3_client import get_s3_client
from utils.logger import get_logger
from typing import Optional
import uuid
from config.settings import S3_BUCKET_NAME  ,AWS_ENDPOINT_URL
logger = get_logger(__name__)



def upload_attachment_to_s3(attachment_data: bytes, file_name: str,
                            email_id: str, content_type: str = None) -> Optional[str]:
    """Upload attachment to S3."""
    try:
        logger.info(f"Starting S3 upload for email_id={email_id}, file={file_name}")
        s3_client = get_s3_client()
        
        file_uuid = str(uuid.uuid4())
        s3_key = f"emails/{email_id}/attachments/{file_uuid}_{file_name}"
        logger.debug(f"S3 key generated: {s3_key}")
        upload_params = {
            'Bucket': S3_BUCKET_NAME,
            'Key': s3_key,
            'Body': attachment_data
        }
        
        if content_type:
            upload_params['ContentType'] = content_type
            logger.debug(f"Content-Type set: {content_type}")
        logger.info(f"Uploading file to S3 bucket={S3_BUCKET_NAME} at key={s3_key}...")
        s3_client.put_object(**upload_params)
        s3_url = f"{AWS_ENDPOINT_URL}/{S3_BUCKET_NAME}/{s3_key}"
        logger.info(f"Upload complete for file={file_name}")
        
        logger.debug(f"S3 uploaded: {file_name}")
        return s3_url
        
    except Exception as e:
        logger.error(f"S3 upload error: {str(e)}")
        return None
