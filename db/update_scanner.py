from db.connections import *
from utils.logger import get_logger
logger=get_logger(__name__)

def update_scanner_state_in_db(scanner_id: str, entity_id: str, email_account: str,
                               last_processed_timestamp: str, last_processed_email_id: str,
                               scan_count: int, status: str) -> bool:
    """Update scanner state."""
    conn = None
    logger.debug(f"Starting update_scanner_state_in_db for scanner_id={scanner_id}, entity_id={entity_id}, email_account={email_account}")
    try:
        conn = get_guident_db()
        cursor = conn.cursor()
        logger.debug("Checking if scanner state already exists in DB...")
        check_query = """
            SELECT scanner_id FROM email_scanner_state
            WHERE scanner_id = %s::uuid AND entity_id = %s::uuid AND email_account = %s
        """
        cursor.execute(check_query, (scanner_id, entity_id, email_account))
        exists = cursor.fetchone()
        
        if exists:
            logger.info(f"Existing scanner state found. Updating scanner state for scanner_id={scanner_id}")
            update_query = """
                UPDATE email_scanner_state
                SET last_processed_timestamp = %s, last_processed_email_id = %s,
                    scan_count = scan_count + %s, last_scan_at = CURRENT_TIMESTAMP,
                    status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE scanner_id = %s::uuid AND entity_id = %s::uuid AND email_account = %s
            """
            cursor.execute(update_query, (
                last_processed_timestamp, last_processed_email_id, scan_count,
                status, scanner_id, entity_id, email_account
            ))
        else:
            logger.info(f"No existing scanner state found. Inserting new record for scanner_id={scanner_id}")
            insert_query = """
                INSERT INTO email_scanner_state
                (scanner_id, entity_id, email_account, last_processed_timestamp,
                 last_processed_email_id, scan_count, last_scan_at, status)
                VALUES (%s::uuid, %s::uuid, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s)
            """
            cursor.execute(insert_query, (
                scanner_id, entity_id, email_account, last_processed_timestamp,
                last_processed_email_id, scan_count, status
            ))
        
        conn.commit()
        cursor.close()
        logger.info(f"✓ Scanner state updated successfully for scanner_id={scanner_id}, status={status}")
        return True
        
    except Exception as e:
        logger.error(f"Scanner state update error for scanner_id={scanner_id}: {str(e)}", exc_info=True)
        if conn:
            conn.rollback()
            logger.debug("Database transaction rolled back due to error")
        return False
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed")