from db.connections import get_guident_db
from utils.logger import get_logger
logger=get_logger(__name__)
def check_email(email_message_id: str) -> bool:
    """
    Check if an email already exists in the database.
    
    Args:
        email_message_id (str): Graph email message ID.
        
    Returns:
        bool: True if email exists, False otherwise.
    """
    conn = None
    try:
        logger.debug(f"Checking existence of email_message_id: {email_message_id[:50]}...")
        conn = get_guident_db()
        if not conn:
            logger.error("Database connection not available. Cannot check email.")
            return False
        cursor = conn.cursor()
        
        query = "SELECT EXISTS(SELECT 1 FROM invoice_emails WHERE email_message_id = %s)"
        cursor.execute(query, (email_message_id[:255],))
        result = cursor.fetchone()
        exists = result[0] if result else False
        
        if exists:
            logger.info(f"Email already exists in DB: {email_message_id[:50]}...")
        else:
            logger.info(f"Email does not exist in DB, can process: {email_message_id[:50]}...")
        cursor.close()
        return exists
        
    except Exception as e:
        logger.error(f"Error checking email in DB: {str(e)}", exc_info=True)
        return False
    finally:
        if conn:
            try:
                conn.close()
                logger.debug("Database connection closed successfully")
            except Exception as e:
                logger.warning(f"Error closing DB connection: {str(e)}", exc_info=True)
