from utils.logger import get_logger 
from typing import Any,Dict,Optional
from db.connections import get_guident_db
from utils.generate_work_id import generate_work_id
logger= get_logger(__name__)
def insert_email_to_database(email_data: Dict[str, Any], entity_id: str) -> Optional[str]:
    """Insert email and return work_id."""
    conn = None
    logger.debug(f"Starting insert_email_to_database for entity_id={entity_id}")

    try:
        conn = get_guident_db()
        cursor = conn.cursor()
        
        cc_emails = []
        if email_data.get("graph_message", {}).get("ccRecipients"):
            cc_emails = [cc.get("emailAddress", {}).get("address", "") 
                        for cc in email_data["graph_message"]["ccRecipients"]]
        
        work_id = generate_work_id()
        logger.debug(
            f"Inserting email: id={email_data.get('id', '')[:30]}, "
            f"subject='{email_data.get('subject', '')[:50]}', "
            f"from={email_data.get('sender_email', '')}, "
            f"to={(email_data.get('recipient_mailbox', [''])[0])}, "
            f"has_attachments={email_data.get('has_attachments', False)}"
        )        
        insert_query = """
            INSERT INTO invoice_emails
            (email_message_id, email_thread_id, subject, received_from_email,
             received_from_name, received_to_email, cc_emails, body_text, body_html,
             sent_at, received_at, processing_status, has_attachments,
             attachment_count, work_id, entity_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::uuid)
        """
        
        cursor.execute(insert_query, (
            email_data.get("id", ""),
            email_data.get("conversation_id", "")[:255],
            email_data.get("subject", "")[:500] if email_data.get("subject") else "",
            email_data.get("sender_email", "")[:255],
            email_data.get("sender", "")[:255],
            (email_data.get("recipient_mailbox", [""])[0])[:255] if email_data.get("recipient_mailbox") else "",
            cc_emails,
            email_data.get("body", ""),
            email_data.get("body", ""),
            email_data.get("received_time"),
            email_data.get("received_time"),
            "RECEIVED",
            email_data.get("has_attachments", False),
            email_data.get("attachment_count", 0),
            work_id,
            entity_id
        ))
        
        conn.commit()
        cursor.close()
        logger.info(f"Email stored successfully: work_id={work_id}")
        
        return work_id
        
    except Exception as e:
        logger.error(f"Email insert error for work_id={work_id}: {str(e)}", exc_info=True)
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed")

