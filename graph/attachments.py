import base64
from aws.push_s3 import upload_attachment_to_s3
from db.insert_document import insert_document_to_database
from config.settings import GRAPH_API_ENDPOINT
from utils.logger import get_logger

logger = get_logger(__name__)


def process_attachments(session, user_email, folder_id, email_id, work_id, attachments=None):
    """
    Process and upload attachments for an email.
    
    Args:
        session: Graph API session
        user_email: Email account
        folder_id: Mail folder ID
        email_id: Email message ID
        work_id: Work ID from database
        attachments: Ignored - always fetches from API
    
    Returns:
        int: Number of successfully uploaded attachments
    """
    uploaded_count = 0
    
    # ✅ ALWAYS fetch attachments from Graph API
    # The initial message list doesn't include full attachment data
    logger.debug(
        f"Fetching attachments from Graph API | "
        f"email_id={email_id[:30]}..., work_id={work_id}"
    )
    
    try:
        # Fetch attachment details from Graph API
        att_url = f"{GRAPH_API_ENDPOINT}/users/{user_email}/mailFolders/{folder_id}/messages/{email_id}/attachments"
        logger.debug(f"Attachment API URL: {att_url}")
        
        att_response = session.get(att_url)
        att_response.raise_for_status()
        
        attachment_values = att_response.json().get("value", [])
        
        if not attachment_values:
            logger.info(f"No attachments found via API | email_id={email_id[:30]}...")
            return uploaded_count
        
        logger.info(
            f"Fetched {len(attachment_values)} attachment(s) from Graph API | "
            f"email_id={email_id[:30]}..., work_id={work_id}"
        )
        
        for idx, attachment in enumerate(attachment_values, 1):
            att_name = attachment.get("name", "<unnamed>")
            att_type = attachment.get("contentType", "<unknown>")
            att_size = attachment.get("size", 0)
            
            logger.debug(
                f"Processing attachment {idx}/{len(attachment_values)} | "
                f"name='{att_name}', size={att_size}, type={att_type}"
            )
            
            # Skip inline attachments (embedded images, etc.)
            if attachment.get("isInline"):
                logger.debug(f"⏭ Skipping inline attachment: {att_name}")
                continue
            
            # Check for content bytes
            content_bytes = attachment.get("contentBytes")
            if not content_bytes:
                logger.warning(
                    f"⚠ No content bytes for attachment: {att_name} | "
                    f"email_id={email_id[:30]}..."
                )
                continue
            
            try:
                # Decode and upload to S3
                logger.debug(f"Decoding and uploading: {att_name}")
                att_data = base64.b64decode(content_bytes)
                
                s3_url = upload_attachment_to_s3(
                    att_data,
                    attachment.get("name"),
                    email_id,
                    attachment.get("contentType")
                )
                
                if not s3_url:
                    logger.error(f"✗ S3 upload failed: {att_name}")
                    continue
                
                logger.debug(f"✓ S3 uploaded: {att_name} → {s3_url}")
                
                # Insert into database
                doc_id = insert_document_to_database(
                    work_id,
                    attachment.get("name"),
                    attachment.get("size"),
                    attachment.get("contentType"),
                    s3_url
                )
                
                if doc_id:
                    uploaded_count += 1
                    logger.info(
                        f"✓ Attachment stored | "
                        f"doc_id={doc_id}, name='{att_name}', "
                        f"size={att_size}, work_id={work_id}"
                    )
                else:
                    logger.error(
                        f"✗ DB insert failed for attachment: {att_name} | "
                        f"work_id={work_id}"
                    )
            
            except Exception as e:
                logger.error(
                    f"✗ Failed to process attachment: {att_name} | "
                    f"Error: {str(e)}",
                    exc_info=True
                )
                continue
        
        logger.info(
            f"✓ Attachment processing complete | "
            f"work_id={work_id}, uploaded={uploaded_count}/{len(attachment_values)}"
        )
    
    except Exception as e:
        logger.error(
            f"✗ Attachment processing error | "
            f"email_id={email_id[:30]}..., work_id={work_id} | "
            f"Error: {str(e)}",
            exc_info=True
        )
    
    return uploaded_count