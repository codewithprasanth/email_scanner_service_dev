
from db.connections import *
from utils.logger import get_logger
from typing import Optional
logger=get_logger(__name__)
def get_last_processed_timestamp_from_db(email_account: str) -> Optional[str]:
    """Get last processed timestamp."""
    conn = None
    logger.info(f"Fetching last processed timestamp for email account: {email_account}")
    try:
        conn = get_guident_db()
        cursor = conn.cursor()
        
        query = """
            SELECT last_processed_timestamp
            FROM email_scanner_state
            WHERE email_account = %s
            ORDER BY last_processed_timestamp DESC
            LIMIT 1
        """
        
        cursor.execute(query, (email_account,))
        result = cursor.fetchone()
        cursor.close()
        logger.debug(f"Query executed. Result fetched: {result}")
        if result and result[0]:
            timestamp = result[0]
            formatted_timestamp = timestamp.strftime("%Y-%m-%dT%H:%M:%SZ") if hasattr(timestamp, 'strftime') else str(timestamp)
            logger.info(f"Last processed timestamp for {email_account}: {formatted_timestamp}")
            return formatted_timestamp
        logger.info(f"No previous timestamp found for {email_account}")
        return None
        
    except Exception as e:
        logger.error(f"Error fetching last processed timestamp for {email_account}: {str(e)}", exc_info=True)
        return None
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed.")